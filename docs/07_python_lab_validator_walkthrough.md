# Python 5G Lab Validator: Complete Code Walkthrough

## Purpose

This guide explains the Phase 10 validator from top to bottom:

- what problem the program solves;
- how its Python design works;
- what every major class and function does;
- how each software check maps to a 5G or Linux concept;
- how failures are converted into useful results;
- how the Markdown report is produced;
- how the automated tests prove the logic.

Open these files side by side:

1. [`tools/lab_check.py`](../tools/lab_check.py) — the implementation;
2. this walkthrough — the explanation;
3. [`tests/test_lab_check.py`](../tests/test_lab_check.py) — controlled proof of
   the implementation;
4. [`reports/latest_lab_check.md`](../reports/latest_lab_check.md) — a real
   successful output.

Read this guide in order the first time. On later readings, use the function
index to jump directly to a topic.

## 1. The Program In One Sentence

The validator is a read-only Python command-line program that gathers evidence
from Linux, Open5GS, UERANSIM, and the UE data path, converts each observation
into a structured PASS or FAIL result, and writes a Markdown report whose first
failure suggests the next diagnostic action.

## 2. The Main Mental Model

The program checks dependencies in this order:

```text
required programs exist
        |
        v
MongoDB and Open5GS services are active
        |
        v
expected protocol endpoints are listening
        |
        v
gNB establishes SCTP and completes NG Setup
        |
        v
UE authenticates and registers
        |
        v
UE establishes a PDU session
        |
        v
Linux creates the UE tunnel and route
        |
        v
traffic succeeds from inside the UE namespace
```

This ordering is the core design decision. Later checks depend on earlier
checks, so the first failure is usually the most useful place to investigate.

## 3. What The Tool Does Not Do

The validator does not:

- install software;
- start or stop Open5GS;
- start or stop UERANSIM;
- edit a configuration;
- change subscriber data;
- add or remove routes;
- change firewall or Network Address Translation (NAT) rules;
- create or delete network namespaces.

It observes the current state. This makes it a validator rather than a
deployment or repair tool.

## 4. Inputs And Outputs

The complete live command is:

```bash
python3 tools/lab_check.py \
  --gnb-log /tmp/5g-lab-gnb.log \
  --ue-log /tmp/5g-lab-ue.log \
  --namespace ueransim-999700000000001-internet-psi1 \
  --target 8.8.8.8 \
  --output reports/latest_lab_check.md
```

Inputs:

- command-line options;
- current Linux service and socket state;
- a current UERANSIM gNB log;
- a current UERANSIM UE log;
- a live UE network namespace;
- the result of a short ping from that namespace.

Output:

- one Markdown report;
- terminal summary;
- process exit code `0`, `1`, or `2`.

## 5. Function Index

| Source section | Responsibility |
| --- | --- |
| [`CommandResult`](../tools/lab_check.py#L44) | Stores one external command result |
| [`CheckResult`](../tools/lab_check.py#L55) | Stores one lab decision |
| [`CommandRunner`](../tools/lab_check.py#L65) | Executes commands safely |
| [`discover_binary`](../tools/lab_check.py#L109) | Locates required executables |
| [`check_required_commands`](../tools/lab_check.py#L129) | Validates software prerequisites |
| [`check_core_services`](../tools/lab_check.py#L156) | Validates MongoDB/Open5GS units |
| [`check_expected_ports`](../tools/lab_check.py#L184) | Validates protocol endpoints |
| [`read_log`](../tools/lab_check.py#L224) | Reads one supplied log safely |
| [`parse_gnb_log`](../tools/lab_check.py#L246) | Separates SCTP from NG Setup |
| [`parse_ue_log`](../tools/lab_check.py#L281) | Separates registration from PDU session |
| [`discover_namespace`](../tools/lab_check.py#L346) | Resolves a live UE namespace |
| [`check_ue_tunnel`](../tools/lab_check.py#L387) | Validates `uesimtun0` and its route |
| [`check_connectivity`](../tools/lab_check.py#L432) | Tests the complete UE data path |
| [`collect_environment`](../tools/lab_check.py#L474) | Collects concise version context |
| [`overall_status`](../tools/lab_check.py#L494) | Calculates the final PASS or FAIL |
| [`suggested_next_action`](../tools/lab_check.py#L500) | Selects the first useful action |
| [`render_report`](../tools/lab_check.py#L509) | Builds Markdown text |
| [`write_report`](../tools/lab_check.py#L559) | Writes the report file |
| [`run_checks`](../tools/lab_check.py#L566) | Orchestrates checks in dependency order |
| [`build_parser`](../tools/lab_check.py#L617) | Defines the command-line interface |
| helper functions | Extract, sanitize, and format evidence |
| [`main`](../tools/lab_check.py#L702) | Connects the complete program |

## 6. Header, Imports, And Type Annotations

See [`tools/lab_check.py` lines 1-16](../tools/lab_check.py#L1).

```python
#!/usr/bin/env python3
```

The shebang lets Linux run the executable file with Python 3.

```python
from __future__ import annotations
```

This makes type annotations easier to evaluate and allows modern type syntax
without eagerly resolving every referenced type.

Important imports:

| Module | Why it is used |
| --- | --- |
| `argparse` | Parses command-line options |
| `os` | Checks executable permission and environment variables |
| `platform` | Reads kernel and Python information |
| `re` | Matches ports and the UE IPv4 address |
| `shutil` | Searches the shell `PATH` |
| `subprocess` | Runs Linux commands |
| `sys` | Returns the program exit code |
| `dataclasses` | Defines structured result objects |
| `datetime` | Adds report generation time |
| `pathlib` | Handles paths safely |
| `typing` | Describes expected argument types |

Type annotations such as:

```python
def overall_status(checks: Sequence[CheckResult]) -> str:
```

mean that `checks` should be an ordered sequence of `CheckResult` objects and
the function returns a string. Python does not enforce this at runtime, but the
annotations improve readability and support static analysis.

## 7. Constants: The Lab Contract

See [`tools/lab_check.py` lines 19-41](../tools/lab_check.py#L19).

`PASS` and `FAIL` prevent repeated string literals throughout the code.

`REQUIRED_COMMANDS` defines the executable contract:

- `ip` for Linux interfaces, routes, and namespaces;
- `ping` for connectivity;
- `tcpdump` and `tshark` for packet work;
- `nr-gnb` and `nr-ue` for UERANSIM.

`CORE_SERVICES` defines the service contract. It includes MongoDB plus the
required Open5GS network functions.

`EXPECTED_PORTS` maps a port to its technical purpose:

| Port | Meaning |
| ---: | --- |
| `38412/SCTP` | N2 transport between gNB and AMF |
| `8805/UDP` | N4 Packet Forwarding Control Protocol |
| `2152/UDP` | N3 GPRS Tunnelling Protocol User Plane |
| `7777/TCP` | Open5GS Service-Based Interface |
| `27017/TCP` | MongoDB |

These constants make the expected lab state visible near the beginning of the
file instead of hiding it inside several functions.

## 8. Two Result Types

See [`tools/lab_check.py` lines 44-62](../tools/lab_check.py#L44).

### `CommandResult`

`CommandResult` records facts about an operating-system command:

```text
argv       exact argument list
returncode numeric exit code
stdout     normal output
stderr     error output
error      Python-level execution problem
```

An exit code of `0` normally means success. Other values have command-specific
meaning.

### `CheckResult`

`CheckResult` records an interpreted lab decision:

```text
name       report row name
status     PASS or FAIL
evidence   concise reason
action     recommended response if failed
```

This separation is important:

```text
CommandResult = what Linux returned
CheckResult   = what that result means for the 5G lab
```

Both dataclasses are `frozen=True`, so their values cannot be changed after
creation. A result therefore behaves like an immutable observation.

## 9. Safe Command Execution

See [`CommandRunner`](../tools/lab_check.py#L65).

The runner converts every argument to a string and calls:

```python
subprocess.run(
    command,
    capture_output=True,
    check=False,
    text=True,
    timeout=...,
)
```

Meaning:

- `capture_output=True` stores standard output and standard error;
- `check=False` prevents a nonzero command exit from raising an exception;
- `text=True` returns strings rather than bytes;
- `timeout` prevents a stuck command from blocking forever.

The program does not use `shell=True`. Therefore, arguments are passed
directly to the executable rather than being reinterpreted by a shell. This
reduces quoting errors and command-injection risk.

The exception branches normalize unusual failures:

| Situation | Stored return code |
| --- | ---: |
| executable missing | `127` |
| timeout | `124` |
| other operating-system error | `126` |

The rest of the program can process these values like any other command result
instead of crashing.

## 10. Required-Program Discovery

See [`discover_binary`](../tools/lab_check.py#L109) and
[`check_required_commands`](../tools/lab_check.py#L129).

`shutil.which(name)` searches the shell `PATH`.

UERANSIM binaries may not be in `PATH`, so the function has a second strategy:

```text
<UERANSIM root>/build/nr-gnb
<UERANSIM root>/build/nr-ue
```

It confirms that the candidate is a file and is executable.

`check_required_commands` loops through the required names and creates two
lists:

- `found`;
- `missing`.

If any item is missing, the whole prerequisite check fails and lists both what
was found and what was absent.

Dependency injection appears in:

```python
which: Callable[[str], str | None] = shutil.which
```

Normal execution uses `shutil.which`. Tests can provide a fake function,
allowing missing-command behavior to be tested without uninstalling anything.

## 11. Core-Service Validation

See [`check_core_services`](../tools/lab_check.py#L156).

For every service, Python runs:

```text
systemctl is-active <service>
```

The service passes only when:

```text
return code == 0
and output == "active"
```

Why both? A program should not trust output text alone when the command also
provides a formal exit status.

The result groups all inactive services into one report row. This avoids a
large table while still identifying every missing dependency.

An active service proves that its process is running. It does not prove that a
protocol procedure completed, which is why later checks still inspect ports
and logs.

## 12. Protocol-Endpoint Validation

See [`check_expected_ports`](../tools/lab_check.py#L184).

The tool runs two socket queries:

```text
ss -H -lntup
ss -H -ln --sctp
```

The first shows listening TCP and UDP sockets. The second is necessary because
SCTP is not included in the normal TCP/UDP view.

The two outputs are joined and searched with a regular expression:

```python
rf":{port}(?:\s|$)"
```

This means:

- find a colon followed by the exact port;
- require whitespace or end-of-line afterward;
- avoid treating a partial number as the requested port.

This check proves that protocol endpoints exist. It does not prove that a peer
completed a procedure. For example:

```text
AMF listens on SCTP 38412 = ready for N2
NG Setup success          = gNB was accepted on N2
```

## 13. Reading Logs Safely

See [`read_log`](../tools/lab_check.py#L224).

The tool requires explicit paths to current logs. It does not search every log
in the repository because it could accidentally parse an old failure scenario.

Possible outcomes:

- no path: return a FAIL result;
- unreadable path: return a FAIL result with the file error;
- readable path: return the text.

`errors="replace"` means an unusual byte is replaced rather than causing the
entire validation to crash.

The full log is never copied into the Markdown report. Only selected evidence
is reported.

## 14. gNB Log Interpretation

See [`parse_gnb_log`](../tools/lab_check.py#L246).

The parser first checks explicit failure:

```text
NG Setup procedure is failed
```

If found, it extracts that line so a standardized cause can appear as evidence.

For success it requires both:

```text
SCTP connection established
NG Setup procedure is successful
```

This is based on the Phase 9 PLMN and TAC results. SCTP could succeed while NG
Setup failed, so transport reachability alone is insufficient.

Protocol meaning:

- Stream Control Transmission Protocol (SCTP) provides the N2 transport;
- NG Application Protocol (NGAP) NG Setup allows the Access and Mobility
  Management Function (AMF) to accept the gNB configuration.

## 15. UE Log Interpretation

See [`parse_ue_log`](../tools/lab_check.py#L281).

The function deliberately returns two results:

1. UE registration;
2. PDU session.

This reflects 5G architecture. Registration gives the UE mobility-management
service. A Protocol Data Unit (PDU) session separately gives it a data-network
connection.

Success markers:

```text
Initial Registration is successful
PDU Session establishment is successful
```

Known authentication and registration failure markers include:

```text
MAC_FAILURE
Authentication Reject received
Registration reject received
PLMN selection failure
no cells in coverage
```

Known session failure markers include:

```text
DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED
PDU Session Establishment Reject
PDU Session establishment failure
```

The wrong-DNN behavior is correctly represented:

```text
registration result = PASS
PDU-session result  = FAIL
```

That is more accurate than assigning one status to the entire UE log.

## 16. Network-Namespace Discovery

See [`discover_namespace`](../tools/lab_check.py#L346).

A namespace is an isolated Linux network stack with its own interfaces and
routes. UERANSIM places `uesimtun0` inside a PDU-session namespace so the
simulated UE behaves like a separate device.

If `--namespace` is supplied, the tool uses it.

Otherwise, it runs:

```text
ip netns list
```

It keeps names that:

- start with `ueransim-`;
- contain `-psi`.

Outcomes:

| Matches | Result |
| ---: | --- |
| one | use it |
| zero | fail because no live session namespace exists |
| multiple | fail and require an explicit `--namespace` |

Choosing one of several namespaces automatically could validate the wrong UE,
so ambiguity is treated as a failure.

## 17. Tunnel And Route Validation

See [`check_ue_tunnel`](../tools/lab_check.py#L387).

The function runs two commands inside the namespace:

```text
ip -brief address show uesimtun0
ip route
```

They are prefixed with:

```text
sudo -n ip netns exec <namespace>
```

`sudo -n` never prompts. It fails immediately if authorization is unavailable.
The operator runs `sudo -v` before validation, but the Python program itself is
not launched as root.

The tunnel passes only when:

- `uesimtun0` exists;
- it has a `10.45.x.x` address;
- the namespace has `default dev uesimtun0`.

The report extracts only the lab IPv4 prefix and omits the transient IPv6
link-local address.

Why check the route too? An interface with an address can exist while traffic
still follows no usable default path.

## 18. End-To-End Connectivity

See [`check_connectivity`](../tools/lab_check.py#L432).

The ping runs inside the UE namespace:

```text
sudo -n ip netns exec <namespace> ping -c 3 -W 2 8.8.8.8
```

An ordinary host ping would validate only Ubuntu connectivity. The namespace
ping validates:

```text
UE namespace
 -> uesimtun0
 -> UERANSIM UE/gNB path
 -> N3 GTP-U
 -> UPF
 -> N6/Linux forwarding
 -> NAT
 -> external destination
 -> complete return path
```

The function requires:

- ping return code `0`;
- output containing `0% packet loss`.

It extracts only the packet-summary line for the report.

The timeout grows with the number of requested packets:

```python
max(8.0, ping_count * 3.0)
```

This gives the command enough time while still preventing an indefinite wait.

## 19. Environment And Path Privacy

See [`collect_environment`](../tools/lab_check.py#L474) and
[`display_path`](../tools/lab_check.py#L691).

The environment section includes only:

- operating-system name;
- kernel;
- Python version;
- Open5GS management type;
- UERANSIM root.

`display_path` converts a path under the current home directory:

```text
/home/<local-account>/UERANSIM
```

into:

```text
~/UERANSIM
```

This keeps the technical location understandable without recording the local
account name.

## 20. Overall Status And First Failure

See [`overall_status`](../tools/lab_check.py#L494) and
[`suggested_next_action`](../tools/lab_check.py#L500).

Overall status is PASS only when:

- the list is not empty;
- every required check is PASS.

The suggested action loops through the ordered results and returns the first
failure's action.

Example:

```text
commands PASS
services PASS
ports PASS
gNB FAIL
UE FAIL
connectivity FAIL
```

The suggestion points to the gNB, not connectivity. Fixing the earlier
dependency may resolve every later symptom.

## 21. Markdown Report Generation

See [`render_report`](../tools/lab_check.py#L509) and
[`write_report`](../tools/lab_check.py#L559).

The renderer builds a list of lines containing:

1. title and timestamp;
2. overall result;
3. environment;
4. check table;
5. suggested next action.

It accepts an optional `generated` datetime. Normal execution uses the current
time. Tests inject a fixed time so expected output is deterministic.

`_md_cell` removes newlines and escapes `|` so command evidence cannot break a
Markdown table.

`write_report` creates missing parent directories and writes UTF-8 text.

## 22. Orchestration In Dependency Order

See [`run_checks`](../tools/lab_check.py#L566).

This is the main coordinator. It appends results in this order:

1. required commands;
2. core services;
3. expected ports;
4. gNB connection;
5. UE registration;
6. PDU session;
7. UE tunnel;
8. UE connectivity.

The function uses explicit failure results when evidence is unavailable. For
example, no UE log creates both:

- UE registration FAIL;
- PDU session FAIL.

No namespace similarly creates:

- UE tunnel FAIL;
- UE connectivity FAIL.

The report therefore remains structurally complete even when the lab is not
running.

## 23. Command-Line Interface

See [`build_parser`](../tools/lab_check.py#L617).

`argparse` defines:

| Option | Type | Default |
| --- | --- | --- |
| `--output` | path | `reports/latest_lab_check.md` |
| `--gnb-log` | path | none |
| `--ue-log` | path | none |
| `--namespace` | string | auto-detect |
| `--target` | string | `8.8.8.8` |
| `--ping-count` | integer | `3` |
| `--command-timeout` | float | `5.0` seconds |
| `--ueransim-root` | path | environment value or `~/UERANSIM` |

The `UERANSIM_ROOT` environment variable supports a non-default installation
without editing the source code.

## 24. Small Helper Functions

See [`tools/lab_check.py` lines 666-699](../tools/lab_check.py#L666).

- `_matching_line` returns the full log line containing a marker.
- `_first_marker` returns the first known failure marker found.
- `_ping_summary` extracts the transmitted/received/loss line.
- `_md_cell` makes evidence safe for a Markdown table.
- `display_path` removes the local home-directory prefix.

The leading underscore means a function is an internal implementation detail,
not part of the main external interface.

## 25. Program Entry Point

See [`main`](../tools/lab_check.py#L702).

Execution flow:

```text
determine repository root
 -> build argument parser
 -> parse arguments
 -> validate numeric arguments
 -> create CommandRunner
 -> run all checks
 -> collect environment
 -> render report
 -> write report
 -> print terminal summary
 -> return exit code
```

Invalid numeric arguments call `parser.error`, which produces command-line
usage information and exit code `2`.

Normal outcomes:

```text
all checks pass          -> exit 0
one or more checks fail  -> exit 1
invalid command usage    -> exit 2
```

The final block:

```python
if __name__ == "__main__":
    sys.exit(main())
```

means:

- when executed directly, run `main` and return its code to Linux;
- when imported by tests, do not run the live validator automatically.

## 26. One Complete Successful Execution

The actual Phase 10 run followed this logic:

1. `ip`, `ping`, `tcpdump`, and `tshark` were found in `PATH`.
2. `nr-gnb` and `nr-ue` were found under `~/UERANSIM/build`.
3. MongoDB and all required Open5GS units were active.
4. the expected N2, N3, N4, SBI, and database ports were present.
5. the gNB log proved SCTP and NG Setup.
6. the UE log proved authentication, NAS security, and registration.
7. the UE log separately proved PDU-session establishment.
8. `uesimtun0` had `10.45.0.6/24`.
9. the UE namespace default route used `uesimtun0`.
10. three pings from the UE namespace received three replies.
11. every `CheckResult` was PASS.
12. `overall_status` returned PASS.
13. the Markdown report was written.
14. the process returned exit code `0`.

See the result in
[`reports/latest_lab_check.md`](../reports/latest_lab_check.md).

## 27. How The Tests Work

See [`tests/test_lab_check.py`](../tests/test_lab_check.py).

The tests use Python's built-in:

- `unittest`;
- `unittest.mock`;
- temporary directories.

No live core, UE, root permission, or internet is required.

### `FakeRunner`

`FakeRunner` records each requested command and returns controlled
`CommandResult` objects. This tests interpretation logic without executing
Linux commands.

### Binary tests

These prove:

- UERANSIM can be found outside `PATH`;
- a missing command becomes FAIL;
- home paths are sanitized.

### Log-parser tests

These prove:

- SCTP plus NG Setup produces gNB PASS;
- NG Setup Failure produces gNB FAIL;
- registration and PDU session are separate;
- MAC failure is detected;
- wrong DNN keeps registration PASS but session FAIL.

### Namespace and connectivity tests

These prove:

- exactly one namespace is auto-detected;
- tunnel address and default route are both required;
- zero packet loss passes;
- complete packet loss fails with user-plane guidance.

### Socket test

This proved TCP/UDP and SCTP output must be combined. The host smoke test first
revealed that ordinary `ss -lntup` does not include SCTP, and the automated test
now prevents that defect from returning.

### Report tests

These prove:

- fixed input produces deterministic Markdown;
- nested report paths are created;
- the first failure controls the suggested action.

### Timeout test

`unittest.mock.patch` makes `subprocess.run` raise `TimeoutExpired`. The test
confirms the runner returns code `124` rather than crashing.

Run all tests with:

```bash
python3 -m unittest discover -s tests -v
```

## 28. Important Design Principles

### Separate observation from interpretation

`CommandResult` stores raw command outcome. `CheckResult` stores lab meaning.

### Separate 5G stages

The code does not confuse:

- process active with protocol ready;
- SCTP connected with NG Setup accepted;
- UE registered with PDU session established;
- PDU session established with external connectivity.

### Fail clearly

Missing logs, permissions, binaries, namespaces, routes, or packets create
useful FAIL results rather than uncaught exceptions.

### Keep privilege narrow

Only namespace commands use `sudo -n`. Python itself runs as the normal user.

### Keep evidence concise

The report records decisions and short evidence, not raw logs or secrets.

### Make logic testable

Command execution is wrapped and replaceable. Parsers accept plain strings.
The report renderer accepts a fixed clock.

## 29. Limitations

The validator is intentionally scoped to this single-host lab.

- It recognizes the lab UE subnet prefix `10.45`.
- It checks known local Open5GS services and ports.
- It parses UERANSIM's current console wording.
- It validates ICMP connectivity, not application throughput.
- It reports current state; it does not provide continuous monitoring.
- A process can fail immediately after a successful point-in-time report.

Possible future extensions:

- load expected values from a configuration file;
- support multiple UEs and namespaces;
- add JSON output;
- inspect packet-capture landmarks automatically;
- add latency and packet-loss thresholds;
- add continuous or scheduled health checks.

## 30. A Clear Technical Summary

A concise explanation of the implementation is:

> I built a standard-library Python validator for a local 5G Standalone lab.
> It runs read-only Linux checks through a timeout-controlled subprocess
> wrapper, then converts raw command and log evidence into immutable PASS/FAIL
> results. The checks follow the real dependency chain: required tools,
> MongoDB and Open5GS services, N2/N3/N4 endpoints, gNB SCTP and NG Setup, UE
> registration, PDU-session establishment, the namespace tunnel and route, and
> finally ping from inside the UE namespace. Registration and session state are
> deliberately separate because one can succeed while the other fails. The
> first failed dependency determines the suggested action. A Markdown renderer
> produces concise sanitized evidence, and 17 unit tests use fake command
> results to verify success, known failure modes, timeouts, and report output
> without requiring a live core.

## 31. Knowledge Check

After reading, you should be able to answer:

1. Why are `CommandResult` and `CheckResult` separate?
2. Why does the program avoid `shell=True`?
3. Why are there two `ss` commands?
4. Why is SCTP success not enough to pass the gNB check?
5. Why does `parse_ue_log` return two results?
6. Why must ping run inside the UE namespace?
7. What does `sudo -n` protect against?
8. Why are checks stored in dependency order?
9. How is the first suggested action selected?
10. Why can the tests run without Open5GS or UERANSIM?
11. What does exit code `1` mean compared with exit code `2`?
12. What evidence proves the complete user plane rather than host connectivity?

If any answer is unclear, return to the matching numbered section and inspect
the linked function beside it.

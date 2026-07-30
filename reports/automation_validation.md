# Automation Validation Report

## Status

Complete. The Python validator, automated tests, operator documentation, and
live end-to-end PASS report have been verified.

## Implemented Tool

[`tools/lab_check.py`](../tools/lab_check.py) is a read-only, standard-library
Python command-line tool. It checks the lab in dependency order:

```text
required commands
  -> MongoDB/Open5GS services
  -> listening protocol endpoints
  -> gNB SCTP and NG Setup
  -> UE authentication and registration
  -> PDU-session establishment
  -> UE namespace, tunnel address, and default route
  -> connectivity from inside the UE namespace
```

The tool:

- uses argument-list subprocess calls without `shell=True`;
- applies timeouts;
- converts command errors into structured results;
- uses `sudo -n` only for namespace inspection and UE ping;
- does not start, stop, install, or reconfigure the lab;
- generates concise Markdown evidence;
- returns exit code `0` for PASS and `1` for a completed validation with one
  or more failed checks.

## Live Validation

The successful point-in-time report is:

[`reports/latest_lab_check.md`](latest_lab_check.md)

It confirmed:

- all six required commands;
- all ten required MongoDB/Open5GS services;
- N2 SCTP, N4 PFCP, N3 GTP-U, SBI, and MongoDB endpoints;
- SCTP association and NG Setup;
- UE authentication, NAS security, and registration;
- PDU-session establishment;
- `uesimtun0` address `10.45.0.6/24` and its default route;
- three of three Echo Replies from a test executed inside the UE namespace.

Overall live status: **PASS**

## Automated Tests

Run:

```bash
python3 -m unittest discover -s tests -v
```

Result:

```text
Ran 17 tests
OK
```

The tests cover binary discovery, missing commands, combined TCP/UDP/SCTP
endpoint inspection, protocol-aware log parsing, namespace discovery, tunnel
and route validation, connectivity success and failure, report output,
suggested actions, path sanitization, and command timeouts.

## Privacy And Evidence Review

- UERANSIM home paths are rendered with `~` rather than a local account name.
- The tunnel result includes only the required lab IPv4 address.
- Raw gNB and UE logs remain in `/tmp` and are not committed.
- Authentication keys and OP/OPc values are not copied into the report.
- Evidence is summarized rather than reproduced as large command output.

## Completion Gate

- Python tool runs: PASS
- Markdown report generation: PASS
- Missing-command handling: PASS
- Successful and failed log parsing: PASS
- Live tunnel and connectivity checks: PASS
- At least four automated tests: PASS (`17`)
- README usage instructions: PASS
- Live overall report: PASS

The automation deliverable is complete and integrated with the repository
documentation, successful live evidence, and unit-test suite.

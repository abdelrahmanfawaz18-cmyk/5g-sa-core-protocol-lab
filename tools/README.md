# Validation Tools

## 5G SA Lab Check

[`lab_check.py`](lab_check.py) performs read-only checks across the complete
lab dependency chain:

```text
commands
  -> MongoDB/Open5GS services
  -> listening protocol endpoints
  -> gNB SCTP and NG Setup
  -> UE registration
  -> PDU-session establishment
  -> UE namespace, tunnel, and route
  -> connectivity through the UE data path
```

It does not start, stop, install, or reconfigure any service. It does not
change routes, firewall rules, namespaces, or subscriber data.

For a top-to-bottom explanation of the Python, Linux checks, 5G meaning,
execution flow, and automated tests, read the
[complete code walkthrough](../docs/07_python_lab_validator_walkthrough.md).

## Basic Command

From the repository root:

```bash
python3 tools/lab_check.py --output reports/latest_lab_check.md
```

The basic command always generates a report. Live checks fail clearly when a
current gNB log, UE log, or UE namespace is unavailable.

## Complete Live Check

Run the baseline gNB and save its current console output:

```bash
./scripts/run/start_gnb.sh 2>&1 | tee /tmp/5g-lab-gnb.log
```

Run the baseline UE in another terminal and save its current output:

```bash
./scripts/run/start_ue.sh 2>&1 | tee /tmp/5g-lab-ue.log
```

After registration and PDU-session establishment succeed, open a third
terminal and authorize only the later namespace commands:

```bash
sudo -v
```

Then run:

```bash
python3 tools/lab_check.py \
  --gnb-log /tmp/5g-lab-gnb.log \
  --ue-log /tmp/5g-lab-ue.log \
  --namespace ueransim-999700000000001-internet-psi1 \
  --target 8.8.8.8 \
  --output reports/latest_lab_check.md
```

The tool invokes namespace inspection and ping through `sudo -n`. This flag
never prompts for a password; it fails immediately if `sudo -v` was not run
or its authorization expired. The Python process itself is not run as root.

## Options

| Option | Purpose |
| --- | --- |
| `--output PATH` | Markdown report destination |
| `--gnb-log PATH` | Current UERANSIM gNB console log |
| `--ue-log PATH` | Current UERANSIM UE console log |
| `--namespace NAME` | Intended live PDU-session namespace |
| `--target IP` | UE connectivity target; default `8.8.8.8` |
| `--ping-count N` | Number of Echo Requests; default `3` |
| `--command-timeout S` | Default subprocess timeout |
| `--ueransim-root PATH` | UERANSIM source/build root |

If `--namespace` is omitted, the tool accepts exactly one namespace whose name
starts with `ueransim-` and contains `-psi`.

## Exit Codes

| Code | Meaning |
| ---: | --- |
| `0` | Every required check passed |
| `1` | The tool ran, but at least one lab check failed |
| `2` | Command-line usage was invalid |

## Report Safety

The report contains concise decisions and evidence rather than raw logs. It
does not copy authentication keys, OP/OPc values, or full command output.

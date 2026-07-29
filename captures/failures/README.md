# Controlled Failure Evidence

This directory contains one subdirectory for each controlled failure
experiment.

| Scenario | Current state |
| --- | --- |
| `wrong_plmn` | Complete |
| `wrong_tac` | Complete |
| `wrong_subscriber_key` | Complete |
| `wrong_dnn` | Complete |
| `missing_nat` | Complete |

Raw packet captures and console logs are ignored by Git. They must remain
local until they have been reduced to the relevant test window and reviewed
for synthetic-only identifiers, unrelated traffic, and file size.

Every completed scenario must contain:

- a reviewed `.pcap` file;
- `packet_summary.txt`;
- `log_summary.txt`;
- a completed `README.md`;
- proof that the baseline worked again after restoration.

See
[`docs/06_failure_scenario_guide.md`](../../docs/06_failure_scenario_guide.md)
for the experiment method and safety rules.

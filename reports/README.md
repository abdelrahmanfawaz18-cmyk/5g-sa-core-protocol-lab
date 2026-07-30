# Reports

This directory contains concise lab-validation reports generated from verified
commands, logs, and connectivity tests.

Reports must use lab-only data and should summarize evidence rather than copy large raw logs.

- [Baseline configuration validation](configuration_validation.md)
- [Registration validation](registration_validation.md)
- [Registration tshark summary](registration_tshark_summary.txt)
- [UE interface and connectivity report](ue_interface_success.md)
- [User-plane tshark summary](user_plane_tshark_summary.txt)
- [User-plane validation](user_plane_validation.md)
- [Packet-analysis validation](packet_analysis_validation.md)
- [Live automated lab check](latest_lab_check.md)
- [Automation validation](automation_validation.md)
- [Repository release-readiness report](release_readiness.md)

The Python validator generates `latest_lab_check.md` with:

```bash
python3 tools/lab_check.py --output reports/latest_lab_check.md
```

The generated report is a concise point-in-time result. It must be reviewed
before being committed because live paths, addresses, and failure evidence can
vary between runs.

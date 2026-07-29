# Reports

This directory contains concise lab-validation reports generated from verified
commands, logs, and connectivity tests.

Reports must use lab-only data and should summarize evidence rather than copy large raw logs.

- [Phase 5 completion report](phase_5_completion.md)
- [Phase 6 completion report](phase_6_completion.md)
- [Phase 6 tshark summary](phase_6_tshark_summary.txt)
- [Phase 7 UE interface and connectivity report](ue_interface_success.md)
- [Phase 7 tshark summary](phase_7_tshark_summary.txt)
- [Phase 7 completion report](phase_7_completion.md)
- [Phase 8 completion report](phase_8_completion.md)
- [Phase 10 live lab check](latest_lab_check.md)
- [Phase 10 completion report](phase_10_completion.md)

Phase 10 generates `latest_lab_check.md` with:

```bash
python3 tools/lab_check.py --output reports/latest_lab_check.md
```

The generated report is a concise point-in-time result. It must be reviewed
before being committed because live paths, addresses, and failure evidence can
vary between runs.

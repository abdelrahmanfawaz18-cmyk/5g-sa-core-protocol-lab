# Scripts

This directory contains reproducible setup, run, capture, and network-helper
scripts developed during the lab.

Scripts must expose errors clearly, document required privileges, and avoid embedding secrets or machine-specific personal paths.

Phase 6 run scripts are under `run/`:

- `start_core.sh` starts any inactive required services and verifies core
  readiness.
- `capture_n2.sh` records NGAP/NAS signalling on SCTP port `38412`.
- `start_gnb.sh` runs the gNB in the foreground with the repository baseline.
- `start_ue.sh` runs the UE in the foreground with the repository baseline.

Run each script from its own terminal. The gNB, UE, and capture scripts remain
in the foreground so their output and failures stay visible. Stop them with
`Ctrl+C`.

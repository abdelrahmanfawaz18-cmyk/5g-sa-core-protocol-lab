# Scripts

This directory contains reproducible setup, run, capture, and network-helper
scripts developed during the lab.

Scripts must expose errors clearly, document required privileges, and avoid embedding secrets or machine-specific personal paths.

Phase 6 run scripts are under `run/`:

- `start_core.sh` starts any inactive required services and verifies core
  readiness.
- `capture_n2.sh` records NGAP/NAS signalling on SCTP port `38412`.
- `capture_pdu_session.sh` records N2, PFCP, GTP-U, and ICMP evidence for
  Phase 7.
- `start_gnb.sh` runs the gNB in the foreground with the repository baseline.
- `start_ue.sh` runs the UE in the foreground with the repository baseline.

Run each script from its own terminal. The gNB, UE, and capture scripts remain
in the foreground so their output and failures stay visible. Stop them with
`Ctrl+C`.

Phase 7 network helpers are under `network/`:

- `inspect_ue_network.sh` displays forwarding, routes, and relevant firewall
  state without changing them.
- `enable_ue_nat.sh` idempotently enables runtime forwarding and masquerading
  for the isolated `10.45.0.0/16` UE subnet.
- `cleanup_root_namespace_rules.sh` removes only the temporary same-host
  routing workarounds used while diagnosing the Phase 7 data path.

The UE baseline uses UERANSIM network-namespace isolation. In the successful
Phase 7 run, `uesimtun0` was placed in
`ueransim-999700000000001-internet-psi1`.

The network helpers use `sudo` for kernel networking and firewall state. The
NAT helper does not make its rules persistent across reboot.

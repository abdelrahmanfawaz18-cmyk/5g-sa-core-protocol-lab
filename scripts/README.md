# Scripts

This directory contains reproducible setup, run, capture, and network-helper
scripts developed during the lab.

Scripts must expose errors clearly, document required privileges, and avoid embedding secrets or machine-specific personal paths.

Baseline run scripts are under `run/`:

- `start_core.sh` starts any inactive required services and verifies core
  readiness.
- `capture_n2.sh` records NGAP/NAS signalling on SCTP port `38412`.
- `capture_pdu_session.sh` records N2, PFCP, GTP-U, and ICMP evidence for
  PDU-session and full-lifecycle analysis. An optional path argument selects
  the output file.
- `start_gnb.sh` runs the gNB in the foreground with the repository baseline.
- `start_ue.sh` runs the UE in the foreground with the repository baseline.

Run each script from its own terminal. The gNB, UE, and capture scripts remain
in the foreground so their output and failures stay visible. Stop them with
`Ctrl+C`.

User-plane network helpers are under `network/`:

- `inspect_ue_network.sh` displays forwarding, routes, and relevant firewall
  state without changing them.
- `enable_ue_nat.sh` idempotently enables runtime forwarding and masquerading
  for the isolated `10.45.0.0/16` UE subnet.
- `cleanup_root_namespace_rules.sh` removes only the temporary same-host
  routing workarounds used while diagnosing the UE data path.

The UE baseline uses UERANSIM network-namespace isolation. In the successful
run, `uesimtun0` was placed in
`ueransim-999700000000001-internet-psi1`.

The network helpers use `sudo` for kernel networking and firewall state. The
NAT helper does not make its rules persistent across reboot.

Controlled-failure helpers are under `failures/`:

- `verify_failure_baseline.sh` performs a read-only readiness check and refuses
  to treat the host as ready if the verified kernel, services, listener,
  interfaces, binaries, baseline configurations, or process state are wrong.
- `capture_wrong_plmn.sh` records the focused SCTP/NGAP evidence for the
  wrong-PLMN scenario and refuses to overwrite an earlier capture.
- `start_gnb_wrong_plmn.sh` starts the gNB with the isolated PLMN `999-71`
  configuration while preserving the normal PLMN `999-70` file. Its raw
  console log is local evidence and is ignored by Git until summarized.
- `capture_wrong_tac.sh` records N2 evidence while the gNB advertises the
  unsupported Tracking Area Code (TAC) `2`.
- `start_gnb_wrong_tac.sh` starts the gNB with TAC `2` while preserving the
  known-good TAC `1` file. If NG Setup succeeds, the normal UE is then used to
  test location handling during registration.
- `capture_wrong_subscriber_key.sh` records N2 NGAP/NAS evidence for the
  authentication experiment.
- `start_ue_wrong_subscriber_key.sh` starts a dedicated UE whose synthetic
  permanent key differs from the subscriber record by one hexadecimal digit.
  The known-good UE file and MongoDB subscriber record remain unchanged.
- `capture_wrong_dnn.sh` records N2 and Packet Forwarding Control Protocol
  (PFCP) evidence for the session-selection experiment.
- `start_ue_wrong_dnn.sh` starts a dedicated UE that requests the unsupported
  Data Network Name (DNN) `unsupported`. Authentication material and the
  known-good UE configuration remain unchanged.
- `capture_missing_nat.sh` records GTP-U and Internet Control Message Protocol
  (ICMP) evidence for the external return-path experiment.
- `remove_ue_nat_rule.sh` removes exactly one scoped UE masquerade rule while
  verifying that IPv4 forwarding and both UE forwarding rules stay enabled.
  Restore the rule immediately with `network/enable_ue_nat.sh`.

Run the baseline verifier before each controlled scenario. Never run a
failure launcher at the same time as the normal gNB or UE launcher.

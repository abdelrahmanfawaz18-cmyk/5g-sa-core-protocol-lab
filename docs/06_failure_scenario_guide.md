# Controlled Failure Scenario Guide

## Status

Phase 9 is in progress. The wrong-PLMN scenario is complete: its isolated
fault, packet evidence, concise logs, restoration, and successful recovery
have been verified. Wrong TAC is the next scenario.

## Purpose

The successful Phase 8 capture established a known-good reference. Phase 9
changes one variable at a time and compares the resulting protocol boundary
with that reference.

The method is:

```text
verify baseline
  -> predict the failure boundary
  -> start a focused capture
  -> introduce one isolated mismatch
  -> identify the last successful event
  -> identify the first failed or missing event
  -> stop the faulty process
  -> restore the unchanged baseline
  -> prove successful recovery
  -> document only the reviewed evidence
```

## Safety Rules

1. Do not edit the known-good UERANSIM baseline files during an experiment.
2. Use a scenario-specific configuration or a narrowly scoped runtime change.
3. Change exactly one variable.
4. Start packet capture before triggering the failure.
5. Keep raw logs and captures local until they have been reviewed.
6. Stop the faulty process before starting the recovery test.
7. Restore the changed value or runtime rule immediately after the test.
8. Confirm the known-good behavior returns.
9. Do not run two scenarios at the same time.
10. Do not change global forwarding when a scenario-specific NAT rule can be
    removed safely.

## Scenario Order

| Order | Scenario | Primary boundary | Main concepts |
| ---: | --- | --- | --- |
| 1 | Wrong PLMN — complete | N2 NG Setup | SCTP transport versus NGAP acceptance |
| 2 | Wrong TAC | N2 or registration location handling | Tracking Area Identity |
| 3 | Wrong subscriber key or OPc | NAS authentication | 5G-AKA challenge and response |
| 4 | Wrong DNN | PDU-session establishment | Registration versus data-session authorization |
| 5 | Missing NAT | N6 return path | Successful 5G tunnel versus Linux external routing |

PLMN means Public Land Mobile Network. TAC means Tracking Area Code. OPc is
the derived Operator Code used by the authentication algorithm. DNN means Data
Network Name. NAT means Network Address Translation.

## Evidence Required For Every Scenario

Each scenario directory must contain:

- `README.md` with the experiment and final interpretation;
- one reviewed packet capture;
- `packet_summary.txt` with concise protocol landmarks;
- `log_summary.txt` with only relevant log excerpts.

The README must state:

- known-good baseline;
- intentional change;
- predicted boundary;
- observed symptom;
- last successful procedure;
- first failed or missing procedure;
- packet and log evidence;
- root cause;
- restoration action;
- successful recovery proof;
- concise technical explanation.

## Scenario 1: Wrong PLMN

The baseline gNodeB (gNB) advertises:

```text
MCC: 999
MNC: 70
PLMN: 999-70
```

The isolated failure configuration advertises:

```text
MCC: 999
MNC: 71
PLMN: 999-71
```

Every other gNB field remains identical.

### Prediction

The gNB should still reach the Access and Mobility Management Function (AMF)
at `127.0.0.5:38412` and may establish its Stream Control Transmission
Protocol (SCTP) association. It then sends an NG Setup Request using Next
Generation Application Protocol (NGAP).

The AMF is configured for PLMN `999-70`, so it should not accept the gNB's
advertised PLMN `999-71`. The observed implementation may return an NG Setup
Failure or terminate the association. The actual result must be recorded
rather than assumed.

### What This Distinguishes

```text
SCTP success = transport endpoint is reachable
NG Setup success = AMF accepts the gNB's 5G configuration
```

Transport success alone does not prove the Radio Access Network node is
admitted by the core.

### Recovery

The faulty gNB is stopped. The normal launcher then uses the unchanged
baseline configuration:

```text
configs/ueransim/open5gs-gnb.yaml
```

An NG Setup Response and the UERANSIM message
`NG Setup procedure is successful` provide recovery proof.

## Later Scenarios

The remaining scenario folders are prepared but must be implemented and run
one at a time. Their README files contain the planned single change and
expected boundary.

## Completion Gate

Phase 9 is complete only when all five scenario folders contain reviewed
evidence and every scenario has a successful rollback test.

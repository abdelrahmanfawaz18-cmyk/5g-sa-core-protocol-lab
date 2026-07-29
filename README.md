# 5G SA Core Protocol Lab

This project is a hands-on 5G Standalone lab built with Open5GS and UERANSIM. It will demonstrate UE registration, authentication, PDU session establishment, user-plane traffic through the UPF, Wireshark/tshark packet analysis, deliberate failure reproduction, and Python-based lab validation.

All subscriber identifiers, keys, network names, addresses, and examples in this repository are for a local lab only. Do not reuse real mobile-network secrets or production subscriber data here.

## Architecture Diagram

The complete labelled map, including network functions, interfaces,
protocols, and control/user-plane separation, is in the
[5G Standalone learning handbook](docs/learning/README.md).

```text
Simulated UE
    |
    | N1: 5G NAS, carried through the gNB
    v
UERANSIM gNB
    | \
    |  \ N3: GTP-U/UDP
    |   \
    |    v
    |   Open5GS UPF ---- N6: IP ---- Data Network
    |          ^
    |          |
    |          | N4: PFCP/UDP
    v          |
Open5GS AMF -- Open5GS SMF
 N2: NGAP/SCTP
```

## Target Skills Demonstrated

- 5G Standalone core lab setup
- Open5GS configuration
- UERANSIM gNB and UE simulation
- Linux networking and routing
- NGAP, NAS-5GS, PFCP, GTP-U, SCTP, and IP packet analysis
- Wireshark and tshark capture workflows
- Failure reproduction and troubleshooting
- Python validation tooling
- Clear technical documentation

## Current Status

- [x] Environment prepared
- [x] Open5GS installed
- [x] UERANSIM installed
- [x] gNB connected to AMF
- [x] UE registered
- [x] PDU session established
- [x] User traffic passed through UPF
- [x] Successful packet captures collected
- [x] Packet-analysis guide and Wireshark evidence completed
- [x] Failure scenarios documented
- [x] Python lab validation tool completed

## Roadmap Checklist

- [x] Phase 1: Create local repository shell
- [x] Phase 1: Add README skeleton
- [x] Phase 1: Add `.gitignore`
- [x] Phase 1: Add initial documentation
- [x] Phase 1: Create public GitHub repository
- [x] Phase 1: Push first commit
- [x] Phase 2: Environment preflight
- [x] Phase 3: Open5GS installation
- [x] Phase 4: UERANSIM installation
- [x] Phase 5: Baseline configuration
- [x] Phase 6: Successful registration
- [x] Phase 7: PDU session and user-plane traffic
- [x] Phase 8: Packet capture evidence
- [x] Phase 9: Failure scenarios
- [x] Phase 10: Python lab validation tool
- [ ] Phase 11: GitHub README polish
- [ ] Phase 12: Final project notes and cleanup

## Repository Structure

```text
5g-sa-core-protocol-lab/
  README.md
  .gitignore
  docs/
  configs/
  scripts/
  tools/
  captures/
  reports/
  screenshots/
  diagrams/
  tests/
```

## Beginner Notes

Work through the roadmap one phase at a time. Phases 1 through 9 are complete:
the repository is established, the Ubuntu environment passed preflight,
Open5GS is installed and healthy, UERANSIM is built, and the shared baseline
configuration and synthetic subscriber are validated. The gNB connected to
the AMF, and the UE completed authentication, NAS security activation, and
registration. The UE then established an IPv4 PDU session, received an
isolated tunnel interface, and passed bidirectional traffic through the UPF.
The complete lifecycle is captured, filtered, and interpreted with tshark and
Wireshark. Five controlled failures now document how PLMN, TAC, authentication
material, DNN, and NAT faults appear and how each baseline is restored. The
current phase automates lab validation with Python.

Before starting the controlled failure scenarios, use the
[5G Standalone learning handbook](docs/learning/README.md) to build a reusable
mental model of the architecture. It includes a full system map, component
responsibilities, interface and protocol tables, identifier explanations, the
complete successful procedure, packet-analysis methods, and an acronym
glossary.

For a detailed explanation of what was completed and how the 5G components
communicate, read the [beginner guide to Phases 1-4](docs/phases_1_to_4/README.md).

The shared Phase 5 values and matching rules are documented in the
[lab configuration map](docs/configuration_map.md). The supporting checks are
summarized in the [Phase 5 completion report](reports/phase_5_completion.md).

The observed registration messages are explained in the
[successful registration flow](docs/03_successful_registration_flow.md), with
supporting results in the
[Phase 6 completion report](reports/phase_6_completion.md).

The control and user-plane steps are explained in the
[PDU session flow](docs/04_pdu_session_flow.md), with interface and routing
evidence in the
[UE connectivity report](reports/ue_interface_success.md) and the final gate
in the [Phase 7 completion report](reports/phase_7_completion.md).

The [packet capture guide](docs/05_packet_capture_guide.md) explains how to
separate control-plane and user-plane traffic, follow encapsulation, and
correlate protocol messages. The supporting gate is in the
[Phase 8 completion report](reports/phase_8_completion.md).

The [controlled failure scenario guide](docs/06_failure_scenario_guide.md)
defines the Phase 9 one-variable method, safety checks, evidence requirements,
and recovery gate.

## Python Lab Validation Tool

Phase 10 provides a read-only validator that checks required commands,
MongoDB/Open5GS services, listening protocol endpoints, current gNB and UE
logs, PDU-session state, the UE tunnel interface, and connectivity from inside
the UE namespace.

Generate a report with:

```bash
python3 tools/lab_check.py --output reports/latest_lab_check.md
```

For the complete live workflow and all options, see the
[validation tool guide](tools/README.md). Run the automated tests with:

```bash
python3 -m unittest discover -s tests -v
```

## Packet Analysis Quick Reference

| Filter | Purpose |
| --- | --- |
| `sctp` | N2 transport association and shutdown |
| `ngap` | gNB-to-AMF signalling |
| `nas-5gs` | Decodable UE-to-core NAS messages |
| `pfcp` | SMF-to-UPF control |
| `gtp` | N3 user-plane tunnelling |
| `gtp && icmp` | Ping traffic inside GTP-U |
| `icmp && !gtp` | Plain ping traffic outside GTP-U |

### NGAP Carrying NAS

![NGAP Initial UE Message carrying a NAS Registration Request](screenshots/wireshark_ngap_nas.png)

### PFCP And GTP-U

![PFCP session setup and GTP-U ICMP evidence](screenshots/wireshark_pfcp_gtpu.png)

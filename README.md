# 5G SA Core Protocol Lab

This project is a hands-on 5G Standalone lab built with Open5GS and UERANSIM. It will demonstrate UE registration, authentication, PDU session establishment, user-plane traffic through the UPF, Wireshark/tshark packet analysis, deliberate failure reproduction, and Python-based lab validation.

All subscriber identifiers, keys, network names, addresses, and examples in this repository are for a local lab only. Do not reuse real mobile-network secrets or production subscriber data here.

## Architecture Diagram

The final diagram will be added after the lab design is confirmed.

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
- [ ] UERANSIM installed
- [ ] gNB connected to AMF
- [ ] UE registered
- [ ] PDU session established
- [ ] User traffic passed through UPF
- [ ] Successful packet captures collected
- [ ] Failure scenarios documented
- [ ] Python lab validation tool completed

## Roadmap Checklist

- [x] Phase 1: Create local repository shell
- [x] Phase 1: Add README skeleton
- [x] Phase 1: Add `.gitignore`
- [x] Phase 1: Add initial documentation
- [x] Phase 1: Create public GitHub repository
- [x] Phase 1: Push first commit
- [x] Phase 2: Environment preflight
- [x] Phase 3: Open5GS installation
- [ ] Phase 4: UERANSIM installation
- [ ] Phase 5: Baseline configuration
- [ ] Phase 6: Successful registration
- [ ] Phase 7: PDU session and user-plane traffic
- [ ] Phase 8: Packet capture evidence
- [ ] Phase 9: Failure scenarios
- [ ] Phase 10: Python lab validation tool
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

Work through the roadmap one phase at a time. Phases 1 through 3 are complete: the repository is established, the Ubuntu environment passed preflight, and Open5GS is installed and healthy. The next phase is UERANSIM installation, which should begin only when explicitly started.

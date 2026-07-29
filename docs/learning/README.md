# 5G Standalone Learning Handbook

## Purpose

This handbook builds a mental model of the 5G Standalone system used in this
lab. It explains the architecture before the controlled failure experiments
begin.

The documents use the same Open5GS, UERANSIM, Linux, and packet-capture
examples that were observed in the successful lab run. They are intended to
be read in order the first time and used as individual references afterward.

## How To Use The Handbook

Read one document at a time. After each document, return to its review
questions and answer them without reading the preceding text. An answer does
not need to use standards language; it needs to describe the correct
responsibility and packet path.

When an acronym appears for the first time in a section, its full name is
written beside it. The final glossary provides a quick lookup when a term is
forgotten.

## Reading Order

| Order | Document | Main question answered |
| ---: | --- | --- |
| 1 | [Full Architecture Map](01_full_architecture_map.md) | What are the major parts, and how are they connected? |
| 2 | [Network Functions](02_network_functions.md) | What responsibility does each component own? |
| 3 | [Interfaces, Protocols, Planes, and Layers](03_interfaces_protocols_planes_and_layers.md) | What communicates, how does it communicate, and what type of traffic is it? |
| 4 | [Identifiers and Configuration](04_identifiers_and_configuration.md) | Which values identify the network, subscriber, slice, session, and tunnel? |
| 5 | [End-to-End Procedures](05_end_to_end_procedures.md) | In what order do setup, registration, session creation, and data transfer happen? |
| 6 | [Packet Analysis and Troubleshooting](06_packet_analysis_and_troubleshooting.md) | How can a failure be localized using packets, logs, and configuration? |
| 7 | [Acronym Glossary](07_acronym_glossary.md) | What does a forgotten acronym mean? |

## Four Terms That Must Stay Separate

| Term | Meaning | Example |
| --- | --- | --- |
| Network function | A software or network component with a defined responsibility | The Access and Mobility Management Function (AMF) handles access and mobility signalling |
| Interface or reference point | A defined relationship between two endpoints | N2 connects the gNodeB (gNB) to the AMF |
| Protocol | The rules and message formats used to communicate | Next Generation Application Protocol (NGAP) is used on N2 |
| Plane | The purpose of the traffic | Control-plane traffic creates state; user-plane traffic carries the UE's data |

One statement can use all four terms:

> The gNB and the AMF are endpoints, N2 is their interface, NGAP is their
> signalling protocol, and their NGAP messages are control-plane traffic.

## Scope

The handbook focuses on the single-host lab:

- Open5GS provides the 5G Core.
- UERANSIM provides one simulated gNB and one simulated User Equipment (UE).
- MongoDB stores the synthetic subscriber record used through the Unified
  Data Repository (UDR).
- Linux supplies process control, network namespaces, packet forwarding,
  routing, and Network Address Translation (NAT).
- Wireshark, tshark, tcpdump, and dumpcap provide packet evidence.

Some optional 5G Core functions are included for architectural context even
though the baseline does not actively exercise them.

## Learning Checkpoint

The handbook has served its purpose when the successful run can be explained
as this chain:

1. The gNB establishes transport and an N2 relationship with the AMF.
2. The UE sends Non-Access-Stratum (NAS) registration signalling through the
   gNB to the AMF.
3. The AMF coordinates subscriber authentication through core services.
4. The UE and core activate NAS security and complete registration.
5. The Session Management Function (SMF) creates a Protocol Data Unit (PDU)
   session and programs the User Plane Function (UPF).
6. The gNB and UPF build the N3 user-plane tunnel.
7. The UE sends an Internet Protocol (IP) packet through the tunnel.
8. The UPF decapsulates and forwards it, while Linux routing and NAT provide
   external reachability.

## Related Lab Documents

- [Lab configuration map](../configuration_map.md)
- [Successful registration flow](../03_successful_registration_flow.md)
- [PDU session and user-plane flow](../04_pdu_session_flow.md)
- [Packet capture guide](../05_packet_capture_guide.md)

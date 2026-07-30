# 5G Acronym Glossary

## How To Use This Reference

This is a quick lookup table, not a replacement for the earlier explanations.
The “what it does” column describes the term in the context of this lab.

## Architecture And Network Functions

| Acronym | Full name | What it does |
| --- | --- | --- |
| 5GC | 5G Core | Contains control and user-plane functions that provide 5G services |
| 5GS | 5G System | Refers to the complete 5G system, including access and core |
| AF | Application Function | Provides service-related influence or information to the core when used |
| AMF | Access and Mobility Management Function | Handles gNB access, UE registration, NAS termination, reachability, and mobility |
| AUSF | Authentication Server Function | Supports network-side subscriber authentication |
| BSF | Binding Support Function | Helps discover policy-function bindings when that service is used |
| DN | Data Network | External network reached through the UPF |
| gNB | gNodeB | 5G base station connecting the UE to the core |
| NEF | Network Exposure Function | Exposes selected network capabilities through controlled services |
| NF | Network Function | A component with a defined role in the 5G system |
| NG-RAN | Next Generation Radio Access Network | 5G access network containing gNBs |
| NRF | Network Repository Function | Registers and helps discover core network functions |
| NSSF | Network Slice Selection Function | Assists selection of a suitable network slice |
| PCF | Policy Control Function | Supplies access and session policy decisions |
| RAN | Radio Access Network | Connects subscriber devices to the mobile core |
| SBA | Service-Based Architecture | 5G Core design where control functions expose and consume services |
| SCP | Service Communication Proxy | Assists routing and communication between service-based functions |
| SEPP | Security Edge Protection Proxy | Protects inter-operator control-plane communication |
| SMF | Session Management Function | Creates and manages PDU sessions and controls the UPF |
| UDM | Unified Data Management | Provides subscriber identity, authentication, and subscription services |
| UDR | Unified Data Repository | Provides persistent structured data services to authorized core functions |
| UE | User Equipment | Subscriber device that registers and sends or receives user data |
| UERANSIM | UE and RAN Simulator project name | Provides the simulated UE and gNB used by the lab |
| UPF | User Plane Function | Encapsulates, decapsulates, and forwards UE user traffic |
| USIM | Universal Subscriber Identity Module | Secure subscriber module that normally holds identity and authentication material |

## Interfaces And Architecture References

| Acronym | Full name | What it connects or does |
| --- | --- | --- |
| N1 | N1 reference point | Logical UE-to-AMF NAS signalling relationship |
| N2 | N2 reference point | gNB-to-AMF control-plane relationship |
| N3 | N3 reference point | gNB-to-UPF user-plane tunnel |
| N4 | N4 reference point | SMF-to-UPF control relationship |
| N6 | N6 reference point | UPF-to-Data Network user-plane relationship |
| N11 | N11 service relationship | AMF-to-SMF session coordination |
| N12 | N12 service relationship | AMF-to-AUSF authentication service |
| N13 | N13 service relationship | AUSF-to-UDM authentication service |
| N22 | N22 service relationship | AMF-to-NSSF slice-selection service |
| SBI | Service-Based Interface | HTTP-based communication among 5G Core control functions |
| Uu | Uu radio interface | UE-to-gNB radio relationship; represented by UERANSIM software in this lab |

## Protocols And Packet Concepts

| Acronym | Full name | What it does |
| --- | --- | --- |
| DNS | Domain Name System | Resolves domain names to IP addresses |
| F-TEID | Fully Qualified Tunnel Endpoint Identifier | Combines tunnel identity with endpoint addressing information |
| GPRS | General Packet Radio Service | Name retained in the GTP protocol family for historical continuity |
| GTP | General Packet Radio Service Tunnelling Protocol | Protocol family used for mobile-network tunnelling |
| GTP-U | General Packet Radio Service Tunnelling Protocol User Plane | Encapsulates UE user packets on N3 |
| HTTP/2 | Hypertext Transfer Protocol version 2 | Carries service-based core requests and responses |
| ICMP | Internet Control Message Protocol | Carries diagnostics such as ping request and reply |
| IP | Internet Protocol | Provides addressed packet delivery |
| IPv4 | Internet Protocol version 4 | Address family used by the baseline PDU session |
| IPv6 | Internet Protocol version 6 | Newer address family not enabled for the baseline PDU session |
| NAS | Non-Access Stratum | UE-to-core signalling for registration, mobility, security, and sessions |
| NAS-5GS | Non-Access-Stratum protocol for the 5G System | 5G-specific NAS message set |
| NGAP | Next Generation Application Protocol | gNB-to-AMF signalling on N2 |
| PDCP | Packet Data Convergence Protocol | Radio-stack layer for header, security, and data handling functions |
| PFCP | Packet Forwarding Control Protocol | Lets the SMF program and manage UPF forwarding state |
| RLC | Radio Link Control | Radio-stack layer handling segmentation and delivery functions |
| RRC | Radio Resource Control | Controls the UE's radio-access connection and configuration |
| SCTP | Stream Control Transmission Protocol | Reliable message-oriented transport used under NGAP |
| TCP | Transmission Control Protocol | Reliable byte-stream transport used under HTTP-based services |
| TEID | Tunnel Endpoint Identifier | Identifies a directional GTP-U tunnel at its receiver |
| TLS | Transport Layer Security | Protects transport connections when configured |
| UDP | User Datagram Protocol | Connectionless transport used under PFCP and GTP-U |

## Subscriber, Network, And Location Identity

| Acronym | Full name | What it identifies |
| --- | --- | --- |
| 5G-GUTI | 5G Globally Unique Temporary UE Identity | Temporary UE identity assigned by the serving network |
| GUAMI | Globally Unique AMF Identifier | Serving AMF using PLMN, region, set, and pointer |
| IMSI | International Mobile Subscriber Identity | Common digit-based form of permanent subscriber identity |
| MCC | Mobile Country Code | Country portion of a PLMN |
| MNC | Mobile Network Code | Network portion of a PLMN |
| NCI | NR Cell Identity | A New Radio cell |
| NR | New Radio | 5G radio-access technology |
| PLMN | Public Land Mobile Network | Mobile network formed from MCC and MNC |
| SUCI | Subscription Concealed Identifier | Privacy-protected representation of a permanent subscriber identity |
| SUPI | Subscription Permanent Identifier | Permanent subscription identity |
| TAC | Tracking Area Code | Tracking area within a PLMN |
| TAI | Tracking Area Identity | Combined PLMN and TAC |

## Authentication And Security

| Acronym or term | Full name | What it does |
| --- | --- | --- |
| 5G-AKA | 5G Authentication and Key Agreement | Authenticates subscriber/network relationship and establishes key material |
| AUTN | Authentication Token | Lets the UE verify the authentication challenge and freshness |
| IA2 | 5G integrity algorithm 2 | Integrity algorithm selected in the baseline |
| K | Permanent subscriber authentication key | Secret input shared by subscriber and home-side system |
| OP | Operator variant algorithm configuration field | Operator-specific Milenage input |
| OPc | Derived Operator Code | Subscriber-specific value derived from OP and K |
| RAND | Random Challenge | Random input for an authentication exchange |
| RES* | 5G authentication Response | UE-calculated response to the challenge |
| SQN | Sequence Number | Adds freshness and replay protection to authentication |
| XRES* | Expected 5G authentication Response | Network-side expected response |

The authentication field named `amf` in the UE YAML means Authentication
Management Field. It is not the Access and Mobility Management Function.

## Slice, Session, And Policy

| Acronym | Full name | What it does |
| --- | --- | --- |
| 5QI | 5G QoS Identifier | References Quality of Service characteristics |
| APN | Access Point Name | Earlier-generation data-network name; used as a UERANSIM field for the DNN |
| DNN | Data Network Name | Identifies the data network requested for a PDU session |
| PDU | Protocol Data Unit | Unit of data at a protocol layer |
| QFI | QoS Flow Identifier | Identifies a QoS flow within a PDU session |
| QoS | Quality of Service | Traffic treatment characteristics such as priority and delay behavior |
| SD | Slice Differentiator | Optional value distinguishing slices with the same SST |
| SEID | Session Endpoint Identifier | Identifies a PFCP session endpoint |
| S-NSSAI | Single Network Slice Selection Assistance Information | Identifies one network slice using SST and optional SD |
| SST | Slice/Service Type | Indicates the general service behavior of a network slice |

## PFCP Rule Terms

| Acronym | Full name | What it does |
| --- | --- | --- |
| FAR | Forwarding Action Rule | Tells the UPF what forwarding action to take |
| PDR | Packet Detection Rule | Tells the UPF how to recognize session traffic |
| QER | QoS Enforcement Rule | Supplies Quality of Service enforcement parameters |
| URR | Usage Reporting Rule | Defines usage measurement and reporting |

## Linux And Lab Terms

| Acronym or term | Full name | What it does |
| --- | --- | --- |
| NAT | Network Address Translation | Translates private UE addressing for external reachability |
| TUN | Network Tunnel interface | Presents layer-3 IP packets between Linux and a user-space process |
| YAML | YAML Ain't Markup Language | Human-readable configuration format used by Open5GS and UERANSIM |

## Quick Relationship Table

| If this term is seen | Associate it with |
| --- | --- |
| AMF | Registration, NAS, access, mobility |
| AUSF and UDM | Authentication |
| UDR and MongoDB | Persistent subscriber data |
| NSSF and S-NSSAI | Slice selection |
| SMF, DNN, and PDU Session ID | Session management |
| SMF, UPF, and PFCP | User-plane rule creation |
| gNB, UPF, GTP-U, and TEID | N3 user tunnel |
| UPF, N6, IP, routing, and NAT | External data path |
| N2, NGAP, and SCTP | gNB-to-AMF control |
| N1 and NAS-5GS | Logical UE-to-AMF control |

## Authoritative Starting References

- [3GPP TS 23.501: System architecture for the 5G System](https://www.3gpp.org/dynareport/23501.htm)
- [3GPP TS 23.502: Procedures for the 5G System](https://www.3gpp.org/dynareport/23502.htm)
- [3GPP TS 24.501: Non-Access-Stratum protocol for the 5G System](https://www.3gpp.org/dynareport/24501.htm)
- [3GPP TS 38.413: NG-RAN; NG Application Protocol](https://www.3gpp.org/dynareport/38413.htm)
- [Open5GS Quickstart](https://open5gs.org/open5gs/docs/guide/01-quickstart/)
- [UERANSIM configuration reference](https://github.com/aligungr/UERANSIM/wiki/Configuration)

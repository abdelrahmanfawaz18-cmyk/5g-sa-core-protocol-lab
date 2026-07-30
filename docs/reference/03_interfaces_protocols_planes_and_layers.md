# Interfaces, Protocols, Planes, And Layers

## Why These Terms Are Confusing

The same packet can be described in several correct ways:

```text
It is control-plane traffic.
It crosses N2.
It uses NGAP.
NGAP is carried by SCTP.
SCTP is carried by IP.
It contains a NAS message from the UE.
```

Each sentence describes a different dimension: purpose, interface, protocol,
transport, network layer, or nested payload.

## Interfaces And Reference Points

An interface or reference point defines which endpoints communicate and why.
It is not itself always the name of a protocol.

| Interface | Endpoints | Main protocol or service | Plane | Responsibility |
| --- | --- | --- | --- | --- |
| Uu | UE and gNB | 5G New Radio stack | Control and user | Radio access; represented by a software link in UERANSIM |
| N1 | UE and AMF, logically | NAS-5GS | Control | Registration, authentication, security, mobility, and session signalling |
| N2 | gNB and AMF | NGAP over SCTP | Control | NG-RAN control, UE context, location, and NAS relay |
| N3 | gNB and UPF | GTP-U over UDP | User | Tunnels UE user packets between access and core |
| N4 | SMF and UPF | PFCP over UDP | Control | Creates, changes, and removes UPF forwarding state |
| N6 | UPF and Data Network | Ordinary IP | User | Carries decapsulated traffic toward or from an external network |
| N11 | AMF and SMF | Service-Based Interface service operations | Control | Coordinates PDU-session handling |
| N12 | AMF and AUSF | Service-Based Interface service operations | Control | Requests subscriber authentication service |
| N13 | AUSF and UDM | Service-Based Interface service operations | Control | Obtains home-side authentication service |
| N22 | AMF and NSSF | Service-Based Interface service operations | Control | Requests slice-selection assistance |
| Nudr | UDR service used by authorized core functions | Service-Based Interface service operations | Control data | Retrieves or stores structured core data |
| SBI | Core control functions | HTTP-based service communication | Control | General service registration, discovery, and function-to-function operations |

N1 is special. It is a logical UE-to-AMF relationship:

```text
UE creates NAS
  -> gNB receives it through the access side
  -> gNB places NAS inside an NGAP NAS-PDU
  -> NGAP crosses N2
  -> AMF extracts and processes NAS
```

## Protocol Reference

| Acronym | Full name | Typical location | What it does |
| --- | --- | --- | --- |
| RRC | Radio Resource Control | UE to gNB access signalling | Establishes and manages radio-control state |
| NAS-5GS | Non-Access-Stratum protocol for the 5G System | Logical N1, UE to AMF | Carries registration, authentication, security, mobility, and session-management messages |
| NGAP | Next Generation Application Protocol | N2, gNB to AMF | Carries NG-RAN procedures, UE context, location, session-resource control, and NAS payloads |
| SCTP | Stream Control Transmission Protocol | Under NGAP on N2 | Provides reliable message-oriented transport with associations, chunks, and streams |
| HTTP/2 | Hypertext Transfer Protocol version 2 | Service-Based Interface | Carries service requests and responses between 5G Core control functions |
| PFCP | Packet Forwarding Control Protocol | N4, SMF to UPF | Installs and updates user-plane packet detection and forwarding rules |
| GTP-U | General Packet Radio Service Tunnelling Protocol User Plane | N3, gNB to UPF | Encapsulates UE user packets and identifies directional tunnels using TEIDs |
| UDP | User Datagram Protocol | Under PFCP and GTP-U | Provides connectionless transport using ports |
| IP | Internet Protocol | N2, N3, N4, N6, and SBI | Provides addressed packet delivery between endpoints |
| ICMP | Internet Control Message Protocol | Inside the UE data path | Carries diagnostic messages such as ping request and reply |
| DNS | Domain Name System | UE data traffic when names are resolved | Maps domain names to IP addresses |

## Port Reference For This Lab

| Protocol use | Transport | Standard or baseline port | Lab endpoints |
| --- | --- | ---: | --- |
| NGAP | SCTP | `38412` | gNB `127.0.0.1` to AMF `127.0.0.5` |
| PFCP | UDP | `8805` | SMF `127.0.0.4` to UPF `127.0.0.7` |
| GTP-U | UDP | `2152` | gNB `127.0.0.1` to UPF `127.0.0.7` |

The port identifies a receiving service. It does not replace the protocol
name or interface name. For example, UDP port `2152` helps identify GTP-U,
while N3 describes the gNB-to-UPF relationship.

## Planes

A plane groups traffic by its purpose.

| Plane | Purpose | Examples in this lab | What it does not carry |
| --- | --- | --- | --- |
| Control plane | Creates, changes, and releases network state | NG Setup, Registration Request, Authentication, PFCP rules | The UE's actual ping payload |
| User plane | Carries subscriber data after control state exists | Inner ICMP packet inside GTP-U, decapsulated N6 IP | Subscriber authentication decisions |
| Management plane | Configures and operates the system | YAML files, systemd services, logs, subscriber provisioning | Normal UE protocol signalling |

The management plane is operational rather than part of the live UE protocol
exchange. Editing an AMF YAML file changes how the AMF behaves, but the YAML
file itself is not sent as NGAP.

## Protocol Stacks

### N2 stack

```text
+-------------------------------------------+
| NAS-5GS payload, when an NGAP message      |
| carries UE-to-core signalling              |
+-------------------------------------------+
| Next Generation Application Protocol      |
| (NGAP)                                     |
+-------------------------------------------+
| Stream Control Transmission Protocol      |
| (SCTP)                                     |
+-------------------------------------------+
| Internet Protocol (IP)                     |
+-------------------------------------------+
| Linux link or loopback capture layer       |
+-------------------------------------------+
```

NGAP can carry procedures that contain no NAS, such as NG Setup. When it does
carry NAS, the NAS message remains logically between the UE and AMF.

### N3 stack

```text
+-------------------------------------------+
| UE payload, such as ICMP                   |
+-------------------------------------------+
| Inner UE Internet Protocol packet          |
+-------------------------------------------+
| GPRS Tunnelling Protocol User Plane        |
| (GTP-U)                                    |
+-------------------------------------------+
| User Datagram Protocol (UDP)               |
+-------------------------------------------+
| Outer transport Internet Protocol packet   |
+-------------------------------------------+
| Linux link or loopback capture layer       |
+-------------------------------------------+
```

The outer IP addresses deliver the tunnel packet between gNB and UPF. The
inner IP addresses belong to the UE packet and its data-network destination.

### N4 stack

```text
+-------------------------------------------+
| Packet Forwarding Control Protocol (PFCP)  |
+-------------------------------------------+
| User Datagram Protocol (UDP)               |
+-------------------------------------------+
| Internet Protocol (IP)                     |
+-------------------------------------------+
| Linux link or loopback capture layer       |
+-------------------------------------------+
```

PFCP describes forwarding behavior. It does not encapsulate the UE's ping.

### Service-Based Interface stack

```text
+-------------------------------------------+
| 5G Core service operation and data         |
+-------------------------------------------+
| HTTP/2                                     |
+-------------------------------------------+
| Transmission Control Protocol (TCP)        |
+-------------------------------------------+
| Internet Protocol (IP)                     |
+-------------------------------------------+
```

Production deployments may protect these connections with Transport Layer
Security (TLS). The exact local Open5GS transport settings depend on its
configuration.

## Layers Versus Planes

A layer explains encapsulation or functional abstraction. A plane explains
purpose. They are not competing classifications.

| Layer or viewpoint | Question it answers | Example |
| --- | --- | --- |
| Procedure | What 5G operation is happening? | Registration or PDU-session establishment |
| Application signalling | Which 5G messages express the operation? | NAS-5GS, NGAP, or PFCP |
| Transport | How are messages delivered between processes? | SCTP, TCP, or UDP |
| Network | How are endpoints addressed and routed? | Outer IPv4 addresses |
| Tunnel | How is one network packet carried through another path? | GTP-U with a TEID |
| Inner user packet | What did the UE actually send? | IPv4 containing an ICMP Echo Request |
| Link or capture | Where did the operating system observe the frame? | Linux cooked capture on pseudo-interface `any` |

Frame `26` from the successful capture is user-plane traffic with several
layers:

```text
Outer IP 127.0.0.1 -> 127.0.0.7
  UDP port 2152
    GTP-U with a tunnel endpoint identifier
      Inner IP 10.45.0.2 -> 8.8.8.8
        ICMP Echo Request
```

The entire stack is user-plane traffic. IP, UDP, GTP-U, inner IP, and ICMP are
its nested protocol layers.

## Encapsulation And Decapsulation

Encapsulation means adding a new header around an existing packet.

For uplink traffic:

```text
Original UE IP packet
  + GTP-U header
  + UDP header
  + outer IP header
  = N3 tunnel packet
```

The gNB encapsulates the UE packet. The UPF decapsulates it before forwarding
the inner packet toward N6.

For downlink traffic, the UPF performs the encapsulation and the gNB removes
the wrapper.

## Control Dependency

The user plane depends on earlier control-plane work:

```text
NAS session request
  -> session authorized
  -> PFCP rules installed
  -> N3 tunnel information exchanged
  -> user packets can be forwarded
```

A control-plane success does not guarantee later user-plane success. It only
proves that the completed control stage worked.

## Protocol and Layer Conclusions

- N3 is a reference point between the gNB and UPF; GTP-U is its user-plane
  tunnelling protocol.
- A GTP-U packet contains an outer transport header for the tunnel and an
  inner IP packet created by the UE.
- NGAP includes both NAS-carrying procedures and access-network procedures
  such as NG Setup that contain no NAS.
- PFCP is control-plane traffic because it creates forwarding rules; it does
  not carry the UE payload governed by those rules.
- UDP port `2152` identifies the GTP-U endpoint used on N3.

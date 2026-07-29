# End-To-End 5G Procedures

## The Dependency Chain

The successful lab run is not one procedure. It is a dependency chain:

```text
Core readiness
  -> gNB transport
  -> NG Setup
  -> UE cell selection
  -> UE registration
  -> authentication
  -> NAS security
  -> PDU-session establishment
  -> UPF programming
  -> N3 tunnel resource setup
  -> UE address and route
  -> user-plane traffic
  -> controlled release
```

Every later stage depends on enough earlier stages succeeding.

## Procedure 0: Core Readiness

Before the gNB or UE starts, the lab verifies:

- MongoDB is active;
- required Open5GS services are active;
- the Access and Mobility Management Function (AMF) listens for Stream
  Control Transmission Protocol (SCTP) on `127.0.0.5:38412`;
- the User Plane Function (UPF) has its `ogstun` interface;
- matching baseline configuration and subscriber data exist.

This is management-plane readiness. It proves the software is available, not
that any 5G procedure has succeeded.

## Procedure 1: SCTP Association And NG Setup

### Transport first

The gNodeB (gNB) opens a Stream Control Transmission Protocol (SCTP)
association to the AMF.

The observed SCTP handshake is:

```text
gNB -> AMF: INIT
AMF -> gNB: INIT ACK
gNB -> AMF: COOKIE ECHO
AMF -> gNB: COOKIE ACK
```

SCTP is message-oriented transport. It provides features such as:

- reliable delivery;
- multiple logical streams;
- association management;
- path-awareness features.

SCTP success proves IP reachability, the port, and transport behavior. It does
not prove that the AMF accepts the gNB's 5G configuration.

### NG Setup second

After transport exists:

```text
gNB -> AMF: NG Setup Request
AMF -> gNB: NG Setup Response
```

NG Setup carries information such as the gNB identity, supported Public Land
Mobile Network (PLMN), Tracking Area Code (TAC), and supported slice.

The NG Setup Response proves that:

- Next Generation Application Protocol (NGAP) is working;
- the AMF accepts this gNB;
- the advertised serving information is compatible.

It still does not prove that a UE can authenticate.

## Procedure 2: Cell Selection And Access Connection

The UERANSIM User Equipment (UE) searches for a matching simulated gNB.

The UE considers:

- its home or selected PLMN;
- cells it can discover through `gnbSearchList`;
- the cell's suitability;
- the Tracking Area Identity (TAI);
- access conditions.

After selecting a cell, UERANSIM reports Radio Resource Control (RRC)
connection establishment.

In the simulated environment:

```text
UE -> RRC Setup Request -> gNB
gNB/UE complete simulated RRC establishment
UE state becomes RRC-CONNECTED
```

RRC success proves access-side signalling between the simulated UE and gNB. It
does not prove the core accepts the UE.

## Procedure 3: Initial Registration

The UE creates a Non-Access-Stratum (NAS) Registration Request.

```text
UE
  -> NAS Registration Request
  -> gNB
  -> NGAP Initial UE Message containing NAS-PDU
  -> AMF
```

The gNB does not terminate the NAS registration procedure. It relays the NAS
payload. The AMF terminates NAS and creates the serving UE control context.

The Registration Request can include:

- registration type;
- Subscription Concealed Identifier (SUCI) or another UE identity;
- UE security capabilities;
- requested slice information;
- access and mobility information.

Registration has started, but the UE is not yet authenticated or admitted.

## Procedure 4: 5G-AKA Authentication

5G Authentication and Key Agreement (5G-AKA) checks that the UE and subscriber
system possess matching authentication material.

The simplified service path is:

```text
AMF -> Authentication Server Function (AUSF)
       -> Unified Data Management (UDM)
          -> Unified Data Repository (UDR)
             -> MongoDB subscriber record
```

The message path visible toward the UE is:

```text
Network -> UE: Authentication Request with RAND and AUTN
UE -> Network: Authentication Response with RES*
Network: compare UE response with expected result
```

Terms:

- RAND is the Random Challenge.
- AUTN is the Authentication Token.
- RES* is the 5G authentication response calculated by the UE.
- XRES* is the expected 5G authentication response on the network side.
- SQN is the Sequence Number used for freshness.

The permanent authentication key is never transmitted.

### Resynchronization observed in the lab

One earlier successful run first produced an authentication synchronization
failure:

```text
Authentication Request
  -> UE reports SQN freshness problem
  -> core resynchronizes sequence state
  -> second Authentication Request
  -> Authentication Response succeeds
```

This is a defined recovery path. The later security and registration messages
prove the final outcome succeeded.

## Procedure 5: NAS Security

After authentication establishes key material, the AMF sends a Security Mode
Command.

The procedure:

```text
AMF -> UE: Security Mode Command
UE -> AMF: Security Mode Complete
```

NAS security can provide:

- integrity protection, which detects unauthorized modification;
- ciphering, which provides confidentiality when enabled;
- replay protection using counters and security context.

The baseline selected integrity algorithm IA2 and null ciphering. Null
ciphering is acceptable for this isolated analysis baseline but does not
provide NAS confidentiality.

After security activation, Wireshark may identify the NAS security wrapper
without decoding the complete inner message unless the necessary session keys
are supplied.

## Procedure 6: Registration Acceptance

After authentication and security:

```text
AMF -> UE: Registration Accept
UE -> AMF: Registration Complete
```

Registration Accept admits the UE and can provide:

- a temporary 5G Globally Unique Temporary UE Identity (5G-GUTI);
- registration-area information;
- allowed slice information;
- timers and serving context.

Registration Complete confirms the UE received and accepted the registration
context.

At this point:

```text
UE registered = yes
PDU session   = not necessarily
Internet      = not yet proven
```

## Procedure 7: PDU-Session Request

The UE requests a Protocol Data Unit (PDU) session.

Its request includes or implies:

- PDU Session ID;
- Data Network Name (DNN), `internet` in this lab;
- session type, IPv4 in this lab;
- Single Network Slice Selection Assistance Information (S-NSSAI);
- session-management capabilities.

The NAS request follows the logical N1 relationship through the gNB and AMF.
The AMF coordinates session handling with the Session Management Function
(SMF).

The SMF checks whether:

- the requested DNN is supported and authorized;
- the slice is compatible;
- the session type is supported;
- a suitable UPF can serve the session;
- policy and subscriber information permit the session.

Registration can remain successful even if this separate session request
fails.

## Procedure 8: PFCP Programming Of The UPF

The SMF controls the User Plane Function (UPF) using Packet Forwarding Control
Protocol (PFCP) over N4.

The observed exchange:

```text
SMF -> UPF: PFCP Session Establishment Request
UPF -> SMF: PFCP Session Establishment Response
```

PFCP rules can include:

| Acronym | Full name | Responsibility |
| --- | --- | --- |
| PDR | Packet Detection Rule | Identifies traffic belonging to a session |
| FAR | Forwarding Action Rule | Specifies forwarding, dropping, buffering, or related action |
| QER | QoS Enforcement Rule | Supplies Quality of Service enforcement parameters |
| URR | Usage Reporting Rule | Defines usage measurement and reporting behavior |
| F-TEID | Fully Qualified Tunnel Endpoint Identifier | Identifies an IP address and GTP-U tunnel endpoint |

PFCP installs forwarding state. It does not carry the UE's data payload.

## Procedure 9: N3 Resource Setup

The core and gNB exchange tunnel information needed for the access-side user
plane:

```text
AMF -> gNB: PDU Session Resource Setup Request
gNB -> AMF: PDU Session Resource Setup Response
```

This is an NGAP procedure on N2. It coordinates the gNB's side of N3.

After the gNB supplies its tunnel information, the SMF can update the UPF:

```text
SMF -> UPF: PFCP Session Modification Request
UPF -> SMF: PFCP Session Modification Response
```

This completes the required directional forwarding state.

## Procedure 10: PDU-Session Acceptance And UE Interface

The UE receives PDU Session Establishment Accept through protected NAS.

UERANSIM then creates:

- a Linux network namespace for the simulated UE;
- `uesimtun0`, a Tunnel (TUN) interface;
- an assigned UE IPv4 address such as `10.45.0.2`;
- a default route through `uesimtun0`.

The TUN interface presents IP packets to a user-space program. UERANSIM reads
those packets and sends them through its simulated UE/gNB path.

The namespace keeps the UE network separate from the root namespace where the
core and UPF run.

## Procedure 11: Uplink User Packet

For an ICMP Echo Request:

```text
1. ping creates inner packet 10.45.0.2 -> 8.8.8.8.
2. UE namespace routes it to uesimtun0.
3. UERANSIM carries it from UE to gNB.
4. gNB adds GTP-U, UDP, and outer IP headers.
5. N3 packet travels 127.0.0.1 -> 127.0.0.7.
6. UPF matches the TEID and PFCP rules.
7. UPF removes the N3 wrapper.
8. Plain inner IP packet is forwarded toward N6.
9. Linux NAT changes the private UE source to the host's external address.
10. Packet reaches 8.8.8.8.
```

The Tunnel Endpoint Identifier (TEID) lets the UPF map the received GTP-U
packet to the correct tunnel and session context.

## Procedure 12: Downlink User Packet

For the ICMP Echo Reply:

```text
1. Reply returns to the translated host address.
2. Linux connection tracking reverses NAT.
3. Destination becomes the UE address 10.45.0.2.
4. Packet reaches the UPF through the UE-side data path.
5. UPF matches PFCP downlink state.
6. UPF adds the downlink GTP-U wrapper and TEID.
7. N3 packet travels 127.0.0.7 -> 127.0.0.1.
8. gNB removes the GTP-U wrapper.
9. UERANSIM delivers the packet through uesimtun0.
10. ping receives the reply inside the UE namespace.
```

Successful bidirectional ping proves much more than registration:

- the session exists;
- N4 control worked;
- N3 tunnelling works in both directions;
- the UPF forwards correctly;
- UE addressing and routing work;
- N6 forwarding and NAT work.

## Procedure 13: Release

When the UE process stops, access and session state can be released.

The successful full capture showed:

- UE Context Release Request;
- UE Context Release Command;
- UE Context Release Complete;
- PFCP Session Modification associated with cleanup;
- SCTP shutdown when the gNB stopped.

Release matters because networks must clean up state and resources, not only
create them.

## One-Page Message Map

| Stage | Main messages or event | Main owner | Proof produced |
| --- | --- | --- | --- |
| N2 transport | SCTP association | gNB and AMF | Transport reaches port `38412` |
| RAN admission | NG Setup Request/Response | gNB and AMF | AMF accepts gNB configuration |
| UE access | RRC connection | UE and gNB | Simulated access connection works |
| Registration start | Registration Request | UE and AMF | UE asks to register |
| Authentication | Authentication Request/Response | AUSF/UDM side and UE | Credentials produce matching response |
| Security | Security Mode Command/Complete | AMF and UE | NAS security context activated |
| Admission | Registration Accept/Complete | AMF and UE | UE is registered |
| Session request | PDU Session Establishment Request | UE, AMF, SMF | UE requests data connectivity |
| UPF control | PFCP Session Establishment | SMF and UPF | Initial forwarding state installed |
| N3 setup | PDU Session Resource Setup | AMF and gNB | Access-side tunnel resource established |
| Final UPF state | PFCP Session Modification | SMF and UPF | Tunnel information completed |
| Session admission | PDU Session Establishment Accept | Core and UE | Data session accepted |
| Data | Bidirectional GTP-U and inner ICMP | gNB and UPF | User traffic crosses N3 and N6 |
| Cleanup | UE Context Release and PFCP cleanup | AMF, gNB, SMF, UPF | State is released |

## Review Questions

1. Why does SCTP success not prove NG Setup success?
2. Why does Registration Accept not prove Internet connectivity?
3. At what stage does the SMF program the UPF?
4. Why are PFCP Session Modification and NGAP PDU Session Resource Setup both
   involved?
5. What extra conditions does a successful bidirectional ping prove?

## Next Document

Continue with
[Packet Analysis and Troubleshooting](06_packet_analysis_and_troubleshooting.md).

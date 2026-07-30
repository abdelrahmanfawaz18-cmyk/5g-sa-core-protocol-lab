# 5G Identifiers And Configuration

## Why Identifiers Matter

The 5G procedures depend on matching configuration contracts. A packet can
reach the correct process and still be rejected because the network,
tracking area, subscriber, slice, or data-network identity is wrong.

Identifiers answer different questions:

```text
Which mobile network?       PLMN
Which tracking area?        TAC and TAI
Which cell and gNB?         NCI and gNB ID
Which subscriber?           SUPI, SUCI, and temporary 5G-GUTI
Which slice?                S-NSSAI
Which data network?         DNN
Which PDU session?          PDU Session ID
Which GTP-U tunnel?         TEID
Which PFCP session?         SEID
```

## Network And Location Identifiers

| Acronym | Full name | Meaning | Baseline |
| --- | --- | --- | --- |
| MCC | Mobile Country Code | Identifies the country portion of a mobile network identity | `999`, a lab/private-use value |
| MNC | Mobile Network Code | Identifies the network within the MCC | `70` |
| PLMN | Public Land Mobile Network | Network identity formed from MCC and MNC | `999-70` |
| TAC | Tracking Area Code | Identifies a tracking area inside a PLMN | `1` |
| TAI | Tracking Area Identity | Combined PLMN and TAC | PLMN `999-70`, TAC `1` |
| NCI | NR Cell Identity | Identifies a New Radio cell | `0x000000010` |
| gNB ID | gNodeB Identifier | Identifies the gNB portion represented within the cell identity model | Configured with length `32` bits |
| GUAMI | Globally Unique AMF Identifier | Identifies an AMF using PLMN, region, set, and pointer fields | Supplied through the AMF configuration |

### PLMN

The Public Land Mobile Network (PLMN) is constructed from:

```text
PLMN = Mobile Country Code + Mobile Network Code
PLMN = 999 + 70
```

The length of the Mobile Network Code matters. `70` and `070` are different
values.

The PLMN must be consistent across the core's served network, gNB, UE home
identity, and synthetic subscriber identity.

### TAC And TAI

The Tracking Area Code (TAC) is meaningful within a PLMN. Together they form a
Tracking Area Identity (TAI):

```text
TAI = PLMN + TAC
```

The AMF advertises or accepts supported tracking areas. A gNB that presents an
unsupported TAI can fail during access-network setup or later UE handling.

### Cell And AMF Identity

The NR Cell Identity (NCI) identifies a cell in the New Radio access network.
The Globally Unique AMF Identifier (GUAMI) identifies the serving AMF using:

- PLMN identity;
- AMF Region ID;
- AMF Set ID;
- AMF Pointer.

A temporary UE identity can contain information derived from the serving AMF
identity so the network can route later signalling appropriately.

## Subscriber Identities

| Acronym | Full name | Purpose | Visibility |
| --- | --- | --- | --- |
| SUPI | Subscription Permanent Identifier | Permanent identity of the subscription | Stored by UE/subscriber system; protected where possible |
| IMSI | International Mobile Subscriber Identity | Common SUPI form based on mobile-network digits | Baseline uses a synthetic IMSI |
| SUCI | Subscription Concealed Identifier | Privacy-protected representation of the SUPI | Sent during initial identification when needed |
| 5G-GUTI | 5G Globally Unique Temporary UE Identity | Temporary serving-network identity used after registration | Assigned by the core |

The lab uses:

```text
UERANSIM form: imsi-999700000000001
Database form: 999700000000001
```

The `imsi-` text is a UERANSIM representation prefix. It is not stored as part
of the numeric database IMSI.

The baseline uses Subscription Concealed Identifier (SUCI) protection scheme
`0`, the null scheme, because it is an isolated lab with synthetic data. A
production network should use the appropriate identity-protection design.

## Authentication Material

| Term | Full name | Purpose |
| --- | --- | --- |
| K | Permanent subscriber authentication key | Secret shared by the subscriber side and home subscriber system |
| OP | Operator variant algorithm configuration field | Operator-specific input used by the Milenage authentication algorithm |
| OPc | Derived Operator Code | Subscriber-specific value derived from OP and K |
| SQN | Sequence Number | Protects authentication freshness and helps prevent replay |
| RAND | Random Challenge | Random input sent to the UE during authentication |
| AUTN | Authentication Token | Lets the UE verify freshness and authenticity of the network challenge |
| RES* | 5G authentication Response calculated by the UE | Proves the UE has matching authentication material |
| XRES* | Expected 5G authentication Response | Network-side expected value compared with the UE response |

The UE and core do not send `K` across N1 or N2. They independently derive
results from matching secret material.

Conceptually:

```text
Network side: K + OPc + SQN + RAND -> AUTN and expected response
UE side:      K + OPc + AUTN + RAND -> validation and response

UE response matches expected response -> authentication can succeed
UE response differs                 -> authentication fails
SQN is outside accepted range       -> resynchronization may be attempted
```

The UE YAML field `opType` determines whether the configured `op` value is
interpreted as OP or OPc. The value and its type must both match the
subscriber record.

## Slice Identifiers

| Acronym | Full name | Purpose | Baseline |
| --- | --- | --- | --- |
| NSSAI | Network Slice Selection Assistance Information | Set of slice identifiers available or requested | One slice |
| S-NSSAI | Single Network Slice Selection Assistance Information | Identifies one slice | SST `1`, no SD |
| SST | Slice/Service Type | Indicates the broad service behavior of a slice | `1` |
| SD | Slice Differentiator | Optional value distinguishing slices with the same SST | Omitted |

The S-NSSAI is:

```text
S-NSSAI = SST + optional SD
```

SST `1` without an SD is not automatically identical to SST `1` with an SD
value. The baseline intentionally omits SD everywhere.

Matching slice information is required across:

- UE requested and configured slice;
- gNB supported slice;
- AMF and NSSF slice support;
- SMF and UPF session configuration;
- subscriber authorization.

## Session And User-Plane Identifiers

| Term | Full name | Purpose | Baseline example |
| --- | --- | --- | --- |
| DNN | Data Network Name | Names the external data network requested by the UE | `internet` |
| APN | Access Point Name | Earlier-generation term used by some configuration fields for a similar purpose | UERANSIM YAML field `apn` contains `internet` |
| PDU | Protocol Data Unit | A unit of data exchanged at a protocol layer | IPv4 packet for the baseline session |
| PDU Session ID | Protocol Data Unit Session Identifier | Identifies a UE's PDU session | `1` |
| UE IP address | User Equipment Internet Protocol address | Address assigned for the data session | `10.45.0.2` in the final successful run |
| TEID | Tunnel Endpoint Identifier | Identifies one direction of a GTP-U tunnel at the receiver | Capture-specific; uplink and downlink differ |
| SEID | Session Endpoint Identifier | Identifies a PFCP session endpoint | Assigned during PFCP session creation |
| QFI | QoS Flow Identifier | Identifies a Quality of Service flow within a PDU session | Depends on session policy |
| 5QI | 5G QoS Identifier | References standardized or configured QoS characteristics | Subscriber baseline uses `9` |

### DNN

The Data Network Name (DNN) tells the core which data network the UE wants.
The UERANSIM field is named `apn`, but its value maps to the 5G DNN:

```text
UE apn: internet
Subscriber DNN permission: internet
SMF/UPF data-network configuration: internet
```

The UE can register successfully but still fail to establish a PDU session if
the DNN is unsupported.

### TEID

The Tunnel Endpoint Identifier (TEID) tells a GTP-U receiver which tunnel and
session context should process a packet.

TEIDs are directional:

```text
gNB selects the TEID it expects to receive from UPF
UPF selects the TEID it expects to receive from gNB
```

Therefore, uplink and downlink TEIDs do not need to have the same value.

### SEID

The Session Endpoint Identifier (SEID) belongs to PFCP session control. It
identifies PFCP state between the SMF and UPF. It is not the same as a GTP-U
TEID and does not identify the UE's inner IP packet.

## Addressing And Linux Identifiers

| Item | Baseline | Responsibility |
| --- | --- | --- |
| AMF N2 address | `127.0.0.5` | Receives NGAP over SCTP |
| SMF N4 address | `127.0.0.4` | Sends PFCP control |
| UPF N3/N4 address | `127.0.0.7` | Receives GTP-U and PFCP |
| gNB N2/N3 address | `127.0.0.1` | Sends NGAP and GTP-U |
| UE subnet | `10.45.0.0/16` | Address pool for UE PDU sessions |
| UPF-side gateway | `10.45.0.1` | Address on `ogstun` |
| UE TUN interface | `uesimtun0` | Presents the UE's session as an IP interface |
| UE namespace | `ueransim-999700000000001-internet-psi1` | Isolates the simulated UE network from the host/core |

These IP addresses locate software endpoints. They do not replace 5G
identifiers such as PLMN, SUPI, or DNN.

## Configuration Contracts

| Contract | Values that must agree | Failure area when wrong |
| --- | --- | --- |
| Mobile network | MCC, MNC, PLMN | Cell selection, NG Setup, or registration |
| Tracking area | PLMN and TAC | NG Setup or location acceptance |
| Simulated radio link | gNB `linkIp` and UE `gnbSearchList` | UE cannot find the cell |
| N2 transport | gNB AMF address/port and AMF bind address/port | SCTP association |
| Subscriber identity | UE SUPI/IMSI and database IMSI | Subscriber lookup |
| Authentication | K, OP/OPc, type, and authentication AMF field | 5G-AKA |
| Slice | SST and optional SD across UE, gNB, core, and subscriber | Registration or session selection |
| Data network | UE APN/DNN and subscriber/core DNN | PDU-session establishment |
| N4 | SMF and UPF PFCP endpoints | UPF rule installation |
| N3 | gNB and UPF GTP-U endpoints and TEIDs | User-plane tunnelling |
| UE network | address pool, gateway, routes, forwarding, and NAT | N6 reachability |

## Identifier Conclusions

- A PLMN identifies the mobile network; a TAI combines that PLMN with a
  Tracking Area Code.
- A 5G-GUTI provides a temporary serving identity so the permanent subscriber
  identity is not required in every subsequent procedure.
- A matching SUPI only finds the subscriber; authentication also requires
  matching key, OP/OPc, authentication-management field, and sequence state.
- PDU Session ID identifies the UE session, PFCP SEID identifies an
  SMF-to-UPF control session, and GTP-U TEID identifies a user-plane tunnel
  endpoint.
- DNN selection occurs during session management, so registration can succeed
  before an unsupported DNN is rejected.

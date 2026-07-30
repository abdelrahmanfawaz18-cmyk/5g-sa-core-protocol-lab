# 5G Network Functions

## How To Read A Function Name

A 5G Core function is named for the responsibility it owns. It does not
necessarily perform the entire procedure alone.

For example, the Access and Mobility Management Function (AMF) leads UE
registration, but it requests authentication services from the Authentication
Server Function (AUSF) and subscriber information through the Unified Data
Management (UDM) function.

## Fast Reference

| Component | Full name | Plane | Main responsibility |
| --- | --- | --- | --- |
| UE | User Equipment | Control and user | Represents the subscriber device; originates NAS signalling and user data |
| gNB | gNodeB | Access control and user | Provides 5G radio access and connects the UE to the core |
| AMF | Access and Mobility Management Function | Control | Terminates NAS, manages registration, access, reachability, and mobility |
| AUSF | Authentication Server Function | Control | Supports network-side 5G subscriber authentication |
| UDM | Unified Data Management | Control | Manages subscriber identity, authentication data processing, and subscription services |
| UDR | Unified Data Repository | Control data | Stores and retrieves persistent structured data for core functions |
| NRF | Network Repository Function | Control | Registers available functions and supports service discovery |
| NSSF | Network Slice Selection Function | Control | Assists selection of a suitable network slice |
| PCF | Policy Control Function | Control | Provides policy decisions for access and sessions |
| SMF | Session Management Function | Control | Creates, changes, and releases PDU sessions; controls the UPF |
| UPF | User Plane Function | User | Encapsulates, decapsulates, classifies, and forwards UE packets |
| DN | Data Network | User destination | Provides the external service or network reached through the UPF |

## User Equipment

**Full name:** User Equipment
**Lab process:** UERANSIM `nr-ue`

The User Equipment (UE) represents a phone, modem, sensor, or other subscriber
device.

It is responsible for:

- selecting a suitable mobile network and cell;
- initiating registration;
- responding to authentication challenges;
- activating Non-Access-Stratum (NAS) security;
- requesting a Protocol Data Unit (PDU) session;
- sending and receiving ordinary user IP packets.

The UE contains or is associated with subscription credentials. In a real
device, the permanent authentication key normally resides in a Universal
Subscriber Identity Module (USIM). In this isolated simulator, the lab-only
values are stored in the UERANSIM YAML configuration.

The UE does not control the core. It asks for services, supplies its
capabilities and identity, and follows accepted network configuration.

## gNodeB

**Full name:** next-generation NodeB, normally written gNodeB or gNB
**Lab process:** UERANSIM `nr-gnb`

The gNodeB (gNB) is the 5G base station in the Next Generation Radio Access
Network (NG-RAN).

It is responsible for:

- providing the access-side connection to the UE;
- managing the UE's radio-access context;
- relaying NAS messages between the UE and AMF;
- exchanging NGAP control messages with the AMF;
- establishing the access-side resources for a PDU session;
- adding and removing General Packet Radio Service (GPRS) Tunnelling Protocol
  User Plane (GTP-U) encapsulation for UE user traffic.

The gNB does not validate the subscriber's permanent authentication key. It
transports UE signalling to the AMF, which coordinates authentication through
the core.

The gNB has two important core-facing paths:

```text
N2 control: gNB <-> AMF
N3 user:    gNB <-> UPF
```

## Access And Mobility Management Function

**Full name:** Access and Mobility Management Function
**Acronym:** AMF
**Lab service:** `open5gs-amfd`

The AMF is the main control-plane contact for a UE after its NAS messages enter
the core.

It is responsible for:

- accepting or rejecting a gNB's NG Setup procedure;
- terminating the UE's logical N1 NAS connection;
- managing initial registration and later registration updates;
- maintaining UE reachability and connection state;
- coordinating authentication and NAS security;
- tracking the UE's registered area and temporary identity;
- selecting or contacting functions needed for slice and session handling;
- carrying session-management NAS messages between the UE and SMF side.

The AMF does not forward the UE's ping packets. Its work creates and maintains
control state.

### Important name collision

The UERANSIM UE configuration also contains a lowercase `amf` authentication
field. In that context, AMF means **Authentication Management Field**, a
two-octet value used during authentication.

```text
AMF network function          = Access and Mobility Management Function
UE YAML authentication `amf` = Authentication Management Field
```

They are unrelated despite using the same letters.

## Authentication Server Function

**Full name:** Authentication Server Function
**Acronym:** AUSF
**Lab service:** `open5gs-ausfd`

The AUSF provides the authentication service used by the serving network. It
works with the AMF and UDM during procedures such as 5G Authentication and Key
Agreement (5G-AKA).

Conceptually, it:

- receives an authentication request associated with a subscriber;
- obtains authentication material through UDM services;
- provides the serving side of the authentication procedure;
- verifies the UE's calculated response against the expected response;
- contributes to the authentication result and key hierarchy.

The permanent subscriber key is not sent to the AMF, gNB, or across the
network. The UE and home-side subscriber system independently calculate
matching results.

## Unified Data Management

**Full name:** Unified Data Management
**Acronym:** UDM
**Lab service:** `open5gs-udmd`

The UDM provides services derived from subscriber information.

Its responsibilities include:

- handling permanent subscriber identity information;
- supplying authentication-related data to the AUSF;
- supplying subscription information to serving functions;
- managing subscriber-related state required by core procedures.

The UDM is not simply the database. It is a network function that applies
subscriber-management logic and obtains persistent records through the UDR.

## Unified Data Repository

**Full name:** Unified Data Repository
**Acronym:** UDR
**Lab service:** `open5gs-udrd`

The UDR provides structured persistent data to functions such as the UDM and
Policy Control Function (PCF).

In this lab:

```text
UDM or PCF -> UDR service -> MongoDB
```

MongoDB is the storage engine. The UDR is the 5G Core function that exposes
the relevant repository services. Other core functions should not be thought
of as directly querying arbitrary database tables during normal 5G service
communication.

## Network Repository Function

**Full name:** Network Repository Function
**Acronym:** NRF
**Lab service:** `open5gs-nrfd`

The NRF acts as a service registry for the 5G Service-Based Architecture
(SBA).

It supports:

- Network Function (NF) registration;
- NF availability and profile information;
- discovery of a suitable function that provides a required service.

The NRF is similar to a directory, not the central processor of every packet.
If the AMF needs an available AUSF or SMF, service discovery can help it locate
one. The actual service request then goes to the selected function.

## Network Slice Selection Function

**Full name:** Network Slice Selection Function
**Acronym:** NSSF
**Lab service:** `open5gs-nssfd`

The NSSF assists with selecting a network slice suitable for the UE and
serving area.

A network slice is identified using Single Network Slice Selection Assistance
Information (S-NSSAI), which contains:

- Slice/Service Type (SST);
- optional Slice Differentiator (SD).

The baseline uses SST `1` without an SD. A single-slice lab still needs
consistent slice values across the UE, gNB, AMF, NSSF, SMF, and subscriber
profile.

## Policy Control Function

**Full name:** Policy Control Function
**Acronym:** PCF
**Lab service:** `open5gs-pcfd`

The PCF supplies policy decisions to other control-plane functions.

Policy can influence:

- session handling;
- authorized service characteristics;
- Quality of Service (QoS);
- traffic control decisions;
- access and mobility policy.

The PCF decides policy; it does not directly forward UE packets. The SMF turns
relevant session policy into control actions, including rules installed in the
UPF.

## Session Management Function

**Full name:** Session Management Function
**Acronym:** SMF
**Lab service:** `open5gs-smfd`

The SMF manages the lifecycle of a PDU session.

It is responsible for:

- handling session establishment, modification, and release;
- checking requested Data Network Name (DNN), slice, and session type;
- selecting a UPF;
- allocating or coordinating the UE address;
- controlling the UPF through Packet Forwarding Control Protocol (PFCP);
- coordinating N3 tunnel information with the AMF and gNB side;
- supplying session parameters returned to the UE.

The SMF controls forwarding state but does not carry the user's payload.

## User Plane Function

**Full name:** User Plane Function
**Acronym:** UPF
**Lab service:** `open5gs-upfd`

The UPF is the packet-forwarding function of the 5G Core.

It is responsible for:

- receiving GTP-U packets from the gNB on N3;
- matching packets to PFCP-programmed rules;
- removing the GTP-U wrapper on uplink traffic;
- forwarding inner IP packets toward N6;
- receiving downlink IP packets;
- adding the correct downlink GTP-U wrapper;
- forwarding the result to the gNB;
- supporting packet detection, forwarding, usage, and QoS-related behavior
  when configured.

The UPF is the boundary between the mobile tunnel and the external data
network.

## Data Network

**Full name:** Data Network
**Acronym:** DN

The Data Network is the destination network reached through the UPF. It could
be:

- the public Internet;
- a private enterprise network;
- an edge-computing network;
- a network hosting a specific service.

In the successful lab test, `8.8.8.8` is an external endpoint in the data
network. Linux routing and Network Address Translation (NAT) connect the
private UE subnet to the host's external network.

## Responsibility Boundaries

| Question | Function primarily responsible |
| --- | --- |
| Can this gNB join the core? | AMF |
| Is this UE registered and reachable? | AMF |
| Does this UE prove possession of matching credentials? | AUSF and UDM, coordinated by AMF |
| Where is persistent subscription data obtained? | UDR backed by MongoDB |
| Which slice can serve this UE? | AMF with NSSF assistance |
| Which policy should affect this session? | PCF |
| Can a PDU session be created for this DNN? | SMF |
| Which forwarding rules should the UPF use? | SMF |
| Which core function carries the UE's ping packet? | UPF |
| Which node encapsulates the uplink packet before N3? | gNB |

## Responsibility Boundaries

- UDM implements subscriber-management logic; UDR provides the persistent data
  interface backed by MongoDB.
- SMF controls sessions through PFCP; UPF performs packet forwarding.
- AMF terminates NAS signalling and coordinates registration.
- A post-registration PDU-session rejection begins with SMF, DNN, slice, and
  subscriber session authorization evidence.
- Authentication failures require correlation across UE, AMF, AUSF, UDM, UDR,
  and the synthetic subscriber record.

# 5G Core Concepts

For a complete beginner-oriented learning path, start with the
[5G Standalone learning handbook](learning/README.md). It expands this summary
into architecture maps, reference tables, procedure walkthroughs, and an
acronym glossary.

## Control Plane and User Plane

The control plane decides how a UE connects, authenticates, registers, and receives a data session. The user plane carries the UE's application packets after the session has been established.

In this lab, the AMF, SMF, AUSF, UDM, UDR, PCF, NSSF, and NRF are control-plane functions. The UPF is the user-plane function.

## NRF

The Network Repository Function is the service registry for the 5G Core. Open5GS control-plane functions register with the NRF and use it to discover other available network functions.

## AMF

The Access and Mobility Management Function handles gNB connectivity, UE registration, mobility management, and NAS signalling. The UERANSIM gNB will later connect to the AMF over N2 using NGAP over SCTP.

## SMF

The Session Management Function creates and manages PDU sessions. It selects and controls the UPF over N4 using PFCP and provides the session information needed to build the UE data path.

## UPF

The User Plane Function forwards UE packets between the gNB and the external data network. It receives GTP-U traffic over N3, follows forwarding rules installed by the SMF, and sends ordinary IP traffic toward N6.

## AUSF

The Authentication Server Function supports 5G subscriber authentication. It works with the UDM and AMF so the network can verify that a UE has valid lab credentials.

## UDM

The Unified Data Management function manages subscriber identity and authentication-related information used by other 5G Core functions. It obtains persistent subscriber data through the UDR.

## UDR

The Unified Data Repository provides persistent data used by functions such as the UDM and PCF. In this Open5GS installation, that data is backed by MongoDB.

## PCF

The Policy Control Function supplies policy decisions for sessions and subscribers. The SMF can use these decisions when determining how a PDU session should be handled.

## NSSF

The Network Slice Selection Function helps select an appropriate network slice for a UE. The first version of this lab will use one basic S-NSSAI rather than a multi-slice deployment.

## Key Interfaces

| Interface | Connection | Protocol | Purpose |
|---|---|---|---|
| N2 | gNB to AMF | NGAP over SCTP | RAN and core control signalling |
| N3 | gNB to UPF | GTP-U over UDP | Encapsulated UE user traffic |
| N4 | SMF to UPF | PFCP over UDP | User-plane session control |
| N6 | UPF to data network | IP | Traffic entering or leaving the mobile core |
| SBI | 5G Core control functions | HTTP-based service APIs | Registration, discovery, and service communication |

## Lab Data Path

```text
UERANSIM UE
    |
UERANSIM gNB
    | \
    |  \ N3: GTP-U/UDP
    |   \
    |    v
    |   Open5GS UPF ---- N6: IP ---- Data network
    |          ^
    |          |
    |          | N4: PFCP/UDP
    v          |
Open5GS AMF -- Open5GS SMF
 N2: NGAP/SCTP
```

## Reference

- [Open5GS Quickstart](https://open5gs.org/open5gs/docs/guide/01-quickstart/)

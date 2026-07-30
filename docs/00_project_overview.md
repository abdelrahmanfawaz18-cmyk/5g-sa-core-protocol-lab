# Project Overview

## Scope

This project is a complete local 5G Standalone protocol lab. Open5GS provides
the 5G Core, UERANSIM provides a simulated gNodeB and User Equipment, Linux
provides the local routing and isolation mechanisms, and Wireshark/tshark
provide packet-level evidence.

The validated baseline demonstrates:

- gNB SCTP association and NG Setup with the AMF;
- synthetic UE authentication and NAS security;
- successful UE registration;
- IPv4 PDU-session establishment;
- PFCP control between SMF and UPF;
- bidirectional GTP-U traffic between gNB and UPF;
- N6 forwarding and Network Address Translation;
- end-to-end ICMP traffic from an isolated UE namespace;
- five controlled fault experiments with recovery evidence;
- automated read-only validation with Python.

## System Model

```text
UERANSIM UE
  -> simulated radio link
  -> UERANSIM gNB
      -> N2 NGAP/SCTP -> Open5GS AMF and control-plane functions
      -> N3 GTP-U     -> Open5GS UPF
                            -> N6 IP -> Data Network
                 Open5GS SMF -> N4 PFCP -> Open5GS UPF
```

The simulated UE behaves as a protocol endpoint, the simulated gNB connects
the access and core sides, and the UPF carries the UE's IP traffic. The AMF
manages access and registration state but does not forward user packets.

## Evidence Model

The project correlates three evidence sources:

1. UERANSIM and Open5GS logs explain component decisions.
2. Packet captures prove message exchange and protocol layering.
3. Linux interfaces, namespaces, routes, forwarding, and NAT prove the local
   user-plane path.

No single source is treated as sufficient when a procedure crosses multiple
functions or interfaces.

## Boundaries

This is a single-host protocol lab, not a commercial mobile network. UERANSIM
does not implement a complete over-the-air New Radio physical layer, and the
external data-network test uses ordinary IP connectivity from the host.

## Lab-Only Data Rule

Only synthetic subscriber and network information belongs in the repository.
Production identities, authentication material, tokens, private credentials,
and unrelated packet traffic must not be committed.

# Registration Validation Report

## Result

**COMPLETE:** One synthetic UE successfully registered through the UERANSIM
gNB with the Open5GS core.

## Verification Gate

| Requirement | Evidence | Result |
| --- | --- | --- |
| One UE registers | UERANSIM `RM-REGISTERED` and AMF `Registration complete` | Pass |
| Success image | `screenshots/successful_registration.png` | Pass |
| Pcap or tshark summary | N2 pcap and concise tshark summary | Pass |
| Message-by-message explanation | `docs/03_successful_registration_flow.md` | Pass |

## gNB Evidence

The gNB reported:

```text
SCTP connection established (127.0.0.5:38412)
Sending NG Setup Request
NG Setup Response received
NG Setup procedure is successful
```

The AMF independently recorded:

```text
gNB-N2 accepted[127.0.0.1]
```

## UE Evidence

The UERANSIM control interface reported:

```text
cm-state: CM-CONNECTED
rm-state: RM-REGISTERED
mm-state: MM-REGISTERED/NORMAL-SERVICE
5u-state: 5U1-UPDATED
selected-plmn: 999/70
current-tac: 1
```

The UE output showed:

```text
Security Mode Command received
Registration accept received
Sending Registration Complete
Initial Registration is successful
```

The AMF independently logged `Registration complete` for the matching
synthetic subscriber.

## Authentication Detail

The first authentication challenge caused a sequence-number synchronization
failure. The capture then shows:

1. Authentication Failure with synchronization-failure cause.
2. A second Authentication Request.
3. Authentication Response.
4. Security Mode Command.
5. Protected registration completion messages.

This is the protocol-defined resynchronization path. The final registered
state proves that the recovery succeeded.

## Packet Evidence

| Property | Verified value |
| --- | --- |
| Capture | `captures/successful/n2_registration_attempt.pcap` |
| Format | pcap, Linux cooked-mode v2 |
| Size | 27 kB |
| Packets | 210 |
| Filter | SCTP port `38412` |
| Endpoints | `127.0.0.1` and `127.0.0.5` only |
| SHA-256 | `65a30ad812db1f639bb1ca164b0e78908095ed8cf0a2e0535f5d1086fe41b901` |

The capture was reviewed before intentional inclusion. It contains only local
N2 traffic and synthetic lab identity data.

## Cleanup

After evidence collection:

- packet capture was stopped;
- UE was stopped;
- gNB was stopped;
- the temporary `uesimtun0` interface was removed automatically;
- MongoDB and Open5GS remained active as background services.

## Result Separation

The same run automatically requested an initial PDU session after
registration. Registration and session success remain separate results. The
[PDU-session validation report](user_plane_validation.md) independently proves
session state, N3 tunnelling, UE routing, and traffic through the UPF.

The registration evidence therefore remains valid without relying on a later
user-plane outcome.

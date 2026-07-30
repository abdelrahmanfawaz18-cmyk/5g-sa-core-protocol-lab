# User-Plane Validation Report

## Result

**COMPLETE:** The synthetic UE established an IPv4 PDU session and passed
bidirectional user-plane traffic through the Open5GS UPF.

## Verification Gate

| Requirement | Evidence | Result |
| --- | --- | --- |
| PDU session established | UERANSIM reported success for PSI `1` | Pass |
| UE has an address and tunnel | Namespace report shows `uesimtun0` with `10.45.0.4` | Pass |
| Ping or equivalent works | Five replies from `8.8.8.8`, `0%` loss | Pass |
| PFCP visible | Session Establishment and Modification exchanges in the reviewed capture | Pass |
| GTP-U visible | Five uplink requests and five downlink replies in GTP-U | Pass |
| Flow documented | `docs/04_pdu_session_flow.md` | Pass |

## Session Evidence

UERANSIM reported:

```text
PDU Session Establishment Accept received
PDU Session establishment is successful PSI[1]
Connection setup for PDU session[1] is successful
TUN interface[uesimtun0, 10.45.0.4] is up
```

The verified session used:

| Property | Value |
| --- | --- |
| PDU type | IPv4 |
| DNN | `internet` |
| Slice | SST `1`, no SD |
| UE address | `10.45.0.4` |
| UE namespace | `ueransim-999700000000001-internet-psi1` |

## Connectivity Evidence

The UE namespace sent five ICMP echo requests to `8.8.8.8` and received all
five replies:

```text
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max/mdev = 17.346/19.649/23.604/2.355 ms
```

Evidence:

- `screenshots/ping_success.png`
- `reports/ue_interface_success.md`

## Protocol Evidence

The reviewed capture contains 49 selected packets:

| Protocol evidence | Frames |
| --- | ---: |
| NGAP | 11 |
| PFCP | 6 |
| GTP-U | 10 |
| GTP-U ICMP requests | 5 |
| GTP-U ICMP replies | 5 |

The PFCP exchange proves that the SMF programmed the UPF. The bidirectional
GTP-U ICMP exchange proves that N3 carried the user traffic between gNB and
UPF. The plain ICMP copies show decapsulation, N6 forwarding, address
translation, and the reverse path.

## Evidence Review

| Property | Verified value |
| --- | --- |
| Capture | `captures/successful/pdu_session_and_user_plane.pcap` |
| Format | pcap, Linux cooked-mode v2 |
| Size | `7645` bytes |
| Packets | `49` |
| SHA-256 | `6040d3e54f79926d9ae2db70664fc1342d98716ab5c9ec00e147dae079ee81f7` |

The full local capture was reduced to the relevant setup and successful data
windows. The reviewed file contains synthetic lab identity data, local lab
addresses, the private host and gateway addresses involved in translation,
and the public ping target. Unrelated heartbeats and background traffic were
removed before inclusion.

## Network Design Detail

UERANSIM places `uesimtun0` in a dedicated Linux network namespace. This
prevents a same-host route collision between the simulated UE and the
co-located Open5GS UPF.

The successful run used normal Linux forwarding and masquerading. Temporary
diagnostic source-routing rules were removed before the final test.

The network rules are runtime-only and must be restored with
`scripts/network/enable_ue_nat.sh` after a reboot.

## Cleanup

After the test:

- packet capture was stopped;
- UE was stopped and its namespace was removed;
- gNB was stopped;
- Open5GS and MongoDB remained background services.

## Related Analysis

The [packet-capture guide](../docs/05_packet_capture_guide.md) provides the
complete NGAP, NAS-5GS, PFCP, GTP-U, inner-IP, and ICMP interpretation for the
reviewed lifecycle capture.

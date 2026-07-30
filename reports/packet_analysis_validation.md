# Packet-Analysis Validation Report

## Result

**COMPLETE:** One continuous successful 5G SA lifecycle was captured,
reviewed, summarized, and interpreted with tshark and Wireshark.

## Verification Gate

| Requirement | Evidence | Result |
| --- | --- | --- |
| Produce packet summaries with tshark | Registration and PDU-session summaries | Pass |
| README shows protocol filters | Packet Analysis Quick Reference | Pass |
| README shows Wireshark images | NGAP/NAS and PFCP/GTP-U images | Pass |
| Explain control plane versus user plane | `docs/05_packet_capture_guide.md` | Pass |

## Successful Run

The run included:

1. SCTP association establishment.
2. NG Setup.
3. UE registration and authentication.
4. NAS security activation.
5. PDU-session establishment.
6. PFCP session establishment and modification.
7. Five bidirectional GTP-U/ICMP exchanges.
8. UE context release.
9. PFCP cleanup.
10. SCTP shutdown.

The UE used IPv4 address `10.45.0.2` in namespace
`ueransim-999700000000001-internet-psi1`.

The Internet connectivity result was:

```text
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max/mdev = 21.483/23.684/26.519/1.803 ms
```

## Capture Properties

| Property | Verified value |
| --- | --- |
| File | `captures/successful/full_successful_run.pcap` |
| Format | pcap, Linux cooked-mode v2 |
| Reviewed packets | `64` |
| File size | `9512` bytes |
| Duration | `555.066027` seconds |
| Strict timestamp order | Yes |
| SHA-256 | `011d538635fe836c4ee50dcb011e3d46e53fd875baa7980c499829da912d2a97` |

The local raw capture recorded 715 packets with zero kernel drops. Periodic
heartbeats and unrelated background ICMP were removed before inclusion.

## Protocol Counts

| Display filter | Frames |
| --- | ---: |
| `sctp` | 28 |
| `ngap` | 16 |
| `nas-5gs` | 9 |
| `pfcp` | 6 |
| `gtp` | 10 |
| `gtp && icmp.type == 8` | 5 |
| `gtp && icmp.type == 0` | 5 |
| `icmp && !gtp` | 20 |

## Required Evidence

- `captures/successful/full_successful_run.pcap`
- `captures/successful/registration_summary.txt`
- `captures/successful/pdu_session_summary.txt`
- `screenshots/wireshark_ngap_nas.png`
- `screenshots/wireshark_pfcp_gtpu.png`
- `docs/05_packet_capture_guide.md`

## Evidence Review

The capture and images contain synthetic lab values only. The screenshots show
only Wireshark, the reviewed capture filename, protocol filters, packet rows,
and decoded fields. No unrelated desktop content or personal filesystem path
is visible.

## Related Failure Evidence

The [controlled-failure guide](../docs/06_failure_scenario_guide.md) and
[`captures/failures/`](../captures/failures/README.md) compare five isolated
faults with this successful capture baseline.

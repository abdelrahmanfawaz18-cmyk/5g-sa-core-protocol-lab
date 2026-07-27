# Packet Captures

This directory contains reviewed packet-capture evidence from successful and
failed lab scenarios.

Raw `.pcap` and `.pcapng` files are ignored by default. A capture must be reviewed for lab-only identifiers, secrets, unrelated traffic, and file size before it is intentionally added.

## Successful Registration

`successful/n2_registration_attempt.pcap` is the Phase 6 N2 capture.

It contains only SCTP traffic between the local gNB address `127.0.0.1` and
AMF address `127.0.0.5` on port `38412`. The identities are synthetic lab
values. The capture is intentionally included after endpoint, protocol, size,
and identity review.

See `reports/phase_6_tshark_summary.txt` for a concise text interpretation.

## PDU Session And User Plane

`successful/pdu_session_and_user_plane.pcap` is the reviewed Phase 7 capture.

It contains the relevant registration and PDU-session setup window, followed
by five successful ICMP exchanges. The evidence includes NGAP, PFCP,
bidirectional GTP-U, and the plain N6-side ICMP packets.

The capture was reduced from the full local recording before inclusion.
Unrelated heartbeats and background traffic were removed. The retained values
are synthetic lab identity data, local lab addresses, the private host and
gateway addresses involved in translation, and the public ping target.

See `reports/phase_7_tshark_summary.txt` for the verified frame mapping,
protocol counts, tunnel directions, and file hash.

## Full Successful Lifecycle

`successful/full_successful_run.pcap` is the Phase 8 analysis capture. It
contains the reviewed lifecycle from SCTP association and NG Setup through
registration, PDU-session establishment, bidirectional GTP-U traffic, UE
context release, and SCTP shutdown.

Supporting summaries:

- `successful/registration_summary.txt`
- `successful/pdu_session_summary.txt`

The local raw capture contained 715 packets with zero kernel drops. Periodic
keepalives and unrelated background ICMP were removed, leaving 64 relevant
packets in strict timestamp order.

See `docs/05_packet_capture_guide.md` for commands, filters, frame landmarks,
and interpretation.

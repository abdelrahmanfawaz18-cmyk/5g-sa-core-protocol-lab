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

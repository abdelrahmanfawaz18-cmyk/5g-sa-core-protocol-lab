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

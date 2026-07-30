# Screenshots

This directory contains selected technical evidence from successful
procedures and troubleshooting scenarios.

Screenshots must be reviewed to remove unrelated windows, personal information, real identifiers, and secrets before they are added.

`successful_registration.png` shows the UERANSIM registration result.
It was cropped to the simulator output and reviewed before inclusion.

`ping_success.png` shows the UE-side connectivity result: five ICMP
replies from `8.8.8.8` with no packet loss. It was cropped to the terminal
result and reviewed before inclusion.

`wireshark_ngap_nas.png` shows the `ngap || nas-5gs` display filter, the
registration timeline, and frame 9 decoded as an NGAP Initial UE Message
carrying a NAS-5GS Registration Request.

`wireshark_pfcp_gtpu.png` shows the `pfcp || gtp` display filter, PFCP session
setup, all five GTP-U echo request/reply pairs, and the outer IP, UDP port,
TEID, inner IP, and ICMP layers of the first uplink packet.

Both Wireshark images show only the reviewed lab capture and synthetic
technical values.

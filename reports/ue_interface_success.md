# UE Interface and Connectivity Success

## Result

**PASS:** On 2026-07-25, the synthetic UE established PDU Session `1`, received
IPv4 address `10.45.0.4`, and exchanged five ICMP echo requests and replies
with `8.8.8.8`.

## Session Contract

| Property | Verified value |
| --- | --- |
| Session type | IPv4 |
| DNN/APN | `internet` |
| S-NSSAI | SST `1`, no SD |
| PDU Session Identity | `1` |
| UE IPv4 address in this run | `10.45.0.4` |
| UPF subnet and gateway | `10.45.0.0/16`, gateway `10.45.0.1` |

The UE, subscriber, SMF, and UPF values agree. Open5GS allocates the UE address
dynamically, so a later run can receive a different address from the same
subnet.

## Linux Network Namespace

UERANSIM created:

```text
ueransim-999700000000001-internet-psi1
```

The namespace isolates the simulated UE from the co-located core host. Without
this separation, Linux can treat the UE address as one of the host's own
addresses instead of forwarding packets through the UPF.

The live interface inspection showed:

```text
lo          UNKNOWN  127.0.0.1/8 ::1/128
uesimtun0   UNKNOWN  10.45.0.4/24 fe80::fb30:3eb5:4bb2:a915/64
```

`UNKNOWN` is normal for this TUN interface. A TUN device is a software
interface and does not have the physical carrier state reported by an Ethernet
interface. UERANSIM reported the PDU session and TUN connection as successful.

## Routing Table

The routing table inside the UE namespace was:

```text
default dev uesimtun0 scope link
10.45.0.0/24 dev uesimtun0 proto kernel scope link src 10.45.0.4
```

The connected route covers the UE-side tunnel subnet. The default route sends
all other IPv4 traffic into `uesimtun0`, where UERANSIM carries it toward the
gNB.

## Connectivity Test

The command was run inside the UE namespace:

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 ping -c 5 8.8.8.8
```

| Measurement | Result |
| --- | --- |
| Target | `8.8.8.8` |
| Packets transmitted | `5` |
| Packets received | `5` |
| Packet loss | `0%` |
| Minimum RTT | `17.346 ms` |
| Average RTT | `19.649 ms` |
| Maximum RTT | `23.604 ms` |
| RTT variation | `2.355 ms` |

The result is shown in
[`screenshots/ping_success.png`](../screenshots/ping_success.png).

## Packet Evidence

The reviewed capture
[`captures/successful/pdu_session_and_user_plane.pcap`](../captures/successful/pdu_session_and_user_plane.pcap)
contains:

- PFCP Session Establishment Request and Response between SMF and UPF;
- PFCP Session Modification Request and Response;
- NGAP PDU Session Resource Setup Request and Response;
- five uplink GTP-U packets containing ICMP echo requests;
- five downlink GTP-U packets containing ICMP echo replies;
- the corresponding plain ICMP packets before encapsulation, after
  decapsulation, and across N6 after address translation.

The concise frame mapping is in
[`reports/phase_7_tshark_summary.txt`](phase_7_tshark_summary.txt).

## Runtime Network State

IPv4 forwarding and the Phase 7 forwarding and masquerade rules were active.
The temporary same-host diagnostic policy rules were removed, and
`net.ipv4.conf.ogstun.accept_local` was restored to `0` before the successful
run. The successful result therefore used the isolated namespace and standard
forwarding path.

The forwarding and masquerade rules created by `enable_ue_nat.sh` are runtime
settings. Run that helper again after a reboot before repeating UE Internet
connectivity tests.

## Cleanup

After evidence collection, the capture, UE, and gNB were stopped. Stopping the
UE removed its temporary namespace and TUN interface. MongoDB and Open5GS
remain available as background services.

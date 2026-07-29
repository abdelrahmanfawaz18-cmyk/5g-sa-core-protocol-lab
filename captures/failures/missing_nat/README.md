# Missing NAT Scenario

## Status

Complete. The failure was reproduced, captured, explained, reversed, and
retested successfully without restarting the 5G session.

## Purpose

Demonstrate that successful registration, Protocol Data Unit (PDU) session
establishment, Packet Forwarding Control Protocol (PFCP), and General Packet
Radio Service Tunnelling Protocol User Plane (GTP-U) do not guarantee
external return traffic.

NAT means Network Address Translation.

## Known-Good Baseline

Linux forwarding and the scoped masquerade rule translate traffic from UE
subnet `10.45.0.0/16` toward the external network.

## Intentional Change

After confirming a working PDU session and successful external connectivity,
remove only:

```text
-A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE
```

The guarded helper refuses to proceed unless exactly one copy exists and both
scoped forwarding rules and global IPv4 forwarding are active:

[`scripts/failures/remove_ue_nat_rule.sh`](../../../scripts/failures/remove_ue_nat_rule.sh)

Do not disable global forwarding and do not change unrelated network rules.

## Expected Correct Behavior

Five Internet Control Message Protocol (ICMP) Echo Requests receive five Echo
Replies through bidirectional GTP-U.

## Predicted Failure Boundary

Registration and the PDU session remain successful. Uplink traffic traverses
GTP-U to the User Plane Function (UPF) and is forwarded externally with its
private `10.45.0.x` source unchanged. The external network cannot route a
reply directly to that private UE address, so ICMP Echo Replies should be
absent.

## Observed Failure Symptom

The UE remained registered with an active PDU session and address `10.45.0.5`.
After removing only the scoped MASQUERADE rule, its ping produced:

```text
5 packets transmitted, 0 received, 100% packet loss
```

The packet capture still showed all five requests traversing uplink GTP-U,
being decapsulated by the UPF path, and being forwarded externally.

## Last Successful Procedure

Registration, PDU-session establishment, UE tunnel creation, uplink GTP-U,
UPF decapsulation, and Linux forwarding all succeeded.

## First Failed Or Missing Procedure

The forwarded requests retained private source `10.45.0.5`. No external Echo
Reply and no downlink GTP-U reply followed.

## Logs Checked

- UERANSIM UE session output;
- UE namespace address and connectivity result;
- Linux IPv4 forwarding state;
- scoped FORWARD rules;
- NAT POSTROUTING rules;
- failure and recovery packet captures.

The concise operational results are in [`log_summary.txt`](log_summary.txt).

## Packet Capture Evidence

- [`missing_nat.pcap`](missing_nat.pcap): reviewed 15-packet failure path;
- [`recovery.pcap`](recovery.pcap): reviewed 30-packet recovery path;
- [`packet_summary.txt`](packet_summary.txt): per-frame path, hashes, and
  interpretation.

The failure capture contains five GTP-U uplink Echo Requests and externally
forwarded requests, but no reply. The recovery capture contains five complete
bidirectional paths, including translation, reverse translation, and GTP-U
downlink replies.

## Root Cause

The external request retained private source `10.45.0.5` because the scoped
MASQUERADE rule was absent. The external network had no route back to that
isolated UE subnet.

## Fix

Restore the standard UE NAT rule using the repository network helper.

## Recovery Proof

The standard helper restored only the missing MASQUERADE rule while confirming
that forwarding was already intact. Without restarting the UE, gNB, or PDU
session, the same test produced:

```text
5 packets transmitted, 5 received, 0% packet loss
```

## Concise Technical Explanation

Registration and PDU-session establishment prove control-plane and session
setup, but they do not guarantee that an external network can route return
traffic. Here, uplink traffic still crossed N3 in GTP-U, reached the UPF, and
was forwarded by Linux. Without NAT, however, it left with private UE source
`10.45.0.5`, so no reply could return. MASQUERADE rewrote that source to the
host's routable external-interface address and tracked the flow for reverse
translation. Restoring only that rule immediately restored all replies. This
localizes the fault to the N6/Linux return path rather than the 5G control
plane, PFCP, GTP-U, or the PDU session.

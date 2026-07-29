# Missing NAT Scenario

## Status

Planned. Not yet implemented or executed.

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

Remove only the exact UE-subnet masquerade rule after the PDU session exists.
Do not disable global forwarding and do not change unrelated network rules.

## Expected Correct Behavior

Five Internet Control Message Protocol (ICMP) Echo Requests receive five Echo
Replies through bidirectional GTP-U.

## Predicted Failure Boundary

Registration and the PDU session remain successful. Uplink GTP-U reaches the
User Plane Function (UPF), but the external network cannot route a reply
directly to the private UE source address.

## Observed Failure Symptom

Pending.

## Logs Checked

Pending. Relevant evidence includes UE state, UPF state, Linux routes,
forwarding, and NAT rules.

## Packet Capture Evidence

Pending.

## Root Cause

Pending confirmation that only the scoped masquerade rule is absent.

## Fix

Restore the standard UE NAT rule using the repository network helper.

## Recovery Proof

Pending.

## Concise Technical Explanation

Pending.

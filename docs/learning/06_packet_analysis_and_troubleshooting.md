# Packet Analysis And Troubleshooting

## Troubleshooting Goal

Troubleshooting is the process of locating the earliest stage whose observed
behavior differs from the expected behavior.

The main method is:

```text
Known-good baseline
  -> change one variable
  -> identify the last successful event
  -> identify the first failed or missing event
  -> inspect the responsible functions and configuration contract
  -> restore the variable
  -> prove recovery
```

This is stronger than changing several settings until the symptom disappears.

## Start With The Symptom Boundary

| Symptom | What is already proven | First area to inspect |
| --- | --- | --- |
| gNB cannot establish SCTP | Core may be running, but N2 transport is not proven | AMF listener, IP, port, SCTP, process state |
| SCTP works but NG Setup fails | N2 transport works | PLMN, TAC, gNB identity, supported slice, NGAP response |
| NG Setup works but UE sees no cell | gNB-to-core control works | UERANSIM radio-link addresses, UE/gNB PLMN, cell suitability |
| Registration starts but authentication fails | UE access, N2, and subscriber signalling path work | SUPI lookup, K, OP/OPc, SQN, AUSF/UDM/AMF logs |
| Registration succeeds but PDU session fails | Identity, authentication, NAS security, and registration work | DNN, S-NSSAI, session type, SMF, subscriber permission |
| PDU session succeeds but no GTP-U appears | Session signalling worked | N3 resource setup, TEIDs, gNB/UPF endpoints, PFCP rules |
| GTP-U uplink appears but no Internet reply | UE-to-UPF path works | N6 routing, forwarding, NAT, external reachability |
| Uplink works but downlink fails | Some forward path works | Return routing, connection tracking, downlink PFCP rule, downlink TEID |

## The Last-Good, First-Bad Method

Suppose a capture shows:

```text
Registration Request
Authentication Request
Authentication Response
Security Mode Command
Security Mode Complete
Registration Accept
Registration Complete
PDU Session Establishment Request
```

but no PDU Session Establishment Accept appears.

That means:

- cell selection is not the first problem;
- N2 is not the first problem;
- subscriber authentication is not the first problem;
- NAS security is not the first problem;
- registration is not the first problem;
- session management is the first unproven stage.

The investigation should start with the Session Management Function (SMF),
requested Data Network Name (DNN), slice, session type, and subscriber session
authorization.

## Evidence Types

### Positive evidence

Positive evidence is something directly observed:

- an SCTP association completes;
- NG Setup Response is received;
- Registration Accept is reported;
- PFCP Session Establishment Response is present;
- a GTP-U packet contains the expected inner UE address;
- an ICMP Echo Reply is received.

### Negative evidence

Negative evidence is the absence of something that should follow.

Examples:

- Authentication Request appears, but Security Mode Command never follows;
- registration completes, but no PFCP session exchange appears;
- uplink GTP-U Echo Requests appear, but no downlink GTP-U Echo Replies appear.

Absence is meaningful only after checking:

- the capture started before the event;
- the capture filter included the protocol;
- the correct interface was captured;
- encrypted inner signalling was not merely undecodable;
- the observation period was long enough;
- logs do not show the event under a different representation.

## Packet Nesting

Wireshark shows a protocol tree because packets are encapsulated.

### NAS inside NGAP

```text
Linux cooked capture
  -> IPv4
     -> SCTP
        -> NGAP Initial UE Message
           -> NAS-PDU
              -> NAS-5GS Registration Request
```

Interpretation:

- IPv4 and SCTP deliver the packet from gNB process to AMF process.
- NGAP defines the N2 procedure.
- NAS is the UE-originated logical N1 message.

### ICMP inside GTP-U

```text
Linux cooked capture
  -> outer IPv4: gNB to UPF
     -> UDP port 2152
        -> GTP-U and TEID
           -> inner IPv4: UE to data-network endpoint
              -> ICMP Echo Request
```

Interpretation:

- outer addresses identify the N3 tunnel endpoints;
- the TEID identifies a directional tunnel at the receiver;
- inner addresses identify the UE packet and its destination;
- ICMP is the user payload used for the connectivity test.

## Capture And Display Filters

A capture filter decides what is saved. A display filter selects from what was
already saved.

| Purpose | Display filter |
| --- | --- |
| N2 transport | `sctp` |
| gNB and AMF procedures | `ngap` |
| Decodable UE NAS | `nas-5gs` |
| Registration timeline | `ngap || nas-5gs` |
| SMF and UPF control | `pfcp` |
| N3 user tunnel | `gtp` |
| Ping inside N3 | `gtp && icmp` |
| Plain ping outside GTP-U | `icmp && !gtp` |
| Compare UPF control and data | `pfcp || gtp` |

The Phase 7 and Phase 8 focused capture condition was:

```text
sctp port 38412 or udp port 8805 or udp port 2152 or icmp
```

That condition includes:

- SCTP/NGAP on N2;
- PFCP on N4;
- GTP-U on N3;
- ICMP transformations on the data path.

It does not include every Service-Based Interface message.

## Logs And Packets Answer Different Questions

| Evidence source | Strongest use |
| --- | --- |
| UE output | UE state, selected cell, received NAS result, tunnel creation |
| gNB output | SCTP/NGAP connection, NG Setup result, UE access context |
| AMF log | NGAP, registration, identity, mobility, and NAS coordination |
| AUSF log | Authentication service handling |
| UDM log | Subscriber authentication and subscription service behavior |
| UDR log | Persistent subscriber-data service access |
| SMF log | DNN, slice, address, PDU session, and UPF selection |
| UPF log | PFCP state and user-plane context |
| Packet capture | Exact on-wire order, endpoints, protocols, causes, TEIDs, inner/outer headers |
| Configuration | Intended values and matching contracts |

A log can explain an internal decision that a focused capture cannot see. A
packet capture can prove what crossed an interface independently of a
component's summary message. Correlating them is stronger than relying on one
source.

## Protocol-To-Owner Map

| Observed protocol | Main endpoints | First logs to correlate |
| --- | --- | --- |
| SCTP | gNB and AMF | gNB and AMF |
| NGAP | gNB and AMF | gNB and AMF |
| NAS-5GS registration | UE and AMF logically | UE and AMF |
| NAS-5GS authentication | UE and AMF/AUSF side | UE, AMF, AUSF, UDM |
| NAS-5GS session management | UE and SMF side through AMF | UE, AMF, SMF |
| PFCP | SMF and UPF | SMF and UPF |
| GTP-U | gNB and UPF | gNB and UPF |
| Plain IP/ICMP on N6 | UPF/host and Data Network | UPF plus Linux routes, forwarding, NAT |

## Configuration-Contract Method

For each failure, write the matching relationship before checking individual
files.

Example:

```text
UE requested DNN = subscriber permitted DNN = SMF-supported DNN
```

Then compare the observed values. This is clearer than opening several YAML
files without knowing what relationship is being tested.

Other contracts:

```text
gNB PLMN = AMF served PLMN
gNB TAC  = AMF supported TAC
UE SUPI  = subscriber IMSI
UE K/OPc = subscriber K/OPc
SMF N4 destination = UPF PFCP address
gNB N3 endpoint <-> UPF GTP-U endpoint
UE subnet = SMF pool = UPF/ogstun subnet
```

## One-Variable Experiment

A controlled experiment should contain:

1. a successful baseline;
2. one intentional change;
3. a predicted failure boundary;
4. a capture started before the trigger;
5. concise logs;
6. observed last-good and first-bad events;
7. restoration of the changed value;
8. a successful recovery test.

Changing one variable makes the experiment causal:

```text
Baseline works
Only X changes
Failure appears
X is restored
Success returns

Therefore X caused the observed difference, within the controlled test.
```

## Controlled Failure Map

| Intentional mismatch | Expected successful stages | Expected failure boundary | Main evidence |
| --- | --- | --- | --- |
| Wrong gNB PLMN | Core service readiness and possibly SCTP | NG Setup acceptance | NGAP result plus gNB/AMF logs |
| Wrong gNB TAC | Transport and possibly NG Setup | Tracking-area acceptance or UE registration | NGAP/NAS plus gNB/AMF logs |
| Wrong subscriber K or OPc | Cell, RRC, N2, Registration Request | 5G-AKA authentication | NAS plus UE/AMF/AUSF/UDM logs |
| Wrong DNN | Registration and NAS security | PDU-session establishment | NAS, SMF logs, PFCP presence or absence |
| Missing scoped NAT rule | Registration, session, PFCP, and uplink GTP-U | N6 return reachability | GTP-U, plain ICMP, Linux route/NAT state |

Actual results must be documented as observed. An implementation may reject a
configuration at a slightly different point than the initial prediction.

## Layered Diagnostic Checklist

### Layer 0: Host and services

- Is the expected kernel running?
- Is MongoDB active?
- Are required Open5GS services active?
- Does `ogstun` exist?
- Are stale UE or gNB processes absent?

### Layer 1: N2 transport

- Is the AMF listening on SCTP port `38412`?
- Does SCTP complete?
- Are IP address and port correct?

### Layer 2: NG-RAN admission

- Does NG Setup receive a response?
- Do PLMN, TAC, gNB identity, and slice match?

### Layer 3: UE access and NAS registration

- Does the UE find the cell?
- Does RRC connect?
- Does the AMF receive Registration Request?

### Layer 4: Authentication and security

- Does subscriber lookup succeed?
- Do K and OP/OPc match?
- Is the SQN fresh or successfully resynchronized?
- Do Security Mode messages follow authentication?

### Layer 5: Session management

- Does registration complete first?
- Is DNN supported?
- Is S-NSSAI authorized?
- Is IPv4 session type supported?
- Does the SMF select a UPF?

### Layer 6: N4 and N3

- Does PFCP Session Establishment succeed?
- Are N3 resources exchanged?
- Are TEIDs and endpoints present?
- Does GTP-U appear in both directions?

### Layer 7: N6 and Linux

- Does the UE namespace have an address and default route?
- Is IPv4 forwarding enabled?
- Does the scoped forwarding rule exist?
- Does the UE-subnet MASQUERADE rule exist?
- Does the host itself reach the external destination?

## Explaining A Technical Finding

A concise technical explanation can use this structure:

```text
1. Baseline:
   State what worked before the change.

2. Intentional change:
   Name the single value or rule changed.

3. Prediction:
   Name the procedure and interface expected to fail.

4. Evidence:
   Identify the last successful and first failed events.

5. Localization:
   State which functions, interface, and protocol own that boundary.

6. Root cause:
   Describe the broken configuration contract.

7. Recovery:
   State what was restored and which successful evidence returned.
```

## Review Questions

1. Why is a missing packet not automatically proof that the sender never
   created it?
2. If PFCP succeeds and uplink GTP-U exists, which earlier layers are already
   proven?
3. Why is changing one variable important?
4. Which evidence sources would be correlated for an authentication failure?
5. What is the first area to inspect when registration succeeds but no PDU
   session is accepted?

## Next Document

Use the [Acronym Glossary](07_acronym_glossary.md) as a permanent quick
reference.

# Wrong Subscriber Key Or OPc Scenario

## Status

Complete. The failure was reproduced, captured, explained, reversed, and
followed by a successful baseline recovery test.

## Purpose

Demonstrate a 5G Authentication and Key Agreement (5G-AKA) failure after
access signalling and registration have already started.

OPc is the derived Operator Code used with the permanent subscriber key by the
authentication algorithm.

## Known-Good Baseline

The synthetic User Equipment (UE) and subscriber record contain matching
identity and authentication material.

## Intentional Change

The dedicated UE configuration changes only the final hexadecimal digit of
the synthetic permanent key:

```text
baseline suffix: 6BC
failure suffix:  6BD
```

The failure configuration is:

[`configs/failures/wrong_subscriber_key/open5gs-ue-wrong-key.yaml`](../../../configs/failures/wrong_subscriber_key/open5gs-ue-wrong-key.yaml)

The MongoDB subscriber record and known-good UE configuration remain
unchanged.

## Expected Correct Behavior

The UE calculates the expected authentication response, Non-Access-Stratum
(NAS) security activates, and registration completes.

## Predicted Failure Boundary

The Authentication Request reaches the UE, but the calculated response cannot
be accepted. Because the wrong key also prevents the UE from validating the
Authentication Token (AUTN), UERANSIM may report a Message Authentication Code
(MAC) failure before it can produce a valid authentication response. Security
Mode and Registration Accept should not complete.

## Observed Failure Symptom

The UE selected the correct cell, established Radio Resource Control (RRC),
sent Registration Request, and received Authentication Request. It then
reported:

```text
AUTN validation MAC mismatch
Sending Authentication Failure with cause [MAC_FAILURE]
Authentication Reject received
```

The UE returned to a deregistered state. Security Mode, Registration Accept,
and PDU Session Establishment did not complete.

## Last Successful Procedure

The gNB completed Stream Control Transmission Protocol (SCTP) and NG Setup.
The UE completed cell selection and RRC connection, and the AMF received its
Registration Request. The network delivered an Authentication Request.

## First Failed Or Missing Procedure

5G-AKA failed when the UE validated the Authentication Token (AUTN). The UE
sent Authentication Failure with 5G Mobility Management cause `20` (MAC
failure), and the AMF returned Authentication Reject. The expected
Authentication Response and subsequent NAS Security Mode procedure were
missing.

## Logs Checked

- UERANSIM UE console;
- Open5GS Access and Mobility Management Function (AMF) journal;
- Open5GS Authentication Server Function (AUSF) journal;
- Open5GS Unified Data Management (UDM) journal.

The AMF independently recorded `Authentication failure(MAC failure)` and
`Authentication reject`. See [`log_summary.txt`](log_summary.txt).

## Packet Capture Evidence

- [`wrong_subscriber_key.pcap`](wrong_subscriber_key.pcap): reviewed
  16-packet failure exchange;
- [`recovery.pcap`](recovery.pcap): reviewed 29-packet recovery exchange;
- [`packet_summary.txt`](packet_summary.txt): frame mapping, hashes, and
  interpretation.

Failure frames 9-12 show Registration Request, Authentication Request,
Authentication Failure with MAC failure, and Authentication Reject. Recovery
frames 9-21 show Authentication Response, Security Mode, and PDU Session
Resource Setup.

## Root Cause

The isolated UE configuration contained a synthetic permanent subscriber key
that differed from the core subscriber record by one hexadecimal digit. The UE
therefore derived different authentication values and could not validate the
network's AUTN.

## Fix

Stop the faulty UE and use the unchanged baseline UE configuration containing
the key that matches the subscriber record.

## Recovery Proof

With the baseline UE configuration restored, the capture contained
Authentication Response followed by Security Mode Command and PDU Session
Resource Setup. UERANSIM reported:

```text
Initial Registration is successful
PDU Session establishment is successful PSI[1]
```

## Concise Technical Explanation

The test changed only one hexadecimal digit of the UE's synthetic permanent
subscriber key. Transport, NG Setup, cell selection, RRC, and the Registration
Request all succeeded, so those layers were not the problem. During 5G-AKA,
the UE used its configured key to validate the MAC inside AUTN. Its result did
not match the network's value because the core used the correct subscriber
key. The UE therefore sent Authentication Failure with cause MAC failure, the
AMF rejected authentication, and NAS security never started. Restoring the
matching key changed the packet sequence to Authentication Response, Security
Mode, successful registration, and PDU-session setup. This localizes the fault
to authentication material rather than access, mobility, or session routing.

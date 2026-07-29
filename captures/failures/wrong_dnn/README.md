# Wrong DNN Scenario

## Status

Complete. The failure was reproduced, captured, explained, reversed, and
followed by a successful baseline recovery test.

## Purpose

Demonstrate that successful registration does not guarantee Protocol Data Unit
(PDU) session establishment.

DNN means Data Network Name.

## Known-Good Baseline

The User Equipment (UE), subscriber profile, Session Management Function
(SMF), and User Plane Function (UPF) use DNN `internet`.

## Intentional Change

The dedicated UE configuration changes only:

```text
apn: internet -> apn: unsupported
```

UERANSIM uses the field name `apn` for the requested 5G DNN. The failure
configuration is:

[`configs/failures/wrong_dnn/open5gs-ue-wrong-dnn.yaml`](../../../configs/failures/wrong_dnn/open5gs-ue-wrong-dnn.yaml)

The subscriber record and known-good UE configuration remain unchanged.

## Expected Correct Behavior

Registration completes, the `internet` PDU session is accepted, and the UE
receives an Internet Protocol version 4 (IPv4) address.

## Predicted Failure Boundary

Authentication, Non-Access-Stratum (NAS) security, and registration should
succeed because the identity and authentication material still match. The UE
then requests DNN `unsupported`, so PDU-session establishment should be
rejected or never accepted. A UE tunnel interface should not become usable.

## Observed Failure Symptom

Authentication, NAS security, and initial registration completed. The UE then
sent PDU Session Establishment Request and received:

```text
DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED
```

NAS timer T3580 expired and the UE retransmitted the session request. Each
retry received the same cause. No successful PDU-session message, UE address,
or tunnel interface followed.

## Last Successful Procedure

The UE completed authentication, NAS Security Mode, Registration Accept, and
Registration Complete. This proves the UE was registered before the data
session failed.

## First Failed Or Missing Procedure

The first PDU Session Establishment Request for DNN `unsupported` failed AMF
subscription/slice validation. No new SMF or UPF session was created, and
NGAP PDU Session Resource Setup never occurred.

## Logs Checked

- UERANSIM UE console;
- Open5GS Access and Mobility Management Function (AMF) journal;
- Open5GS Session Management Function (SMF) journal;
- Open5GS User Plane Function (UPF) journal.

The AMF identified the cause directly:

```text
Ue requested DNN "unsupported" Not Supported OR Not Subscribed in the Slice
```

The SMF and UPF did not create a new `unsupported` session. See
[`log_summary.txt`](log_summary.txt).

## Packet Capture Evidence

- [`wrong_dnn.pcap`](wrong_dnn.pcap): reviewed 28-packet failure exchange;
- [`recovery.pcap`](recovery.pcap): reviewed 35-packet recovery exchange;
- [`packet_summary.txt`](packet_summary.txt): frame mapping, hashes, absence
  checks, and interpretation.

The failure capture contains successful registration signaling, a protected
downlink status response, and a T3580-driven retransmission. It contains no
PFCP Session Establishment and no NGAP PDU Session Resource Setup.

The recovery capture contains PFCP Session Establishment and Modification plus
NGAP PDU Session Resource Setup.

## Root Cause

The UE requested DNN `unsupported`, while the subscriber and core support DNN
`internet`. The AMF rejected the unsupported/unsubscribed DNN before creating
a new SMF or UPF session.

## Fix

Stop the faulty UE and request the supported DNN `internet`.

## Recovery Proof

The unchanged baseline UE requested DNN `internet`. UERANSIM reported:

```text
Initial Registration is successful
PDU Session establishment is successful PSI[1]
```

The SMF created a session, the UPF installed it, and the UE received address
`10.45.0.4` on `uesimtun0`.

## Concise Technical Explanation

Registration and data-session authorization are separate. In this test, the UE
had the correct identity, key, PLMN, TAC, and slice, so authentication, NAS
security, and registration succeeded. The UE then requested DNN
`unsupported`. The AMF could not match that DNN to the subscriber in the
selected slice, so it returned `DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED` before
creating an SMF or UPF session. T3580 caused the UE to retry, but retries
cannot fix a configuration mismatch. Restoring DNN `internet` produced PFCP
session creation, NGAP PDU Session Resource Setup, address assignment, and a
working UE tunnel interface.

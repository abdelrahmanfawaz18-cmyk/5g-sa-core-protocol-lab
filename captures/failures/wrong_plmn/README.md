# Wrong PLMN Scenario

## Status

Complete. The failure was reproduced, captured, explained, reversed, and
followed by a successful baseline recovery test.

## Purpose

Demonstrate that successful Stream Control Transmission Protocol (SCTP)
transport does not guarantee that the Access and Mobility Management Function
(AMF) accepts a gNodeB (gNB).

PLMN means Public Land Mobile Network. It is formed from the Mobile Country
Code (MCC) and Mobile Network Code (MNC).

## Known-Good Baseline

```text
gNB PLMN: 999-70
AMF PLMN: 999-70
TAC:      1
SST:      1
```

TAC means Tracking Area Code. SST means Slice/Service Type.

## Intentional Change

The isolated gNB configuration changes only:

```text
mnc: '70' -> mnc: '71'
```

The failure configuration is:

[`configs/failures/wrong_plmn/open5gs-gnb-wrong-plmn.yaml`](../../../configs/failures/wrong_plmn/open5gs-gnb-wrong-plmn.yaml)

The normal baseline file is not edited.

## Expected Correct Behavior

With PLMN `999-70`, the gNB establishes SCTP, sends NG Setup Request, receives
NG Setup Response, and reports that NG Setup succeeded.

## Predicted Failure Boundary

The faulty gNB should reach the AMF transport endpoint and send NG Setup
Request. The AMF should reject or terminate setup because PLMN `999-71` is not
served by the baseline.

This prediction matched the observed result.

## Observed Failure Symptom

UERANSIM established SCTP and sent NG Setup Request. The AMF responded with NG
Setup Failure:

```text
Cause: misc/unknown-PLMN-or-SNPN
```

The failure occurred approximately 3.8 milliseconds after the first captured
SCTP packet.

## Last Successful Procedure

The SCTP association completed through `INIT`, `INIT ACK`, `COOKIE ECHO`, and
`COOKIE ACK`. The AMF then received and acknowledged the NG Setup Request.

## First Failed Or Missing Procedure

NG Setup acceptance failed. The AMF returned an NGAP unsuccessful outcome
instead of NG Setup Response.

## Logs Checked

- UERANSIM gNB console;
- Open5GS AMF system journal for the failure window;
- Open5GS AMF system journal for the recovery window.

The concise result is in [`log_summary.txt`](log_summary.txt).

## Packet Capture Evidence

- [`wrong_plmn.pcap`](wrong_plmn.pcap): reviewed 11-packet failure exchange;
- [`wrong_plmn_recovery.pcap`](wrong_plmn_recovery.pcap): reviewed 11-packet
  recovery exchange;
- [`packet_summary.txt`](packet_summary.txt): frame mapping, hashes, and
  interpretation.

Failure frame 5 advertises MCC `999`, MNC `71`, TAC `1`, and SST `1`.
Failure frame 7 is NG Setup Failure with cause
`misc/unknown-PLMN-or-SNPN` and a 10-second wait value.

Recovery frame 7 is NG Setup Response for the baseline PLMN `999-70`.

## Root Cause

The root cause was confirmed:

```text
gNB advertised PLMN 999-71 != AMF served PLMN 999-70
```

The AMF journal described the global gNB ID PLMN as foreign.

## Fix

Stop the faulty gNB and start the normal gNB with the unchanged PLMN `999-70`
configuration.

## Recovery Proof

The unchanged baseline produced NG Setup Response in the recovery capture and
UERANSIM reported:

```text
NG Setup procedure is successful
```

## Concise Technical Explanation

The test changed only the gNB Mobile Network Code from the supported value
`70` to unsupported value `71`. The gNB still completed SCTP with the AMF,
which proved that the address, port, and transport path worked. The gNB then
sent NG Setup Request advertising PLMN `999-71`. The AMF decoded the request,
identified the PLMN as foreign, and returned NG Setup Failure with the
standardized cause `unknown-PLMN-or-SNPN`. After the faulty gNB was stopped,
the unchanged PLMN `999-70` baseline received NG Setup Response. This
localizes the failure to RAN identity acceptance rather than N2 transport.

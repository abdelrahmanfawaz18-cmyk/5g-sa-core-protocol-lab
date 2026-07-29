# Wrong TAC Scenario

## Status

Complete. The failure was reproduced, captured, explained, reversed, and
followed by a successful baseline recovery test.

## Purpose

Demonstrate how an unsupported Tracking Area Code (TAC) affects gNodeB (gNB)
admission or User Equipment (UE) location handling.

## Known-Good Baseline

The gNB and Access and Mobility Management Function (AMF) use Public Land
Mobile Network (PLMN) `999-70` and TAC `1`.

## Intentional Change

The isolated gNB configuration changes only:

```text
tac: 1 -> tac: 2
```

The failure configuration is:

[`configs/failures/wrong_tac/open5gs-gnb-wrong-tac.yaml`](../../../configs/failures/wrong_tac/open5gs-gnb-wrong-tac.yaml)

The PLMN and every other baseline value are preserved.

## Expected Correct Behavior

The AMF accepts the gNB tracking area and later accepts UE location
information.

## Predicted Failure Boundary

The gNB has the correct PLMN, so NG Setup may succeed. If Open5GS accepts the
gNB association, the normal UE will register from Tracking Area Identity
`999-70-2`, while the AMF serves `999-70-1`. The expected failure boundary is
therefore Next Generation Application Protocol (NGAP) NG Setup validation or
Non-Access-Stratum (NAS) registration location handling.

The implementation's actual rejection point will be recorded rather than
assumed. Open5GS rejected the mismatch during NG Setup, so starting the UE was
not necessary.

## Observed Failure Symptom

The gNB completed SCTP and sent NG Setup Request. The AMF returned NG Setup
Failure:

```text
Cause: misc/unknown-PLMN-or-SNPN
```

The AMF journal supplied the more specific internal reason:

```text
Cannot find Served TAI. Check 'amf.tai' configuration
```

TAI means Tracking Area Identity.

## Last Successful Procedure

The SCTP association completed through `INIT`, `INIT ACK`, `COOKIE ECHO`, and
`COOKIE ACK`. The AMF then received and acknowledged NG Setup Request.

## First Failed Or Missing Procedure

NG Setup acceptance failed. The AMF returned an NGAP unsuccessful outcome
instead of NG Setup Response.

## Logs Checked

- UERANSIM gNB console;
- Open5GS AMF system journal for the failure window;
- Open5GS AMF system journal for the recovery window.

The concise result is in [`log_summary.txt`](log_summary.txt).

## Packet Capture Evidence

- [`wrong_tac.pcap`](wrong_tac.pcap): reviewed 11-packet failure exchange;
- [`wrong_tac_recovery.pcap`](wrong_tac_recovery.pcap): reviewed 11-packet
  recovery exchange;
- [`packet_summary.txt`](packet_summary.txt): frame mapping, hashes, and
  interpretation.

Failure frame 5 proves the global PLMN remained `999-70` while the Supported
Tracking Area List advertised TAC `2`. Failure frame 7 is NG Setup Failure
with cause `misc/unknown-PLMN-or-SNPN` and a 10-second wait value.

Recovery frame 5 advertises TAC `1`, and recovery frame 7 is NG Setup Response.

## Root Cause

The root cause was confirmed:

```text
gNB advertised TAI 999-70-2 != AMF served TAI 999-70-1
```

The correct global gNB PLMN proves this was not the global-PLMN mismatch from
the previous scenario.

## Fix

Restore the baseline TAC `1`.

## Recovery Proof

The unchanged TAC `1` baseline produced NG Setup Response in the recovery
capture, and UERANSIM reported:

```text
NG Setup procedure is successful
```

## Concise Technical Explanation

The test changed only the gNB Tracking Area Code from supported TAC `1` to
unsupported TAC `2`. The gNB retained the correct PLMN `999-70` and completed
SCTP, proving the transport path worked. Its NG Setup Request advertised
Tracking Area Identity `999-70-2`. The AMF serves `999-70-1`, so it returned
NG Setup Failure. The standardized cause was `unknown-PLMN-or-SNPN`, while the
AMF log identified the more specific reason: it could not find the served TAI.
After restoring TAC `1`, the AMF returned NG Setup Response. This localizes
the failure to tracking-area configuration rather than SCTP or global gNB
PLMN identity.

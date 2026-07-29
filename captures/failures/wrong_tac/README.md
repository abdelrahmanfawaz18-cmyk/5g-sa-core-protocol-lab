# Wrong TAC Scenario

## Status

Planned. Not yet implemented or executed.

## Purpose

Demonstrate how an unsupported Tracking Area Code (TAC) affects gNodeB (gNB)
admission or User Equipment (UE) location handling.

## Known-Good Baseline

The gNB and Access and Mobility Management Function (AMF) use Public Land
Mobile Network (PLMN) `999-70` and TAC `1`.

## Intentional Change

Use a dedicated gNB configuration with a different TAC while preserving the
PLMN and every other baseline value.

## Expected Correct Behavior

The AMF accepts the gNB tracking area and later accepts UE location
information.

## Predicted Failure Boundary

Next Generation Application Protocol (NGAP) NG Setup or UE registration
location handling. The implementation's actual rejection point will be
recorded.

## Observed Failure Symptom

Pending.

## Logs Checked

Pending.

## Packet Capture Evidence

Pending.

## Root Cause

Pending confirmation of the planned tracking-area mismatch.

## Fix

Restore the baseline TAC `1`.

## Recovery Proof

Pending.

## Concise Technical Explanation

Pending.

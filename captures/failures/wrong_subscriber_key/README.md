# Wrong Subscriber Key Or OPc Scenario

## Status

Planned. Not yet implemented or executed.

## Purpose

Demonstrate a 5G Authentication and Key Agreement (5G-AKA) failure after
access signalling and registration have already started.

OPc is the derived Operator Code used with the permanent subscriber key by the
authentication algorithm.

## Known-Good Baseline

The synthetic User Equipment (UE) and subscriber record contain matching
identity and authentication material.

## Intentional Change

Use a dedicated UE configuration with one authentication value changed. The
MongoDB subscriber record and known-good UE configuration remain unchanged.

## Expected Correct Behavior

The UE calculates the expected authentication response, Non-Access-Stratum
(NAS) security activates, and registration completes.

## Predicted Failure Boundary

The Authentication Request reaches the UE, but the calculated response cannot
be accepted. Security Mode and Registration Accept should not complete.

## Observed Failure Symptom

Pending.

## Logs Checked

Pending. Relevant sources include UE, Access and Mobility Management Function
(AMF), Authentication Server Function (AUSF), and Unified Data Management
(UDM) output.

## Packet Capture Evidence

Pending.

## Root Cause

Pending confirmation of the planned authentication-material mismatch.

## Fix

Stop the faulty UE and use the unchanged baseline UE configuration.

## Recovery Proof

Pending.

## Concise Technical Explanation

Pending.

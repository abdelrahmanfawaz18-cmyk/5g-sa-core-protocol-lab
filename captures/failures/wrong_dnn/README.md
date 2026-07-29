# Wrong DNN Scenario

## Status

Planned. Not yet implemented or executed.

## Purpose

Demonstrate that successful registration does not guarantee Protocol Data Unit
(PDU) session establishment.

DNN means Data Network Name.

## Known-Good Baseline

The User Equipment (UE), subscriber profile, Session Management Function
(SMF), and User Plane Function (UPF) use DNN `internet`.

## Intentional Change

Use a dedicated UE configuration that requests an unsupported DNN. Preserve
the subscriber record and known-good UE configuration.

## Expected Correct Behavior

Registration completes, the `internet` PDU session is accepted, and the UE
receives an Internet Protocol version 4 (IPv4) address.

## Predicted Failure Boundary

Registration and Non-Access-Stratum (NAS) security succeed, but PDU-session
establishment is rejected or never accepted.

## Observed Failure Symptom

Pending.

## Logs Checked

Pending. Relevant sources are UE, Access and Mobility Management Function
(AMF), and SMF output.

## Packet Capture Evidence

Pending.

## Root Cause

Pending confirmation of the planned DNN mismatch.

## Fix

Stop the faulty UE and request the supported DNN `internet`.

## Recovery Proof

Pending.

## Concise Technical Explanation

Pending.

# Successful UE Registration Flow

## Status

Complete. The baseline gNB and synthetic UE registration are supported by
correlated simulator, core-log, state, and packet-capture evidence.

One UERANSIM gNB connected to the Open5GS AMF, and one synthetic UE completed
5G-AKA authentication, NAS security activation, and initial registration.

## What The Evidence Proves

The result proves that the control-plane path works across:

```text
UERANSIM UE
    |
    | N1 NAS, relayed by the gNB
    v
UERANSIM gNB
    |
    | N2 NGAP over SCTP
    v
Open5GS AMF
    |
    | Service-based interfaces
    v
AUSF, UDM, UDR, and subscriber database
```

The gNB successfully established its N2 relationship with the AMF. The UE was
then identified, authenticated, placed under NAS security, and registered.

Registration proves control-plane admission. It does not, by itself, prove
that user packets can traverse N3, the UPF, and N6. The independent
PDU-session evidence validates that user-plane path.

## Evidence

- Packet capture:
  [`captures/successful/n2_registration_attempt.pcap`](../captures/successful/n2_registration_attempt.pcap)
- Tshark summary:
  [`reports/registration_tshark_summary.txt`](../reports/registration_tshark_summary.txt)
- UE success image:
  [`screenshots/successful_registration.png`](../screenshots/successful_registration.png)
- Completion report:
  [`reports/registration_validation.md`](../reports/registration_validation.md)

The capture contains only loopback N2 traffic between `127.0.0.1` and
`127.0.0.5`. Its subscriber identity is synthetic and restricted to this lab.

## Observed Message Sequence

| Step | Message | Sender | Receiver | Protocol | What it means |
| --- | --- | --- | --- | --- | --- |
| 1 | NG Setup Request | gNB | AMF | NGAP/SCTP | The gNB presents its identity, PLMN, tracking area, and supported slice |
| 2 | NG Setup Response | AMF | gNB | NGAP/SCTP | The AMF accepts the gNB and establishes the N2 relationship |
| 3 | Registration Request | UE | AMF, through gNB | NAS in NGAP | The UE requests initial registration using its synthetic SUCI |
| 4 | Authentication Request | AMF/AUSF side | UE | NAS in NGAP | The network challenges the UE using a 5G-AKA authentication vector |
| 5 | Authentication Failure, synchronization failure | UE | AMF | NAS in NGAP | The UE reports that the first sequence number is outside its accepted freshness range |
| 6 | Authentication Request | AMF/AUSF side | UE | NAS in NGAP | The network sends a fresh challenge after sequence-number resynchronization |
| 7 | Authentication Response | UE | AMF | NAS in NGAP | The UE returns its calculated response, proving possession of matching authentication material |
| 8 | Security Mode Command | AMF | UE | NAS in NGAP | The AMF selects NAS integrity algorithm IA2 and null ciphering for this local baseline |
| 9 | Security Mode Complete | UE | AMF | Protected NAS in NGAP | The UE accepts the security context and confirms activation |
| 10 | Registration Accept | AMF | UE | Protected NAS in NGAP | The core accepts the UE and supplies registration context, including a temporary identity |
| 11 | Registration Complete | UE | AMF | Protected NAS in NGAP | The UE confirms that registration has completed |

The extra synchronization exchange is part of the observed run, so it is
included rather than hidden. The registration still completed successfully.

## Packet-to-Message Correlation

| Frame | Relative time | Direction | Observed content |
| --- | ---: | --- | --- |
| 5 | `0.000532 s` | gNB to AMF | NG Setup Request |
| 7 | `0.032264 s` | AMF to gNB | NG Setup Response |
| 39 | `87.230361 s` | gNB to AMF | Initial UE Message carrying Registration Request |
| 40 | `87.260230 s` | AMF to gNB | Downlink NAS Transport carrying first Authentication Request |
| 41 | `87.262453 s` | gNB to AMF | Uplink NAS Transport carrying synchronization failure |
| 42 | `87.271021 s` | AMF to gNB | Downlink NAS Transport carrying second Authentication Request |
| 43 | `87.273084 s` | gNB to AMF | Uplink NAS Transport carrying Authentication Response |
| 44 | `87.279705 s` | AMF to gNB | Downlink NAS Transport carrying Security Mode Command |
| 45 | `87.281636 s` | gNB to AMF | Protected Uplink NAS Transport; UE output confirms Security Mode Complete |
| 46 | `87.301172 s` | AMF to gNB | Initial Context Setup Request carrying protected Registration Accept |
| 47 | `87.302063 s` | gNB to AMF | Initial Context Setup Response |
| 49 | `87.509537 s` | gNB to AMF | Protected uplink NAS messages; UE output confirms Registration Complete, followed by a session request |

Tshark can name the unprotected NAS messages directly. After NAS ciphering is
activated, it can still identify NGAP transport and the NAS security header,
but it cannot name encrypted inner messages without derived session keys. The
UERANSIM output and Open5GS AMF log were therefore correlated by timestamp to
identify Security Mode Complete, Registration Accept, and Registration
Complete.

## Technical Explanation

### NG Setup Is Not UE Registration

NG Setup creates the relationship between the NG-RAN node and the AMF. It
proves that SCTP transport works and that the AMF accepts the gNB's PLMN,
tracking area, and supported slice.

At this point, the gNB is connected but no UE has been admitted. UE
registration is a separate NAS procedure that begins later with an Initial UE
Message.

### N1 NAS Is Carried Across N2

N1 is the logical UE-to-AMF signalling relationship. The UE does not have a
direct IP connection to the AMF during registration. Instead:

```text
UE NAS message -> simulated radio link -> gNB -> NGAP NAS-PDU -> AMF
```

The gNB handles the access-side UE context and relays the NAS payload. The AMF
terminates NAS and controls registration.

### 5G-AKA Authentication

The UE and the subscriber database contain matching lab-only authentication
material. The permanent key and OPC are not transmitted over N1 or N2.

The network obtains an authentication vector through the AUSF and UDM. It
sends a random challenge and authentication token to the UE. The UE validates
the network and calculates `RES*`; the core compares that result with its
expected response.

Matching results prove that both sides possess consistent authentication
material without sending the permanent key itself.

### Sequence-Number Resynchronization

5G-AKA uses a sequence number to prevent replay of an old authentication
challenge. The first challenge in this run contained a sequence number the UE
did not consider fresh.

The UE returned an Authentication Failure with synchronization-failure cause
and resynchronization data. The core updated its sequence state and issued a
second Authentication Request. The UE accepted the second challenge and sent
Authentication Response.

This is a protocol-defined recovery path, not the final outcome of the
procedure. The later Security Mode and Registration Complete messages prove
that recovery succeeded.

### NAS Security

The Security Mode Command selected:

- integrity algorithm IA2;
- null ciphering for this isolated local baseline.

Integrity protection enables the receiver to detect unauthorized modification
of NAS messages. Ciphering controls confidentiality. The security context is
derived from authentication; it does not reuse the permanent subscriber key
directly as a packet-encryption key.

The UE's Security Mode Complete is protected using the new NAS security
context.

### Registration Accept And Temporary Identity

Registration Accept tells the UE that the core has admitted it. The live UE
state showed:

```text
rm-state: RM-REGISTERED
mm-state: MM-REGISTERED/NORMAL-SERVICE
selected-plmn: 999/70
current-tac: 1
```

The UE also received a 5G-GUTI. A 5G-GUTI is a temporary identity that reduces
the need to reveal the permanent subscriber identity during later procedures.

Registration Complete confirms that the UE received and accepted the
registration context.

## Reproduction Sequence

Use four terminals so every foreground process and error remains visible.

Terminal 1:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_core.sh
```

Terminal 2:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/capture_n2.sh
```

Terminal 3:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_gnb.sh
```

Wait for:

```text
NG Setup procedure is successful
```

Terminal 4:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_ue.sh
```

Wait for:

```text
Initial Registration is successful
```

Stop the capture, UE, and gNB with `Ctrl+C` after the required evidence has
been collected.

## Registration Result

**COMPLETE:** One synthetic UE registered successfully. NG Setup,
authentication, NAS security activation, Registration Accept, and Registration
Complete are supported by correlated capture, simulator state, simulator
output, and core-log evidence.

## Related User-Plane Evidence

Registration establishes the UE's mobility-management state. The independent
[PDU-session and user-plane analysis](04_pdu_session_flow.md) proves session
admission, tunnel creation, routing, and bidirectional traffic through the
UPF.

# UERANSIM Configuration

## Phase 4 Status

UERANSIM 3.3.0 was built successfully from official source revision
`2a3ef81f189ca95d5c1996a28ed7af9734f5cfb4`.

The source and executable files are local machine dependencies and are not
stored in this repository:

```text
~/UERANSIM
~/UERANSIM/build/nr-gnb
~/UERANSIM/build/nr-ue
~/UERANSIM/build/nr-cli
```

The YAML files in this directory are project copies of the official Open5GS
examples from that revision. They are Phase 4 templates, not a confirmed
working baseline. Phase 5 will compare every shared value with Open5GS before
the programs are started.

All subscriber values in these files are isolated lab examples. Never replace
them with credentials or identifiers from a real mobile subscription.

## gNB Configuration

The gNB configuration is `open5gs-gnb.yaml`.

| Field | Meaning | Required relationship |
| --- | --- | --- |
| `mcc` | Mobile Country Code | Must match the UE and the PLMN accepted by Open5GS |
| `mnc` | Mobile Network Code | Must match the UE and Open5GS; two and three-digit values are different |
| `nci` | NR Cell Identity | Identifies the simulated NR cell |
| `idLength` | gNB identifier length within the NCI | Must be valid for the selected NCI |
| `tac` | Tracking Area Code | Must be accepted by the Open5GS AMF |
| `linkIp` | Local simulated-radio address | Must appear in the UE `gnbSearchList` |
| `ngapIp` | Local gNB endpoint for N2 | Receives NGAP/SCTP traffic from the AMF |
| `gtpIp` | Local gNB endpoint for N3 | Receives GTP-U/UDP traffic from the UPF |
| `amfConfigs` | AMF N2 address and port | Must point to the Open5GS AMF; NGAP normally uses SCTP port 38412 |
| `slices` | S-NSSAIs supported by the gNB | Must include the slice requested by the UE and supported by the core |
| `ignoreStreamIds` | SCTP stream compatibility option | `true` avoids failures caused only by unexpected stream identifiers |
| `cellAccessType` | Terrestrial or satellite access type | `nr` selects normal terrestrial NR |

## UE Configuration

The UE configuration is `open5gs-ue.yaml`.

| Field | Meaning | Required relationship |
| --- | --- | --- |
| `supi` | Permanent subscriber identity, represented as an IMSI | Must exactly match the subscriber provisioned in Open5GS |
| `mcc` and `mnc` | UE home PLMN | Must agree with the SUPI, gNB, and core configuration |
| `protectionScheme` | SUCI identity-protection method | `0` uses the null scheme for this isolated lab |
| `key` | Permanent authentication key | Must exactly match the Open5GS subscriber |
| `op` | OP or OPC authentication value | Must exactly match the Open5GS subscriber |
| `opType` | Tells UERANSIM whether `op` contains OP or OPC | Must describe the stored value correctly |
| `amf` | Authentication Management Field | Must match the subscriber authentication settings; this is not the AMF network function |
| `gnbSearchList` | Simulated-radio address of the gNB | Must match the gNB `linkIp` |
| `sessions[].apn` | Requested data network name | Corresponds to the 5G DNN and must be supported by Open5GS |
| `sessions[].slice` | S-NSSAI requested for the PDU session | Must be supported by the UE, gNB, core, and subscriber |
| `configured-nssai` | Slices configured for the UE | Must include the intended lab slice |
| `default-nssai` | UE default slice | Its SST and optional SD must be compatible with the core |
| `tunNetmask` | Netmask for the UE tunnel interface | Controls the local subnet created after a PDU session |
| `useNamespace` | Places the UE tunnel in a Linux network namespace | `false` keeps the first lab topology simple |

## Shared Values To Validate In Phase 5

The following values form configuration contracts between components:

```text
PLMN:        MCC + MNC
Tracking:    TAC
N2:          gNB ngapIp <-> AMF address and SCTP port
Radio link:  gNB linkIp <-> UE gnbSearchList
Subscriber:  SUPI + key + OP/OPC + authentication AMF
Data:        DNN/APN
Slice:       SST + optional SD
```

One mismatch can prevent gNB connectivity, UE registration, authentication, or
PDU-session establishment. Phase 5 will build a single configuration map so
these values are selected deliberately instead of guessed.

# Baseline Configuration Validation

## Result

**COMPLETE:** The single-host baseline is mapped, the repository configuration
copies are validated, and one matching synthetic subscriber is provisioned.

## Validation Requirement

The configuration baseline requires one table showing every value that must
match and an explanation of faults caused by wrong PLMN, TAC, DNN, S-NSSAI,
key, or OPC.

The required source of truth is:

```text
docs/configuration_map.md
```

It covers access identity, transport endpoints, authentication, slice
selection, session selection, PFCP/GTP-U addressing, and the UE subnet.

## Baseline

| Contract | Verified value |
| --- | --- |
| PLMN | MCC `999`, MNC `70` |
| Tracking area | TAC `1` |
| N2 | gNB `127.0.0.1` to AMF `127.0.0.5:38412/SCTP` |
| N3 | gNB `127.0.0.1` to UPF `127.0.0.7:2152/UDP` |
| N4 | SMF `127.0.0.4:8805` to UPF `127.0.0.7:8805/UDP` |
| Subscriber | IMSI `999700000000001` |
| Authentication | Lab key, OPC, and AMF match the UE baseline |
| Slice | SST `1`, no SD |
| DNN | `internet` |
| Session type | IPv4 |
| UE subnet | `10.45.0.0/16` |
| UE gateway | `10.45.0.1` |

## Configuration Validation

All repository YAML files parsed successfully.

The active sections in these repository copies match their runtime
counterparts under `/etc/open5gs/`:

- NRF
- AMF
- SMF
- UPF
- AUSF
- UDM
- UDR
- PCF
- NSSF

The UERANSIM validation confirmed:

- gNB and UE use PLMN `999-70`;
- gNB and AMF use TAC `1`;
- gNB `linkIp` matches UE `gnbSearchList`;
- gNB points to AMF `127.0.0.5:38412`;
- gNB and UE support SST `1`;
- UE requests DNN `internet`;
- UE requests IPv4;
- UE configured and default NSSAI contain SST `1` with no SD.

## Subscriber Read-Back

MongoDB contains exactly one subscriber.

| Check | Result |
| --- | --- |
| Schema version | `1` |
| IMSI | Matches |
| Key | Matches |
| OPC | Matches |
| OP | `null`, because OPC is used |
| Authentication AMF | `8000` |
| Slice count | `1` |
| SST | `1` |
| SD | Absent |
| Default slice | `true` |
| DNN | `internet` |
| Session type | `1` (IPv4) |
| QoS index | `9` |

## Runtime Readiness

MongoDB and the nine required 5G Core services are active:

- `mongod`
- `open5gs-nrfd`
- `open5gs-amfd`
- `open5gs-smfd`
- `open5gs-upfd`
- `open5gs-ausfd`
- `open5gs-udmd`
- `open5gs-udrd`
- `open5gs-pcfd`
- `open5gs-nssfd`

AMF is ready on `127.0.0.5:38412/SCTP`. SMF and UPF have an active PFCP
association. `ogstun` is active at `10.45.0.1/16`.

Neither `nr-gnb` nor `nr-ue` was running during this configuration-only
validation. Registration and PDU-session results are documented separately.

## Completion Gate

- [x] One master table shows every value that must match.
- [x] Wrong-value failure effects are explained.
- [x] Only synthetic subscriber data is used.
- [x] Runtime and repository configurations agree.
- [x] Subscriber and UE authentication data agree.
- [x] Slice and DNN data agree.
- [x] User-plane subnet and gateway agree.
- [x] The configuration-only validation was isolated from live gNB and UE
  processes.

## Related Runtime Evidence

The [registration flow](../docs/03_successful_registration_flow.md) proves NG
Setup and synthetic UE registration with this baseline. The
[PDU-session flow](../docs/04_pdu_session_flow.md) proves session admission,
UPF programming, tunnel creation, and user traffic.

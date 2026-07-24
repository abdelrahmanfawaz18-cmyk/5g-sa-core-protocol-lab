# Lab Configuration Map

## Status

Phase 5 baseline completed on 2026-07-24.

This document is the source of truth for values shared by Open5GS, UERANSIM,
the subscriber database, and Linux networking. The baseline uses only
synthetic values for an isolated local lab.

No gNB or UE was started while this map was created.

## Design Summary

The first working version uses:

- one local Open5GS core;
- one simulated gNB;
- one simulated UE;
- one PLMN;
- one tracking area;
- one SST-only network slice;
- one IPv4 PDU session;
- one DNN;
- one dynamic UE address pool.

All core and simulator processes run on the same Ubuntu host. Separate
loopback addresses identify the network functions without requiring separate
computers.

## Master Configuration Table

| Item | Baseline value | Runtime location | Project location | Matching contract |
| --- | --- | --- | --- | --- |
| MCC | `999` | NRF and AMF YAML, subscriber identity | Open5GS and UERANSIM YAML copies | NRF, AMF, gNB, UE, and SUPI use the same PLMN |
| MNC | `70` | NRF and AMF YAML, subscriber identity | Open5GS and UERANSIM YAML copies | Two-digit MNC `70` is not the same as `070` |
| PLMN | `999-70` | Derived from MCC and MNC | This map | Network identity shared by UE, RAN, and core |
| TAC | `1` | `/etc/open5gs/amf.yaml` | `configs/open5gs/amf.yaml`, gNB YAML | gNB tracking area is served by AMF |
| NCI | `0x000000010` | UERANSIM gNB YAML | `configs/ueransim/open5gs-gnb.yaml` | Unique NR cell identity for this lab |
| gNB ID length | `32` bits | UERANSIM gNB YAML | `configs/ueransim/open5gs-gnb.yaml` | Valid gNB portion of the NCI |
| RLS address | `127.0.0.1` | gNB `linkIp`, UE `gnbSearchList` | Both UERANSIM YAML files | UE discovers the local simulated gNB |
| gNB N2 address | `127.0.0.1` | gNB `ngapIp` | gNB YAML | Local SCTP endpoint used by the gNB |
| AMF N2 endpoint | `127.0.0.5:38412/SCTP` | `/etc/open5gs/amf.yaml` | Open5GS AMF and UERANSIM gNB YAML | gNB establishes NGAP association with AMF |
| gNB N3 address | `127.0.0.1` | gNB `gtpIp` | gNB YAML | Local GTP-U endpoint used by the gNB |
| UPF N3 endpoint | `127.0.0.7:2152/UDP` | `/etc/open5gs/upf.yaml` | `configs/open5gs/upf.yaml` | N3 carries GTP-U user traffic |
| SMF N4 endpoint | `127.0.0.4:8805/UDP` | `/etc/open5gs/smf.yaml` | `configs/open5gs/smf.yaml` | SMF controls UPF using PFCP |
| UPF N4 endpoint | `127.0.0.7:8805/UDP` | `/etc/open5gs/upf.yaml` | `configs/open5gs/upf.yaml` | UPF receives PFCP rules from SMF |
| SUPI | `imsi-999700000000001` | UERANSIM UE | UE YAML | Maps to numeric IMSI `999700000000001` in MongoDB |
| Authentication key | `465B5CE8B199B49FAA5F0A2EE238A6BC` | UE and subscriber record | UE YAML and this map | Both sides derive the same authentication result |
| Operator value | `E8ED289DEBA952E4283B54E88E6183CA` | UE and subscriber record | UE YAML and this map | Stored and interpreted as OPC |
| Operator type | `OPC` | UE and subscriber record | UE YAML and this map | Prevents OP/OPC interpretation mismatch |
| Authentication AMF | `8000` | UE and subscriber record | UE YAML and this map | Authentication Management Field, not AMF network function |
| SUCI scheme | `0` | UE YAML | `configs/ueransim/open5gs-ue.yaml` | Null protection scheme for the isolated baseline |
| DNN/APN | `internet` | UE session and subscriber profile | UE YAML and this map | Subscriber is permitted to request this data network |
| PDU session type | IPv4 | UE session and subscriber profile | UE YAML and this map | Avoids adding IPv6 routing to the first version |
| Slice SST | `1` | AMF, NSSF, gNB, UE, subscriber | Open5GS and UERANSIM YAML copies | All components identify the same slice |
| Slice SD | Not used | Omitted from all active slice definitions | Open5GS and UERANSIM YAML copies | SST-only S-NSSAI is consistent everywhere |
| UE IPv4 subnet | `10.45.0.0/16` | SMF, UPF, Linux `ogstun` | SMF and UPF YAML copies | SMF address pool and UPF forwarding subnet agree |
| UE IPv4 gateway | `10.45.0.1` | SMF, UPF, Linux `ogstun` | SMF and UPF YAML copies | UPF-side gateway for the UE subnet |
| MTU | `1400` | SMF and Linux `ogstun` | `configs/open5gs/smf.yaml` | Leaves room for GTP-U encapsulation overhead |
| DNS | `8.8.8.8`, `8.8.4.4` | SMF YAML | `configs/open5gs/smf.yaml` | IPv4 DNS information offered with the session |

## Configuration Contracts

### Access Network Identity

```text
NRF PLMN = AMF GUAMI PLMN = AMF TAI PLMN = AMF supported PLMN
         = gNB PLMN = UE home PLMN = SUPI MCC/MNC

AMF TAC = gNB TAC
```

The gNB sends its supported PLMN and tracking area during NG Setup. A PLMN or
TAC mismatch can prevent NG Setup or cause the UE location to be rejected.

### Simulated Radio Link

```text
gNB linkIp = UE gnbSearchList = 127.0.0.1
```

This is UERANSIM's software radio-link transport. If these addresses differ,
the UE cannot find the gNB even if Open5GS is healthy.

### N2 Control Plane

```text
gNB amfConfigs address = AMF NGAP bind address = 127.0.0.5
gNB amfConfigs port    = AMF NGAP SCTP port    = 38412
```

N2 uses NGAP over SCTP. A wrong address or port prevents the gNB from reaching
the AMF. Correct transport alone is not enough; PLMN and TAC must also match.

### Subscriber Authentication

```text
UE SUPI digits = MongoDB subscriber IMSI
UE key         = subscriber security.k
UE OPC         = subscriber security.opc
UE AMF         = subscriber security.amf
```

A missing SUPI causes a subscriber lookup failure. A wrong key, OPC, or
authentication AMF lets lookup succeed but makes the calculated
authentication response differ from the network's expected response.

### Slice Selection

```text
AMF supported S-NSSAI = NSSF S-NSSAI = gNB supported S-NSSAI
                      = UE requested S-NSSAI = subscriber S-NSSAI
                      = SST 1 with no SD
```

An S-NSSAI is the combination of SST and optional SD. SST `1` without an SD is
not identical to SST `1` with SD `1`. The first baseline omits SD everywhere.

### PDU Session

```text
UE APN field = subscriber DNN = internet
UE session type = subscriber session type = IPv4
```

UERANSIM names the YAML field `apn`, while the 5G Core uses DNN terminology.
A wrong DNN can allow registration to finish but cause the PDU-session request
to fail.

### N4 and N3 User Plane

```text
SMF PFCP client -> UPF PFCP server: 127.0.0.7:8805/UDP
gNB GTP-U       <-> UPF GTP-U:      127.0.0.1 <-> 127.0.0.7:2152/UDP
SMF subnet       = UPF subnet       = ogstun subnet = 10.45.0.0/16
SMF gateway      = UPF gateway      = ogstun address = 10.45.0.1
```

N4 controls forwarding rules. N3 carries encapsulated UE packets. Correct N2
can therefore coexist with broken user-plane connectivity if N3, N4, or the
UE subnet is wrong.

## Subscriber Baseline

The Open5GS subscriber database contains exactly one synthetic record:

| Field | Value |
| --- | --- |
| IMSI | `999700000000001` |
| Key | `465B5CE8B199B49FAA5F0A2EE238A6BC` |
| OPC | `E8ED289DEBA952E4283B54E88E6183CA` |
| Authentication AMF | `8000` |
| Slice | SST `1`, no SD |
| DNN | `internet` |
| Session type | IPv4 |
| Default slice | Yes |
| QoS index | `9` |

The record follows the schema used by the official Open5GS database utility.
Subscriber provisioning changes MongoDB state but does not start a UE or
prove registration.

### Provisioning Method

The official `misc/db/open5gs-dbctl` utility was reviewed and used from
Open5GS source revision:

```text
29c00149033e56e34aea9fb559927673c01fb1f5
```

The numeric IMSI is stored in MongoDB without the UERANSIM `imsi-` prefix.
The provisioning sequence was:

```bash
open5gs-dbctl add 999700000000001 465B5CE8B199B49FAA5F0A2EE238A6BC E8ED289DEBA952E4283B54E88E6183CA
open5gs-dbctl type 999700000000001 1
```

The first command created an SST `1`, no-SD subscriber with DNN `internet`.
The second changed the utility's default IPv4v6 session type to IPv4-only,
matching the UERANSIM UE request.

The database was then queried directly to verify the record. Adding a
subscriber does not require a core restart; the UDR reads subscriber data from
MongoDB when the UE procedure begins.

## Failure Interpretation

| Wrong value | Likely stage | Expected symptom |
| --- | --- | --- |
| gNB `linkIp` or UE `gnbSearchList` | UERANSIM RLS | UE cannot find the simulated gNB |
| AMF N2 IP or port | SCTP transport | gNB cannot establish an SCTP association |
| PLMN | NG Setup or registration | Unsupported PLMN, TAI, or registration rejection |
| TAC | NG Setup or registration | Tracking area is not served by AMF |
| SUPI/IMSI | Subscriber lookup | Unknown UE or unknown SUCI |
| Key | 5G authentication | Authentication response does not match |
| OP/OPC value or type | 5G authentication | Authentication calculation fails |
| S-NSSAI | Slice selection | Registration or session selection is rejected |
| DNN | PDU session | Registration may work, but session creation fails |
| N4 PFCP endpoint | Session control | SMF cannot install forwarding state in UPF |
| N3 GTP-U endpoint | User plane | Registration/session signalling may work, but UE data fails |
| UE subnet or gateway | User-plane addressing | Address assignment, routing, or return traffic fails |

## Runtime And Repository Locations

Runtime Open5GS files remain under:

```text
/etc/open5gs/
```

The repository files under `configs/open5gs/` are reviewed Phase 5 copies of
the active configuration sections. They are evidence and reproducibility
references; changing a repository copy does not change a running service.

The UERANSIM programs will later read the repository files directly:

```text
configs/ueransim/open5gs-gnb.yaml
configs/ueransim/open5gs-ue.yaml
```

## Phase 5 Validation

Phase 5 is complete when all of the following are true:

- [x] One table identifies every shared value.
- [x] Open5GS runtime values were read from the active YAML files.
- [x] Repository Open5GS copies match the active baseline sections.
- [x] UERANSIM gNB and UE files use the selected baseline.
- [x] SST `1` is used without SD everywhere.
- [x] One synthetic subscriber matches the UE identity and authentication data.
- [x] The subscriber permits DNN `internet` on SST `1`.
- [x] The subscriber requests IPv4 only.
- [x] The SMF, UPF, and `ogstun` use `10.45.0.0/16` with gateway `10.45.0.1`.
- [x] No gNB or UE process was started.

## Phase 6 Entry Conditions

Phase 6 may begin when:

- Open5GS and MongoDB remain active.
- AMF listens on `127.0.0.5:38412/SCTP`.
- the two UERANSIM YAML files pass parsing and matching checks;
- the subscriber record passes a read-back check;
- there are no running `nr-gnb` or `nr-ue` processes before the controlled
  start sequence.

Phase 6 will separately prove NG Setup, authentication, NAS security, and UE
registration using logs and packet evidence.

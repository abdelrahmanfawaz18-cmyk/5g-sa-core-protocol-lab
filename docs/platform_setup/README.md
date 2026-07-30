# Platform Setup Reference

## Scope

This document records the verified Ubuntu, Open5GS, MongoDB, UERANSIM, and
packet-analysis platform supporting the 5G Standalone lab. It focuses on the
installed architecture, file locations, services, endpoints, and operational
checks.

The active system uses:

| Component | Verified value |
| --- | --- |
| Operating system | Ubuntu 24.04 LTS, 64-bit x86 |
| Validated kernel | `6.17.0-41-generic` |
| Python | `3.12.3` |
| Open5GS | `2.8.0~noble5` |
| MongoDB Community | `8.0.28` |
| UERANSIM | `3.3.0` |
| tcpdump | `4.99.4` |
| Wireshark/tshark | `4.2.2` |

The [environment record](../01_environment_setup.md) contains the original
preflight and installation evidence. The
[latest automated report](../../reports/latest_lab_check.md) records the
successful end-to-end state on the validated runtime kernel.

## Environment Requirements

The lab depends on Linux capabilities that are not available in an ordinary
Windows-native process environment:

- Stream Control Transmission Protocol (SCTP) support for N2;
- `/dev/net/tun` for UPF and UERANSIM tunnel interfaces;
- network namespaces for isolated UE routing;
- IPv4 forwarding and scoped `iptables` rules;
- packet capture on loopback and tunnel interfaces;
- `systemd` service management.

The verified host provides 24 logical CPUs, approximately 15 GiB of usable
memory, and sufficient storage for source builds and reviewed packet captures.

## Open5GS Deployment

Open5GS is installed as system packages and managed by `systemd`. The required
5G Core services are:

```text
open5gs-nrfd
open5gs-amfd
open5gs-smfd
open5gs-upfd
open5gs-ausfd
open5gs-udmd
open5gs-udrd
open5gs-pcfd
open5gs-nssfd
```

MongoDB runs as:

```text
mongod
```

The core readiness helper starts any inactive required units and validates the
AMF listener:

```bash
./scripts/run/start_core.sh
```

Direct service inspection uses:

```bash
systemctl is-active mongod
systemctl is-active open5gs-amfd
systemctl is-active open5gs-smfd
systemctl is-active open5gs-upfd
systemctl --failed --no-pager
```

Detailed service logs are available through `journalctl`, for example:

```bash
journalctl -u open5gs-amfd --no-pager
journalctl -u open5gs-smfd --no-pager
journalctl -u open5gs-upfd --no-pager
```

## Open5GS File Locations

| Purpose | Location |
| --- | --- |
| Active system configuration | `/etc/open5gs/` |
| Open5GS logs | `/var/log/open5gs/` |
| Reviewed repository copies | `configs/open5gs/` |
| Synthetic subscriber database | MongoDB database `open5gs` |
| Configuration map | `docs/configuration_map.md` |

The repository YAML files are reviewed reproducibility references. Editing a
copy under `configs/open5gs/` does not change the active service file under
`/etc/open5gs/`.

## Verified Core Endpoints

| Function | Interface or service | Endpoint |
| --- | --- | --- |
| AMF | N2 NGAP/SCTP | `127.0.0.5:38412` |
| AMF | Service-Based Interface | `127.0.0.5:7777/TCP` |
| SMF | Service-Based Interface | `127.0.0.4:7777/TCP` |
| SMF | N4 PFCP | `127.0.0.4:8805/UDP` |
| UPF | N4 PFCP | `127.0.0.7:8805/UDP` |
| UPF | N3 GTP-U | `127.0.0.7:2152/UDP` |
| NRF | Registration and discovery | `127.0.0.10:7777/TCP` |
| MongoDB | Subscriber data | `127.0.0.1:27017/TCP` |

Socket inspection requires separate Internet-socket and SCTP views:

```bash
ss -H -lntup
ss -H -ln --sctp
```

## Open5GS Function Boundaries

| Function | Primary responsibility |
| --- | --- |
| NRF | Network-function registration and discovery |
| AMF | gNB access, NAS termination, registration, and mobility |
| AUSF | Authentication service |
| UDM | Subscriber identity and authentication management |
| UDR | Persistent subscriber-data access |
| NSSF | Network-slice selection assistance |
| PCF | Policy control |
| SMF | PDU-session management and UPF control |
| UPF | User-packet forwarding between N3 and N6 |

MongoDB is not a 3GPP network function. It is the Open5GS persistence layer
behind subscriber and policy data exposed through core services such as UDR.

## UERANSIM Build

UERANSIM is built from official source revision:

```text
2a3ef81f189ca95d5c1996a28ed7af9734f5cfb4
```

The verified source/build tree is:

```text
~/UERANSIM/
└── build/
    ├── nr-gnb
    ├── nr-ue
    └── nr-cli
```

All three executables report UERANSIM `3.3.0`. If the source is stored
elsewhere, the run scripts accept:

```bash
export UERANSIM_ROOT=/path/to/UERANSIM
```

The validated repository configurations are:

```text
configs/ueransim/open5gs-gnb.yaml
configs/ueransim/open5gs-ue.yaml
```

The run scripts resolve the repository root dynamically and pass those files
directly to `nr-gnb` and `nr-ue`.

## UERANSIM Responsibilities

UERANSIM provides protocol-level UE and gNB behavior:

- cell discovery over its simulated radio link;
- Radio Resource Control state;
- NGAP communication from gNB to AMF;
- NAS registration, authentication, and session messages;
- GTP-U encapsulation between gNB and UPF;
- a UE tunnel interface inside a Linux network namespace.

It does not provide a complete radio-frequency channel, physical waveform, or
production gNB implementation.

## Tunnel And Namespace Support

The host exposes `/dev/net/tun`, which allows user-space networking processes
to exchange layer-3 packets with the Linux kernel.

Open5GS UPF uses:

```text
ogstun
```

The verified IPv4 gateway is:

```text
10.45.0.1/16
```

UERANSIM places `uesimtun0` inside a session-specific namespace such as:

```text
ueransim-999700000000001-internet-psi1
```

The namespace has its own address and default route, allowing tests to prove
that traffic originates from the simulated UE rather than the Ubuntu host.

## Runtime User-Plane Networking

External UE connectivity requires:

- `net.ipv4.ip_forward=1`;
- an outbound forwarding rule for `10.45.0.0/16` entering from `ogstun`;
- a return forwarding rule toward `ogstun`;
- a scoped `MASQUERADE` rule for the UE subnet.

The idempotent helper is:

```bash
./scripts/network/enable_ue_nat.sh
```

These rules are deliberately runtime-only. A reboot clears them, preventing
the lab from silently changing permanent host firewall policy.

Read-only inspection is available through:

```bash
./scripts/network/inspect_ue_network.sh
```

## Packet-Capture Toolchain

The project uses:

| Tool | Purpose |
| --- | --- |
| `tcpdump` | Command-line packet capture |
| `dumpcap` | Wireshark capture engine when user permissions allow |
| `tshark` | Scriptable decoding and summaries |
| Wireshark | Interactive protocol inspection and screenshots |

The capture helpers attempt unprivileged `dumpcap` first and fall back to
`tcpdump` with `sudo` when capture permissions are unavailable.

## Configuration Contracts

Successful operation depends on matching values across the core, gNB, UE, and
subscriber record:

| Contract | Verified baseline |
| --- | --- |
| PLMN | MCC `999`, MNC `70` |
| TAC | `1` |
| Slice | SST `1`, no SD |
| DNN | `internet` |
| PDU session type | IPv4 |
| AMF N2 address | `127.0.0.5` |
| gNB N3 address | `127.0.0.1` |
| UPF N3 address | `127.0.0.7` |
| UE subnet | `10.45.0.0/16` |
| UPF gateway | `10.45.0.1` |

Authentication values are synthetic and intentionally not reproduced in
documentation. Their cross-component matching rules are described in the
[configuration map](../configuration_map.md).

## Operational Verification

The complete live validator command is documented in
[`tools/README.md`](../../tools/README.md). A successful validation proves:

1. required executables are available;
2. MongoDB and required Open5GS units are active;
3. expected N2, N3, N4, SBI, and database endpoints are present;
4. the gNB completed SCTP association and NG Setup;
5. the UE completed authentication, NAS security, and registration;
6. a PDU session was accepted;
7. `uesimtun0` has an IPv4 address and default route;
8. traffic from inside the UE namespace reaches the external target.

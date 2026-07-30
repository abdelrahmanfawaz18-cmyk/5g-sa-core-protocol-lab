# Environment Setup

## Status

Complete. The Ubuntu host, packet-analysis tools, Open5GS services, MongoDB,
UERANSIM executables, SCTP support, and tunnel support are verified.

## Environment Type

The lab runs on a native, dual-boot Ubuntu installation on 64-bit x86 hardware.

## Operating System

- Distribution: Ubuntu 24.04 LTS
- Release: 24.04
- Codename: Noble Numbat

## Kernel

- End-to-end validated Linux kernel: `6.17.0-41-generic`
- Architecture: `x86_64`

## Hardware Capacity

- Logical CPUs: 24
- Usable memory: approximately 15 GiB
- Available lab-filesystem space during preflight: 33 GiB
- The system exceeds the baseline minimum of 4 CPU cores, 8 GB RAM, and 30 GB
  free disk space

## Git

- Git version: `2.43.0`
- Repository branch: `main`
- Remote: the expected GitHub `origin` is configured for fetch and push
- Repository-local author name and GitHub no-reply email are configured

## Python

- Python version: `3.12.3`
- The `python3` command is available

## Network Interfaces

- `lo`: loopback interface is available and active
- `wlp0s20f3`: Wi-Fi interface is active with a private IPv4 address
- `enp109s0`: Ethernet interface is present but disconnected
- `lxcbr0`: local LXC bridge is present and currently has no carrier

## Routing Table

- A default route is present through `wlp0s20f3`
- Connected routes are present for the Wi-Fi network and the local LXC bridge

## Packet Capture Tools

- tcpdump: `4.99.4`
- TShark (Wireshark): `4.2.2`
- Both required packet inspection commands are installed and run successfully
- A temporary five-packet capture was written to `/tmp` with no kernel drops and read successfully with TShark
- The temporary capture is outside the repository and is not tracked by Git

## Tunnel Interface Support

`/dev/net/tun` exists as a character device. Linux TUN/TAP support is available for the tunnel interfaces required later in the lab.

## Environment Preflight Result

**PASS:** The Ubuntu environment satisfies the CPU, memory, storage,
networking, packet-capture, Python, Git, SCTP, and TUN requirements.

## Open5GS Installation

The core installation was completed using packages built for Ubuntu 24.04:

- Open5GS: `2.8.0~noble5`
- MongoDB Community: `8.0.28`
- Installation method: Open5GS release PPA and the official MongoDB 8.0 repository
- MongoDB service: active, enabled at boot, and responding to database commands
- Open5GS WebUI: not installed because subscriber provisioning and validation
  use direct database and command-line workflows

The UDR and PCF configurations use `mongodb://localhost/open5gs`. The database
contains the synthetic subscriber used by the verified baseline.

## Open5GS Services

The required 5G Core services are active and enabled:

- `open5gs-nrfd`
- `open5gs-amfd`
- `open5gs-smfd`
- `open5gs-upfd`
- `open5gs-ausfd`
- `open5gs-udmd`
- `open5gs-udrd`
- `open5gs-pcfd`
- `open5gs-nssfd`

The package also installed supporting and legacy EPC services. In total, 17
Open5GS units are active and enabled, and no Open5GS unit is failed. A
host-level audit found one unrelated failed unit,
`systemd-networkd-wait-online.service`; the active interfaces, default route,
and core endpoints confirm that it does not block this lab.

Startup logs confirm that the required control-plane functions registered with the NRF and that the SMF established its PFCP association with the UPF. The optional SEPP service reports that its second roaming peer is unavailable; this is expected because roaming is outside this single-host lab.

## Open5GS Files

- Configuration directory: `/etc/open5gs/`
- Log directory: `/var/log/open5gs/`
- Function-specific YAML configuration files and logs are stored in these directories
- The initial package installation retained its defaults. The active lab
  baseline and reviewed repository copies are documented in
  [`configuration_map.md`](configuration_map.md).

## Verified Open5GS Endpoints

| Function | Purpose | Local endpoint |
|---|---|---|
| AMF | N2/NGAP | `127.0.0.5:38412` over SCTP |
| AMF | Service-based interface | `127.0.0.5:7777` over TCP |
| SMF | Service-based interface | `127.0.0.4:7777` over TCP |
| SMF and UPF | N4/PFCP | `127.0.0.4:8805` and `127.0.0.7:8805` over UDP |
| UPF | N3/GTP-U | `127.0.0.7:2152` over UDP |
| NRF | Service registration and discovery | `127.0.0.10:7777` over TCP |
| MongoDB | Subscriber and policy data | `127.0.0.1:27017` over TCP |

## Core Installation Result

**COMPLETE:** Open5GS is installed, the required services are healthy, configuration and log locations are known, listening endpoints are verified, and the core functions are documented.

## UERANSIM Installation

The UERANSIM build was completed from the official source revision:

- UERANSIM version: `3.3.0`
- Official source revision:
  `2a3ef81f189ca95d5c1996a28ed7af9734f5cfb4`
- Source directory: `~/UERANSIM`
- gNB executable: `~/UERANSIM/build/nr-gnb`
- UE executable: `~/UERANSIM/build/nr-ue`
- CLI executable: `~/UERANSIM/build/nr-cli`
- Required SCTP development and runtime packages are installed
- All three executables exist and report version `3.3.0`
- Project configuration templates and field explanations are stored under
  `configs/ueransim/`

The executables are not installed globally. The run scripts resolve them from
`~/UERANSIM` or the `UERANSIM_ROOT` environment variable.

## UERANSIM Build Result

**COMPLETE:** UERANSIM is built, the required executables are verified, the
official Open5GS example configurations are copied into the repository, and
the fields that must match the core and subscriber are documented.

## Integrated Result

The installed platform supports the complete verified workflow: NG Setup,
synthetic subscriber authentication, NAS security, registration, IPv4
PDU-session establishment, namespace tunnel creation, PFCP and GTP-U traffic,
and bidirectional external connectivity.

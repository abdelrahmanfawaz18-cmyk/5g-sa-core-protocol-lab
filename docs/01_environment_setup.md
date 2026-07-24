# Environment Setup

## Status

Phase 2 environment preflight completed successfully on 2026-07-23.

## Environment Type

The lab runs on a native, dual-boot Ubuntu installation on 64-bit x86 hardware. It is not running in WSL or a virtual machine.

## Operating System

- Distribution: Ubuntu 24.04.3 LTS
- Release: 24.04
- Codename: Noble Numbat

## Kernel

- Linux kernel: `6.17.0-35-generic`
- Architecture: `x86_64`

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

## Tunnel Interface Support

`/dev/net/tun` exists as a character device. Linux TUN/TAP support is available for the tunnel interfaces required later in the lab.

## Phase 2 Result

**READY:** This Ubuntu environment passed the Phase 2 preflight and is ready for Phase 3.

## Next Step

Phase 3 may begin with Open5GS installation when explicitly started. Open5GS and UERANSIM were not installed or configured during Phase 2.

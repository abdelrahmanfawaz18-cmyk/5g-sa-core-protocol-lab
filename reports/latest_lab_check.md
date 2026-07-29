# 5G SA Lab Check Report

Generated: 2026-07-29 17:16:34 EDT

## Summary

Overall status: **PASS**

## Environment

- Operating system: Ubuntu 24.04.4 LTS
- Kernel: 6.17.0-41-generic
- Python: 3.12.3
- Open5GS: systemd-managed local services
- UERANSIM: ~/UERANSIM

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Required commands | **PASS** | ip=/usr/sbin/ip; ping=/usr/bin/ping; tcpdump=/usr/bin/tcpdump; tshark=/usr/bin/tshark; nr-gnb=~/UERANSIM/build/nr-gnb; nr-ue=~/UERANSIM/build/nr-ue |
| Core services | **PASS** | All 10 required MongoDB/Open5GS services are active. |
| Expected ports | **PASS** | Listening: 38412 (N2 SCTP), 8805 (N4 PFCP), 2152 (N3 GTP-U), 7777 (Open5GS SBI), 27017 (MongoDB) |
| gNB connection | **PASS** | SCTP association established and NG Setup accepted. |
| UE registration | **PASS** | Authentication, NAS security, and initial registration completed. |
| PDU session | **PASS** | PDU Session Establishment completed successfully. |
| UE tunnel interface | **PASS** | uesimtun0 address 10.45.0.6/24; default route uses uesimtun0. |
| UE connectivity | **PASS** | 3 packets transmitted, 3 received, 0% packet loss, time 2003ms |

## Suggested Next Action

No action needed.

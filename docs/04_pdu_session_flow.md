# PDU Session and User-Plane Flow

## Status

Complete. The PDU session, tunnel state, routing, PFCP control, GTP-U traffic,
N6 forwarding, and return path are supported by reviewed evidence.

The synthetic UE established an IPv4 PDU session for DNN `internet` on SST
`1`, received address `10.45.0.4`, and exchanged five ICMP requests and
replies with `8.8.8.8` with no packet loss.

## What A PDU Session Provides

Registration and a PDU session solve different problems:

- Registration admits and identifies the UE on the 5G network.
- A PDU session gives the UE a data-network connection.

In this lab, the PDU session supplies an IPv4 address and a path to the
`internet` data network. The SMF controls that path, while the UPF forwards the
actual user packets.

The result extends the registration control-plane proof into the user plane:

```text
UERANSIM UE namespace
  10.45.0.4
      |
      | IP through uesimtun0
      v
UERANSIM UE -- simulated radio -- UERANSIM gNB
                                      |
                                      | N3: GTP-U/UDP 2152
                                      v
                              Open5GS UPF
                              127.0.0.7
                                      |
                                      | N6: ordinary IP
                                      | forwarding + NAT
                                      v
                                  8.8.8.8
```

The control relationship that creates the UPF forwarding state is separate:

```text
Open5GS SMF 127.0.0.4
          |
          | N4: PFCP/UDP 8805
          v
Open5GS UPF 127.0.0.7
```

## Configuration Contract

PDU-session establishment depends on matching values across several
components:

| Setting | Verified value | Why it must match |
| --- | --- | --- |
| UE session type | IPv4 | Determines the address family requested by the UE |
| DNN/APN | `internet` | Selects the requested data network |
| S-NSSAI | SST `1`, no SD | Selects the network slice |
| Subscriber permission | DNN `internet`, SST `1` | Authorizes the requested session |
| SMF pool | `10.45.0.0/16` | Supplies the UE IPv4 address |
| UPF pool | `10.45.0.0/16` | Provides the matching user-plane subnet |
| SMF N4 endpoint | `127.0.0.4` | Sends PFCP control messages |
| UPF N4 endpoint | `127.0.0.7` | Receives PFCP rules |
| gNB N3 endpoint | `127.0.0.1` | Sends and receives GTP-U for the simulated UE |
| UPF N3 endpoint | `127.0.0.7` | Terminates the N3 GTP-U tunnel |

A mismatch can cause the core to reject the request, choose no compatible
slice, fail to create UPF state, or establish a session that cannot carry
traffic.

## Observed Procedure

| Step | Message or event | Sender | Receiver | Protocol | Meaning |
| --- | --- | --- | --- | --- | --- |
| 1 | PDU Session Establishment Request | UE | AMF, then SMF | NAS over N1/N2 | The UE asks for an IPv4 connection to DNN `internet` on SST `1` |
| 2 | Session handling and SMF selection | AMF | SMF and other core functions | SBI | The core authorizes the request and selects session-management context |
| 3 | PFCP Session Establishment Request | SMF | UPF | PFCP on N4 | The SMF creates packet-detection and forwarding state in the UPF |
| 4 | PFCP Session Establishment Response | UPF | SMF | PFCP on N4 | The UPF confirms that the initial session state was installed |
| 5 | PDU Session Resource Setup Request | AMF | gNB | NGAP on N2 | The core supplies the access-side tunnel information needed by the gNB |
| 6 | PDU Session Resource Setup Response | gNB | AMF | NGAP on N2 | The gNB confirms its side of the N3 resource |
| 7 | PFCP Session Modification | SMF | UPF | PFCP on N4 | The SMF completes the UPF rules using the gNB tunnel information |
| 8 | PDU Session Establishment Accept | Core | UE | Protected NAS | The UE receives the accepted session parameters and assigned address |
| 9 | UE namespace and TUN interface created | UERANSIM | Linux networking | Local TUN | The UE gets `uesimtun0`, address `10.45.0.4`, and a default route |
| 10 | ICMP echo traffic | UE | `8.8.8.8` and back | IP inside GTP-U on N3 | Real user-plane packets traverse the UPF in both directions |

The SBI step is internal core signalling and was not included by the focused
capture filter. Its successful outcome is supported by the later PFCP, NGAP,
and NAS results.

## Packet Correlation

The reviewed capture is:

[`captures/successful/pdu_session_and_user_plane.pcap`](../captures/successful/pdu_session_and_user_plane.pcap)

### Control-Plane Frames

| Frame | Relative time | Direction | Observation |
| --- | ---: | --- | --- |
| 11 | `0.244801 s` | gNB to AMF | Protected uplink NAS transport associated with registration completion and the session request |
| 13 | `0.260304 s` | SMF to UPF | PFCP Session Establishment Request |
| 14 | `0.260730 s` | UPF to SMF | PFCP Session Establishment Response |
| 15 | `0.262283 s` | AMF to gNB | NGAP PDU Session Resource Setup Request |
| 17 | `0.265156 s` | gNB to AMF | NGAP PDU Session Resource Setup Response |
| 18 | `0.266187 s` | SMF to UPF | PFCP Session Modification Request |
| 19 | `0.266354 s` | UPF to SMF | PFCP Session Modification Response |

Protected NAS cannot be named completely from this capture without the
derived NAS session keys. UERANSIM independently reported `PDU Session
Establishment Accept received` and `PDU Session establishment is successful
PSI[1]`, so the simulator output was correlated with the transport frames.

### User-Plane Frames

| Ping sequence | Uplink GTP-U request | Downlink GTP-U reply |
| ---: | ---: | ---: |
| 1 | 20 | 25 |
| 2 | 26 | 31 |
| 3 | 32 | 37 |
| 4 | 38 | 43 |
| 5 | 44 | 49 |

The encapsulated headers show:

```text
Uplink outer path:   127.0.0.1 -> 127.0.0.7
Uplink inner path:   10.45.0.4 -> 8.8.8.8
Uplink TEID:         0x0000a2ab

Downlink outer path: 127.0.0.7 -> 127.0.0.1
Downlink inner path: 8.8.8.8 -> 10.45.0.4
Downlink TEID:       0x00000001
```

A TEID identifies a GTP-U tunnel endpoint in one direction. Uplink and
downlink can use different TEID values because each receiving endpoint assigns
the identifier it expects to receive.

## Packet Walkthrough

### Uplink

1. `ping` creates an ICMP echo request inside the UE namespace.
2. The namespace default route sends it to `uesimtun0`.
3. UERANSIM reads the IP packet from the TUN interface and carries it over its
   simulated radio connection to the gNB.
4. The gNB adds a GTP-U header and sends it on N3 to the UPF.
5. The UPF uses its PFCP-programmed rules to identify the session, removes the
   GTP-U wrapper, and forwards the inner IP packet toward N6.
6. Linux changes the private lab source address to the Ubuntu host's outbound
   address using masquerading, because the upstream network has no route for
   `10.45.0.0/16`.

### Downlink

1. The ICMP echo reply returns to the translated host address.
2. Connection tracking reverses the address translation and restores
   destination `10.45.0.4`.
3. The packet reaches the UPF through `ogstun`.
4. The UPF matches the PFCP forwarding state and adds the downlink GTP-U
   header.
5. The UPF sends the packet over N3 to the gNB.
6. The gNB carries it to UERANSIM UE, which writes it into `uesimtun0`.
7. The `ping` process receives the reply inside the UE namespace.

The capture shows every major transformation for all five packets: inner UE
traffic, translated N6 traffic, and GTP-U traffic in both directions.

## Why Network Namespace Isolation Is Needed

Open5GS and UERANSIM run on the same Ubuntu machine in this lab. If
`uesimtun0` is created in the root namespace, both the UE address and the UPF
gateway appear on the same host. Linux local-address and source-routing
behavior can then bypass or misroute the intended downlink path.

With `useNamespace: true`, UERANSIM places the UE TUN interface in:

```text
ueransim-999700000000001-internet-psi1
```

The root namespace contains the core and UPF, while the child namespace
contains the simulated UE interface and route. This models the separation
that naturally exists between a physical UE and a core network.

## Why Forwarding And Masquerading Are Needed

The UPF converts packets between the N3 GTP-U tunnel and ordinary N6 IP
traffic. Ubuntu must then be allowed to forward those packets. IPv4 forwarding
provides that router behavior.

The assigned UE address is from private lab subnet `10.45.0.0/16`. The
upstream network does not know how to return traffic directly to it.
Masquerading provides source address translation on the outbound path and
automatic reverse translation for replies.

The runtime helper is:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/network/enable_ue_nat.sh
```

Its rules are intentionally not persistent. Repeat the helper after rebooting
before running another Internet user-plane test.

## Reproduction Sequence

First verify the core and install the runtime forwarding state:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_core.sh
./scripts/network/enable_ue_nat.sh
```

Then use separate terminals for the foreground processes.

Capture terminal, using a new output name so existing evidence is preserved:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/capture_pdu_session.sh /tmp/pdu_session_test.pcap
```

gNB terminal:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_gnb.sh
```

Wait for `NG Setup procedure is successful`, then start the UE in another
terminal:

```bash
cd ~/projects/5g-sa-core-protocol-lab
./scripts/run/start_ue.sh
```

After PDU-session success, inspect and test from another terminal:

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 ip -br addr
sudo ip netns exec ueransim-999700000000001-internet-psi1 ip route
sudo ip netns exec ueransim-999700000000001-internet-psi1 ping -c 5 8.8.8.8
```

Stop the capture, UE, and gNB with `Ctrl+C` after collecting the result.

## Evidence

- UE interface and route report:
  [`reports/ue_interface_success.md`](../reports/ue_interface_success.md)
- Concise packet analysis:
  [`reports/user_plane_tshark_summary.txt`](../reports/user_plane_tshark_summary.txt)
- Successful ping image:
  [`screenshots/ping_success.png`](../screenshots/ping_success.png)
- Reviewed packet capture:
  [`captures/successful/pdu_session_and_user_plane.pcap`](../captures/successful/pdu_session_and_user_plane.pcap)
- Completion report:
  [`reports/user_plane_validation.md`](../reports/user_plane_validation.md)

## PDU-Session Result

**COMPLETE:** The PDU session was established, the UE received an address and
isolated TUN interface, real traffic passed through the UPF, PFCP and
bidirectional GTP-U are visible in the reviewed capture, and the complete flow
is documented.

## Related Packet Analysis

The [packet-capture guide](05_packet_capture_guide.md) documents the capture
commands, display filters, message landmarks, encapsulation, and correlation
methods used for this result.

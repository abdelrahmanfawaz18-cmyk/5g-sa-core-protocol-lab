# Beginner Guide to Phases 1-4

## Purpose

This guide explains what was completed during the first four phases of the 5G
SA Core Protocol Lab, why each step was necessary, and how the pieces fit
together. It assumes no previous experience with Linux, Git, mobile networks,
Open5GS, or UERANSIM.

The lab has reached the following point:

- The public project repository is established.
- Ubuntu passed the environment preflight.
- MongoDB and Open5GS are installed and running.
- UERANSIM is built and its example configurations are documented.
- The gNB and UE have not been started.
- No subscriber has been provisioned.
- No registration or PDU session has been attempted.

The last three items are intentional. They belong to later phases.

### How to Read the Command Examples

Commands were typed in Ubuntu's **Terminal** application, which can be opened
with `Ctrl+Alt+T`.

When this guide shows:

```bash
git status
```

type only `git status` and press Enter. Do not type the shell prompt that may
appear before it.

Useful path rules:

- `~` means the current user's home directory.
- `.` means the current directory.
- `/` at the beginning means an absolute path from the filesystem root.
- Linux filenames and paths are case-sensitive.

When `sudo` requests the Ubuntu password, the Terminal does not display dots
or other characters while the password is typed. That is normal.

## 1. The Big Picture

### 1.1 What 5G Standalone Means

5G Standalone, normally shortened to **5G SA**, means that the 5G radio access
network connects to a 5G Core. It does not depend on a 4G EPC for control.

A basic mobile network contains four major areas:

1. **UE:** the user equipment, such as a phone.
2. **RAN:** the radio access network that connects the UE to the core.
3. **5G Core:** the network functions that authenticate the UE, register it,
   create data sessions, enforce policy, and forward traffic.
4. **Data network:** the destination beyond the mobile core, such as a local
   test network or the Internet.

This lab replaces real radio equipment with software:

- UERANSIM `nr-ue` acts as the UE.
- UERANSIM `nr-gnb` acts as the 5G base station.
- Open5GS provides the 5G Core.
- MongoDB stores subscriber and policy data for Open5GS.

UERANSIM does not generate real radio waves. Its UE-to-gNB radio link is a
software simulation. The protocols between the gNB and the core are the real
5G protocols we want to study.

### 1.2 End-to-End Architecture

```text
                                      5G CORE CONTROL PLANE
                                  +-----------------------------+
                                  |                             |
                                  | NRF   AUSF   UDM   UDR      |
                                  |  |      |     |     |       |
                                  |  +------+-----+-----+---+   |
                                  |                       |     |
                                  | NSSF   PCF           AMF----SMF
                                  |                       ^      |
                                  +-----------------------|------|----+
                                                          |      |
                       N1: NAS, logical UE-to-AMF path     | N2   | N4
                                                          |NGAP  |PFCP
                                                          |SCTP  |UDP
                                                          |      v
+-------------+   simulated radio   +----------------+    |   +---------+
| UERANSIM UE |<------------------->| UERANSIM gNB   |----+   |   UPF   |
|   nr-ue     |       RLS/UDP       |    nr-gnb      |-------->|         |
+-------------+                     +----------------+ N3 |   +----+----+
                                       GTP-U/UDP         |        |
                                                         |        | N6: IP
                                                         |        v
                                                         |  +-------------+
                                                         +->| Data Network|
                                                            +-------------+
```

The diagram shows two different kinds of work:

- The **control plane** decides whether and how the UE may connect.
- The **user plane** carries the UE's data after a session is created.

### 1.3 Control Plane Versus User Plane

The control plane handles signalling:

- finding and connecting to a gNB;
- identifying the UE;
- authenticating the subscriber;
- registering the UE;
- selecting a network slice;
- requesting and creating a PDU session;
- telling the UPF how to forward traffic.

The user plane carries actual UE packets:

- ping traffic;
- DNS requests;
- web traffic;
- any other IP data sent through the UE tunnel.

This separation is fundamental. The AMF and SMF make control decisions, while
the UPF forwards user traffic.

## 2. The Main 5G Components

### 2.1 UE

The **User Equipment** is normally a phone, modem, or other cellular device.
In this lab, `nr-ue` simulates it.

The UE has:

- a subscriber identity called a SUPI, represented here as an IMSI;
- an authentication key and OP or OPC value;
- a home PLMN identified by MCC and MNC;
- a requested DNN;
- a requested network slice;
- protocol logic for NAS registration and session management.

The UE will eventually create a Linux TUN interface for its PDU session. That
interface does not exist yet because no PDU session has been established.

### 2.2 gNB

The **next-generation NodeB**, or gNB, is the 5G base station. In this lab,
`nr-gnb` simulates it.

The gNB has three important relationships:

- It communicates with the simulated UE over UERANSIM's software radio link.
- It connects to the AMF over N2 using NGAP over SCTP.
- It connects to the UPF over N3 using GTP-U over UDP.

The gNB relays NAS signalling between the UE and AMF. It does not authenticate
the subscriber itself.

### 2.3 Open5GS Network Functions

| Function | Full name | Beginner explanation |
| --- | --- | --- |
| NRF | Network Repository Function | A directory where core functions register and discover each other |
| AMF | Access and Mobility Management Function | Accepts the gNB connection and manages UE registration and mobility |
| SMF | Session Management Function | Creates and manages PDU sessions and controls the UPF |
| UPF | User Plane Function | Forwards the UE's data between the gNB and data network |
| AUSF | Authentication Server Function | Participates in verifying the UE's authentication response |
| UDM | Unified Data Management | Provides subscriber identity and authentication information |
| UDR | Unified Data Repository | Reads and writes persistent subscriber and policy data |
| PCF | Policy Control Function | Supplies policy decisions for subscribers and sessions |
| NSSF | Network Slice Selection Function | Helps select a compatible network slice |

MongoDB is not a 5G network function. It is the database used by Open5GS
functions such as UDR and PCF.

### 2.4 A Simplified Registration Conversation

Registration has not been performed yet, but understanding the intended
conversation explains why these components were installed.

1. The UE discovers the simulated gNB.
2. The gNB establishes its N2 SCTP association with the AMF.
3. The UE sends a NAS Registration Request.
4. The gNB carries that NAS message inside NGAP to the AMF.
5. The AMF obtains authentication support from AUSF and subscriber information
   through UDM and UDR.
6. The UE and core perform the authentication exchange.
7. If the identity, key, PLMN, and slice information agree, the AMF accepts the
   registration.

The gNB can connect successfully while the UE still fails authentication.
These are separate stages and will later be tested separately.

### 2.5 A Simplified PDU Session Conversation

After registration, the intended session flow is:

1. The UE requests a PDU session for a DNN and S-NSSAI.
2. The AMF forwards session-management information to the SMF.
3. The SMF selects the UPF.
4. The SMF sends PFCP rules to the UPF over N4.
5. The gNB and UPF receive the information needed to form the N3 GTP-U path.
6. UERANSIM creates a UE TUN interface.
7. UE IP packets can travel through the gNB, UPF, and N6 data network.

This is future work. Phase 4 only prepared the software.

## 3. Interfaces and Protocols

An **interface** describes a standardized relationship between components. A
**protocol** defines the message format and behaviour used on that interface.

| Interface | Endpoints | Protocol | Purpose |
| --- | --- | --- | --- |
| N1 | UE and AMF | NAS-5GS | Registration, authentication, mobility, and session signalling |
| N2 | gNB and AMF | NGAP over SCTP | Carries RAN signalling and transports UE NAS messages |
| N3 | gNB and UPF | GTP-U over UDP | Tunnels UE user-plane packets |
| N4 | SMF and UPF | PFCP over UDP | Installs and manages forwarding rules in the UPF |
| N6 | UPF and data network | IP | Connects UE traffic to an external network |
| SBI | 5G Core control functions | HTTP-based service APIs | Lets core functions register, discover, and request services |
| RLS | UERANSIM UE and gNB | UERANSIM protocol over UDP | Simulates the radio link in software; it is not the real NR air interface |

### 3.1 Why N1 Is Called a Logical Interface

The UE does not open a direct IP connection to the AMF. Its NAS message travels
through the gNB:

```text
UE NAS message -> gNB -> NGAP container -> AMF
```

N1 describes the logical UE-to-AMF protocol relationship. N2 describes the
actual gNB-to-AMF transport relationship.

### 3.2 Why SCTP Is Used on N2

SCTP is a transport protocol, like TCP or UDP, but it supports features useful
for telecom signalling, including message boundaries and multiple streams.

In this lab:

```text
gNB -> 127.0.0.5:38412/SCTP -> AMF
```

UERANSIM requires Linux SCTP support. This is one reason the active lab moved
from Windows to native Ubuntu.

### 3.3 Why GTP-U Is Used on N3

GTP-U encapsulates a UE's original IP packet inside another packet so it can
cross the mobile network between the gNB and UPF.

Conceptually:

```text
outer IP + UDP + GTP-U + original UE IP packet
```

The outer headers move the packet between the gNB and UPF. The inner packet is
the UE's actual user traffic.

### 3.4 Why PFCP Is Used on N4

The SMF decides how a PDU session should behave, but it does not forward the
traffic. It uses PFCP to install forwarding rules in the UPF.

This gives a clear separation:

- SMF: session control and decisions.
- UPF: packet forwarding.

### 3.5 IP Addresses, Ports, and Transport Protocols

An IP address identifies a network endpoint. A port identifies a service at
that endpoint. The transport protocol is also part of the identity.

For example, UDP port 2152 and SCTP port 2152 are not the same endpoint.

This single-host lab uses different loopback addresses:

```text
127.0.0.4   SMF
127.0.0.5   AMF
127.0.0.7   UPF
127.0.0.10  NRF
```

All addresses in `127.0.0.0/8` refer to the local computer. Using separate
loopback addresses allows multiple network functions to use familiar ports
without needing multiple physical computers.

### 3.6 Important Mobile-Network Terms

| Term | Meaning |
| --- | --- |
| MCC | Mobile Country Code; the country portion of a mobile network identity |
| MNC | Mobile Network Code; identifies the network within that country code |
| PLMN | Public Land Mobile Network identity formed from MCC and MNC |
| TAC | Tracking Area Code; groups cells into an area used for mobility management |
| NCI | NR Cell Identity; identifies a 5G NR cell |
| SUPI | Permanent 5G subscriber identity known by the home network |
| IMSI | The numeric subscriber-identity format used as the SUPI in this lab |
| SUCI | A concealed form of the SUPI sent over the access network |
| DNN | Data Network Name requested for a PDU session, such as `internet` |
| APN | Older configuration term used by UERANSIM for the corresponding data-network name |
| S-NSSAI | Identifier for one network slice |
| SST | Slice/Service Type; the required part of an S-NSSAI |
| SD | Slice Differentiator; an optional value that distinguishes slices with the same SST |
| PDU session | The logical association that gives a registered UE data connectivity through a UPF |

The Phase 4 templates currently contain example identities and credentials.
They are not considered a working baseline until Phase 5 compares them with
the Open5GS configuration and subscriber record.

## 4. Phase 1: Establish the Project

### 4.1 What We Did

We created the repository at:

```text
~/projects/5g-sa-core-protocol-lab
```

The repository contains:

```text
README.md       Main project summary and status
.gitignore      Rules for files Git should not track
docs/           Explanations and verified setup records
configs/        Lab configuration copies
scripts/        Reserved for later reproducible scripts
tools/          Reserved for later validation utilities
captures/       Reserved for sanitized packet evidence
reports/        Reserved for concise result reports
screenshots/    Reserved for reviewed technical images
diagrams/       Reserved for verified diagrams
tests/          Reserved for tests that accompany future tools
```

Every tracked directory contains useful documentation. Empty placeholder files
were removed.

### 4.2 Why Git Was Needed

Git records changes as commits. Each commit provides:

- the files that changed;
- who created the change;
- a message explaining the milestone;
- a unique identifier;
- the ability to compare or recover earlier versions.

GitHub stores the remote copy. It also served as the bridge between the
original Windows work and the current Ubuntu environment.

The relationship is:

```text
working files -> local Git commits -> GitHub repository
```

The remote is:

```text
https://github.com/abdelrahmanfawaz18-cmyk/5g-sa-core-protocol-lab.git
```

The repository-local Git identity uses the configured GitHub no-reply address,
so commits do not publish a private email address.

### 4.3 How the Repository Reached Ubuntu

The repository shell was originally created and pushed from Windows. Ubuntu
then received the complete history from GitHub:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/abdelrahmanfawaz18-cmyk/5g-sa-core-protocol-lab.git
cd ~/projects/5g-sa-core-protocol-lab
```

The repository-specific commit identity was set with:

```bash
git config user.name "abdelrahmanfawaz18-cmyk"
git config user.email "240996129+abdelrahmanfawaz18-cmyk@users.noreply.github.com"
```

These settings affect this repository only. They do not replace Git's global
settings for unrelated repositories.

The connection and history were checked with:

```bash
git status
git remote -v
git log --oneline --max-count=5
```

- `git status` showed the current branch and whether files had changed.
- `git remote -v` showed the GitHub fetch and push address.
- `git log` showed that the commit history arrived correctly.

### 4.4 Why `.gitignore` Matters

The `.gitignore` prevents common generated or sensitive files from being added
accidentally. It covers:

- editor and operating-system files;
- logs;
- Python caches and virtual environments;
- build and temporary directories;
- environment and key files;
- packet captures by default.

Packet captures may expose unrelated traffic or identifiers. They will only be
added later after deliberate review.

### 4.5 Phase 1 Result

The local repository, documentation shell, public GitHub repository, required
description, topics, commit history, and `main` branch were all verified.

## 5. Phase 2: Prove Ubuntu Can Run the Lab

### 5.1 Why Preflight Came Before Installation

Installing the core would have been wasted effort if Ubuntu lacked SCTP,
packet-capture support, networking, or TUN support. Phase 2 checked the
platform before adding 5G software.

### 5.2 Commands and Their Meanings

The preflight command sequence was:

```bash
uname -a
lsb_release -a
ip addr
ip route
python3 --version
git --version
tcpdump --version
tshark --version
ls -l /dev/net/tun
```

| Command | What it checks |
| --- | --- |
| `uname -a` | Kernel, computer architecture, and operating-system kernel build |
| `lsb_release -a` | Ubuntu distribution name, release, and codename |
| `ip addr` | Network interfaces and their addresses |
| `ip route` | The routes Linux uses to choose where packets go |
| `python3 --version` | Availability and version of Python |
| `git --version` | Availability and version of Git |
| `tcpdump --version` | Availability of command-line packet capture |
| `tshark --version` | Availability of command-line Wireshark analysis |
| `ls -l /dev/net/tun` | Kernel support for software tunnel interfaces |

The verified environment is:

| Item | Result |
| --- | --- |
| Environment | Native dual-boot Ubuntu |
| Ubuntu | 24.04.3 LTS |
| Kernel | 6.17.0-35-generic |
| Architecture | x86-64 |
| Python | 3.12.3 |
| Git | 2.43.0 |
| tcpdump | 4.99.4 |
| TShark | 4.2.2 |
| Logical CPUs | 24 |
| Memory | Approximately 15 GiB |
| TUN device | `/dev/net/tun` exists |

### 5.3 Packet-Capture Test

A small temporary capture proved that packets could be written to a `.pcap`
file and read back with TShark.

The result was:

```text
5 packets captured
5 packets received by filter
0 packets dropped by kernel
```

The capture was stored under `/tmp`, outside the repository. It was evidence
that capture worked, not a project artifact.

### 5.4 TUN Support

A TUN interface is a software network interface that gives a process access to
IP packets.

Two related names must not be confused:

- `/dev/net/tun` is the Linux device used to create TUN interfaces.
- `ogstun` is the Open5GS tunnel interface for the UPF-side UE subnet.

Open5GS has created:

```text
ogstun: 10.45.0.1/16
```

UERANSIM will later create a separate interface such as `uesimtun0` after a
PDU session succeeds.

### 5.5 Phase 2 Result

The system passed the networking, software, packet-capture, hardware, and TUN
completion gates.

## 6. Phase 3: Install and Understand Open5GS

### 6.1 What Was Installed

The final installation uses:

| Software | Version | Purpose |
| --- | --- | --- |
| MongoDB Community | 8.0.28 | Persistent subscriber and policy data |
| Open5GS | 2.8.0~noble5 | 5G Core network functions |

MongoDB came from its Ubuntu Noble 8.0 repository. Open5GS came from the
Open5GS Ubuntu Noble release PPA.

#### MongoDB procedure

The successful MongoDB procedure was:

```bash
sudo apt update
sudo apt install -y curl gnupg
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl enable --now mongod
```

The `|` symbol sends the downloaded key from `curl` directly into `gpg`. It
must remain on the same command line. `tee` writes the repository definition
to the system APT configuration. `enable --now` both starts MongoDB immediately
and configures it to start during later boots.

What these commands did:

1. Add the repository signing key.
2. Add the software repository for Ubuntu Noble.
3. Refresh APT's package information.
4. Install the package.
5. Enable and start the service.
6. Verify service state, ports, database response, and logs.

APT is Ubuntu's package manager. A package repository tells APT where trusted
software packages and updates are available.

MongoDB was verified with:

```bash
systemctl is-active mongod
systemctl is-enabled mongod
mongosh --quiet --eval 'JSON.stringify(db.adminCommand({ping:1}))'
```

The database response contained `"ok":1`.

#### Open5GS procedure

Open5GS was installed from its release PPA:

```bash
sudo add-apt-repository ppa:open5gs/latest
sudo apt update
sudo apt install -y open5gs
```

The package installed and enabled the Open5GS systemd services. Their state was
then checked with `systemctl`, their sockets with `ss`, and their startup
messages under `/var/log/open5gs/`.

### 6.2 Installed Versus Running Versus Enabled

These terms are different:

- **Installed:** files are present on disk.
- **Running or active:** a process is executing now.
- **Enabled:** systemd is configured to start it during future boots.

MongoDB and the required Open5GS services are all installed, active, and
enabled.

Normally, after a reboot, systemd starts them automatically. Their state can be
checked with:

```bash
systemctl is-active mongod
systemctl is-enabled mongod
systemctl is-active open5gs-amfd
systemctl is-enabled open5gs-amfd
```

Expected output is `active` for the first check and `enabled` for the second.

### 6.3 Required 5G Services

The nine required services are:

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

The package also includes supporting and legacy EPC services. Seventeen
Open5GS services are currently active and enabled. No Open5GS service is
failed.

One unrelated host service,
`systemd-networkd-wait-online.service`, is failed. Active networking, a valid
default route, and healthy 5G services prove that it does not block this lab.

### 6.4 Important Open5GS Endpoints

| Function | Address | Transport | Meaning |
| --- | --- | --- | --- |
| AMF N2 | `127.0.0.5:38412` | SCTP | Future gNB NGAP connection |
| AMF SBI | `127.0.0.5:7777` | TCP/HTTP | AMF service-based communication |
| SMF SBI | `127.0.0.4:7777` | TCP/HTTP | SMF service-based communication |
| SMF N4 | `127.0.0.4:8805` | UDP/PFCP | SMF side of UPF control |
| UPF N4 | `127.0.0.7:8805` | UDP/PFCP | UPF side of SMF control |
| UPF N3 | `127.0.0.7:2152` | UDP/GTP-U | Future gNB user-plane tunnel |
| NRF SBI | `127.0.0.10:7777` | TCP/HTTP | Network-function registration |
| MongoDB | `127.0.0.1:27017` | TCP | Local database service |

The verified logs show:

- core network functions registering with the NRF;
- the SMF associating with the UPF over PFCP;
- the AMF listening for a future gNB on SCTP port 38412.

### 6.5 Configuration and Log Locations

```text
/etc/open5gs/      Open5GS YAML configuration files
/var/log/open5gs/  Function-specific Open5GS logs
```

Examples include:

```text
/etc/open5gs/amf.yaml
/etc/open5gs/smf.yaml
/etc/open5gs/upf.yaml
/var/log/open5gs/amf.log
/var/log/open5gs/smf.log
/var/log/open5gs/upf.log
```

YAML is a human-readable configuration format based on keys, values, lists,
and indentation. Indentation is significant.

### 6.6 What Was Intentionally Not Changed

Phase 3 did not:

- change PLMN, TAC, DNN, or S-NSSAI values;
- add a subscriber;
- change Open5GS routing or NAT;
- start a gNB or UE;
- attempt registration.

The purpose was to install a healthy core before changing its baseline.

### 6.7 Phase 3 Result

The core packages, services, endpoints, configuration paths, log paths, NRF
registrations, and PFCP association were verified. Each required core function
is explained in the project documentation.

## 7. Phase 4: Build UERANSIM

### 7.1 Why UERANSIM Was Built From Source

UERANSIM provides the simulated UE and gNB. Its official project distributes
source code, so the Ubuntu build tools compile that source into executable
programs for this computer.

Compiling means translating source code into machine instructions.

### 7.2 Build Prerequisites

The build and runtime dependencies are:

| Package or tool | Reason |
| --- | --- |
| `make` | Runs the project's build recipe |
| `gcc` | Compiles C source and dependencies |
| `g++` | Compiles UERANSIM's C++ source |
| `cmake` | Generates part of the build configuration |
| `libsctp-dev` | Provides SCTP headers and development files |
| `lksctp-tools` | Provides Linux SCTP runtime support and utilities |
| `iproute2` | Provides Linux interface and route tools |

Ubuntu already had `make`, GCC, G++, CMake, and `iproute2`. We installed the
missing SCTP packages with:

```bash
sudo apt update
sudo apt install -y libsctp-dev lksctp-tools
```

`sudo` runs an administrative command. APT needs administrative permission
because it writes system package files.

### 7.3 Clone and Build Commands

The source was downloaded with:

```bash
git clone https://github.com/aligungr/UERANSIM.git ~/UERANSIM
```

The source revision was recorded for reproducibility:

```text
2a3ef81f189ca95d5c1996a28ed7af9734f5cfb4
```

The build commands were:

```bash
cd ~/UERANSIM
make -j4
```

`cd` changes the Terminal's current directory. `make -j4` allows up to four
compilation tasks to run in parallel.

### 7.4 Built Programs

The build produced:

```text
~/UERANSIM/build/nr-gnb
~/UERANSIM/build/nr-ue
~/UERANSIM/build/nr-cli
```

All three report:

```text
v3.3.0
```

They were not copied into a global command directory, so later commands must
use their documented paths or run from `~/UERANSIM/build`.

UERANSIM's version option prints the correct version but may return a nonzero
status afterward. Each executable was checked independently, so that behaviour
did not hide the UE or CLI result.

### 7.5 UERANSIM Is Not a Background Service

Unlike Open5GS, UERANSIM was not registered as a systemd service.

Therefore:

- UERANSIM is installed because its executables exist.
- `nr-gnb` and `nr-ue` are not currently running.
- They will not start automatically after reboot.
- Later phases will start them deliberately with selected YAML files.

This is important because starting them before the shared values match would
create avoidable connection and authentication failures.

### 7.6 Configuration Templates

The official Open5GS examples were copied to:

```text
configs/ueransim/open5gs-gnb.yaml
configs/ueransim/open5gs-ue.yaml
```

They are templates, not yet a confirmed baseline.

The key relationships are:

| Value | Where it appears | Why it must match |
| --- | --- | --- |
| MCC and MNC | UE, gNB, and Open5GS | Together they identify the PLMN |
| TAC | gNB and AMF | Identifies the tracking area |
| `linkIp` | gNB | Address used by the simulated radio link |
| `gnbSearchList` | UE | Must point to the gNB `linkIp` |
| `ngapIp` | gNB | Local endpoint used for N2 |
| AMF address | gNB | Must point to the core's N2 listener |
| SUPI/IMSI | UE and Open5GS subscriber | Identifies the subscriber |
| Key | UE and Open5GS subscriber | Used in authentication calculations |
| OP or OPC | UE and Open5GS subscriber | Must match the selected authentication form |
| Authentication AMF | UE and subscriber | Authentication field; not the AMF network function |
| DNN/APN | UE and core session configuration | Identifies the requested data network |
| S-NSSAI SST | UE, gNB, core, and subscriber | Identifies the slice/service type |
| S-NSSAI SD | Components that use an SD | Optionally distinguishes slices with the same SST |

### 7.7 Phase 4 Result

UERANSIM 3.3.0 is built, all three executables are verified, the two required
configuration templates exist, and the matching rules are documented.

## 8. What Starts Automatically

After an ordinary Ubuntu reboot:

| Component | Expected state |
| --- | --- |
| MongoDB | Starts automatically because `mongod` is enabled |
| Open5GS functions | Start automatically because their services are enabled |
| `ogstun` | Created as part of the Open5GS setup |
| UERANSIM gNB | Does not start automatically |
| UERANSIM UE | Does not start automatically |
| `uesimtun0` | Does not exist until a UE establishes a PDU session |

To check the core without changing anything:

```bash
systemctl is-active mongod
systemctl is-active open5gs-nrfd
systemctl is-active open5gs-amfd
systemctl is-active open5gs-smfd
systemctl is-active open5gs-upfd
```

Each should print `active`.

## 9. How to Read Common Linux Commands

```bash
sudo apt install package-name
```

- `sudo`: use administrative permission.
- `apt`: use Ubuntu's package manager.
- `install`: install the named package.

```bash
systemctl is-active open5gs-amfd
```

- `systemctl`: communicate with systemd.
- `is-active`: ask whether the service is running now.
- `open5gs-amfd`: the AMF service name.

```bash
ss -ln
```

- `ss`: inspect Linux network sockets.
- `-l`: show listening sockets.
- `-n`: show numeric addresses and ports.

```bash
tail -f /var/log/open5gs/amf.log
```

- `tail`: show the end of a file.
- `-f`: continue displaying new lines.
- The path selects the AMF log.
- Press `Ctrl+C` to stop following the file.

## 10. Common Beginner Confusions

### Installed Does Not Always Mean Running

Open5GS is installed, running, and enabled. UERANSIM is installed but not
running and not enabled as a boot service.

### AMF Can Mean Two Different Things

In architecture discussions, AMF means **Access and Mobility Management
Function**.

Inside UE authentication configuration, the `amf` field means
**Authentication Management Field**. It is a different concept.

### APN and DNN

UERANSIM uses an `apn` key in its YAML session configuration. In the 5G Core,
the corresponding network name is normally called a DNN. The text value must
agree even though the field names differ.

### A Listening AMF Does Not Mean a gNB Is Connected

The AMF listening on SCTP port 38412 means it is ready to accept a gNB. It does
not prove that a gNB has connected. That will be verified in a later phase.

### A Running Core Does Not Mean a UE Is Registered

The core can be healthy with zero subscribers and zero UEs. Registration needs
a subscriber record and matching UE, gNB, and core configuration.

### Loopback Addresses Are Still Separate Endpoints

`127.0.0.4`, `127.0.0.5`, and `127.0.0.7` all refer to the same computer, but
Linux treats them as different local addresses. This lets SMF, AMF, and UPF
have distinct endpoints.

## 11. Current Boundary

Phases 1 through 4 prepared and verified the project, host, core, and simulator.
They did not prove end-to-end 5G operation.

The next phase must create one configuration map covering:

```text
MCC
MNC
TAC
AMF address
gNB link, N2, and N3 addresses
SUPI/IMSI
authentication key
OP or OPC
authentication AMF
DNN
S-NSSAI SST
S-NSSAI SD, if used
```

Only after those values are checked across every component should the gNB and
UE be started.

## 12. Related Project Documentation

- [Project overview](../00_project_overview.md)
- [Environment and installation record](../01_environment_setup.md)
- [5G Core concepts](../02_5g_core_concepts.md)
- [UERANSIM configuration guide](../../configs/ueransim/README.md)
- [Main project README](../../README.md)

# Project Overview

## What This Project Is

This project is a local 5G Standalone lab. It will use Open5GS as the 5G Core and UERANSIM as the simulated 5G radio side.

In simple terms:

- The simulated UE acts like a test phone.
- The simulated gNB acts like a test 5G base station.
- Open5GS acts like the mobile core network.
- Wireshark and tshark will prove what happened by showing packets.
- Python scripts will later check whether the lab is working.

## What This Project Is Not

This is not a commercial mobile network. It is not connected to a real carrier. It must not contain real subscriber secrets.

## Phase 1 Goal

Phase 1 creates the repository shell. That means the project folder, Git repository, README, `.gitignore`, documentation folder, and placeholder folders exist before any software installation begins.

## Lab-Only Data Rule

Use only fake subscriber information in this repository. If a value looks like a secret, key, token, or production identifier, do not commit it.


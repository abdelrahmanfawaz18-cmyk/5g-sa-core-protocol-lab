#!/usr/bin/env bash

set -Eeuo pipefail

echo "IPv4 forwarding:"
sysctl net.ipv4.ip_forward

echo
echo "UPF interface local-source validation:"
sysctl net.ipv4.conf.ogstun.accept_local

echo
echo "UPF-side tunnel interface:"
ip -brief address show ogstun

echo
echo "Main routing table:"
ip route

echo
echo "Policy-routing rules:"
ip rule show

echo
echo "IPv4 FORWARD chain:"
sudo iptables -L FORWARD -n -v --line-numbers

echo
echo "IPv4 NAT POSTROUTING chain:"
sudo iptables -t nat -L POSTROUTING -n -v --line-numbers

echo
echo "Ubuntu firewall state:"
sudo ufw status verbose

echo
echo "UE data-network inspection complete."

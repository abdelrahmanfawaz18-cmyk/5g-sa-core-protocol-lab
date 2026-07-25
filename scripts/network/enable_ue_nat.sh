#!/usr/bin/env bash

set -Eeuo pipefail

ue_subnet='10.45.0.0/16'
upf_interface='ogstun'

if ! ip link show "$upf_interface" >/dev/null 2>&1; then
  echo "ERROR: required UPF interface $upf_interface does not exist." >&2
  exit 1
fi

echo "This script enables runtime forwarding for the isolated UE subnet."
echo "UE subnet:    $ue_subnet"
echo "UPF interface: $upf_interface"
echo

sudo -v

if [[ "$(sysctl -n net.ipv4.ip_forward)" != "1" ]]; then
  sudo sysctl -w net.ipv4.ip_forward=1
else
  echo "IPv4 forwarding is already enabled."
fi

if sudo iptables -C FORWARD -i "$upf_interface" -s "$ue_subnet" -j ACCEPT 2>/dev/null; then
  echo "Outbound UE forwarding rule already exists."
else
  sudo iptables -I FORWARD 1 -i "$upf_interface" -s "$ue_subnet" -j ACCEPT
  echo "Added outbound UE forwarding rule."
fi

if sudo iptables -C FORWARD -o "$upf_interface" -d "$ue_subnet" \
  -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null; then
  echo "Return UE forwarding rule already exists."
else
  sudo iptables -I FORWARD 1 -o "$upf_interface" -d "$ue_subnet" \
    -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
  echo "Added return UE forwarding rule."
fi

if sudo iptables -t nat -C POSTROUTING -s "$ue_subnet" \
  ! -o "$upf_interface" -j MASQUERADE 2>/dev/null; then
  echo "UE masquerade rule already exists."
else
  sudo iptables -t nat -A POSTROUTING -s "$ue_subnet" \
    ! -o "$upf_interface" -j MASQUERADE
  echo "Added UE masquerade rule."
fi

echo
echo "Installed Phase 7 rules:"
sudo iptables -S FORWARD | grep -F "$ue_subnet"
sudo iptables -t nat -S POSTROUTING | grep -F "$ue_subnet"

echo
echo "These runtime rules are not made persistent across reboot by this script."

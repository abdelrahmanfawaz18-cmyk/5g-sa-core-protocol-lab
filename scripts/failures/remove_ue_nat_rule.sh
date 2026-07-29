#!/usr/bin/env bash

set -Eeuo pipefail

ue_subnet='10.45.0.0/16'
upf_interface='ogstun'
expected_nat_rule="-A POSTROUTING -s $ue_subnet ! -o $upf_interface -j MASQUERADE"

if ! ip link show "$upf_interface" >/dev/null 2>&1; then
  echo "ERROR: required UPF interface $upf_interface does not exist." >&2
  exit 1
fi

echo "This controlled failure removes only the lab UE masquerade rule."
echo "UE subnet:     $ue_subnet"
echo "UPF interface: $upf_interface"
echo

sudo -v

if [[ "$(sysctl -n net.ipv4.ip_forward)" != "1" ]]; then
  echo "ERROR: IPv4 forwarding is not enabled; baseline is not ready." >&2
  exit 1
fi

if ! sudo iptables -C FORWARD -i "$upf_interface" -s "$ue_subnet" \
  -j ACCEPT 2>/dev/null; then
  echo "ERROR: expected outbound UE forwarding rule is missing." >&2
  exit 1
fi

if ! sudo iptables -C FORWARD -o "$upf_interface" -d "$ue_subnet" \
  -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null; then
  echo "ERROR: expected return UE forwarding rule is missing." >&2
  exit 1
fi

nat_rule_count="$(
  sudo iptables -t nat -S POSTROUTING |
    grep -Fxc -- "$expected_nat_rule" || true
)"

if [[ "$nat_rule_count" != "1" ]]; then
  echo "ERROR: expected exactly one lab masquerade rule, found $nat_rule_count." >&2
  echo "Run ./scripts/network/enable_ue_nat.sh and inspect the result first." >&2
  exit 1
fi

sudo iptables -t nat -D POSTROUTING -s "$ue_subnet" \
  ! -o "$upf_interface" -j MASQUERADE

if sudo iptables -t nat -C POSTROUTING -s "$ue_subnet" \
  ! -o "$upf_interface" -j MASQUERADE 2>/dev/null; then
  echo "ERROR: the lab masquerade rule is still present." >&2
  exit 1
fi

if [[ "$(sysctl -n net.ipv4.ip_forward)" != "1" ]] ||
  ! sudo iptables -C FORWARD -i "$upf_interface" -s "$ue_subnet" \
    -j ACCEPT 2>/dev/null ||
  ! sudo iptables -C FORWARD -o "$upf_interface" -d "$ue_subnet" \
    -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null; then
  echo "ERROR: an unrelated forwarding prerequisite changed unexpectedly." >&2
  echo "Restore the lab with ./scripts/network/enable_ue_nat.sh." >&2
  exit 1
fi

echo "Removed exactly one UE masquerade rule."
echo "IPv4 forwarding remains enabled."
echo "Both scoped UE forwarding rules remain installed."
echo
echo "The controlled missing-NAT state is active."
echo "Restore it immediately after the test with:"
echo "  ./scripts/network/enable_ue_nat.sh"

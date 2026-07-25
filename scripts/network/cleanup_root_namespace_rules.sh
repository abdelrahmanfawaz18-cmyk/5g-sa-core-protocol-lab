#!/usr/bin/env bash

set -Eeuo pipefail

upf_interface='ogstun'
ueransim_table='rt_uesimtun0'

echo "This script removes temporary same-host UE routing workarounds."
echo "The forwarding and NAT rules required by the isolated UE remain installed."
echo

sudo -v

if ip rule show | grep -Eq '^[0-9]+:.*iif ogstun lookup main$'; then
  sudo ip rule del priority 100
  echo "Removed the temporary UPF input routing rule."
else
  echo "The temporary UPF input routing rule is not present."
fi

if [[ "$(sysctl -n net.ipv4.conf.ogstun.accept_local)" != "0" ]]; then
  sudo sysctl -w net.ipv4.conf.ogstun.accept_local=0
  echo "Restored normal local-source validation on ogstun."
else
  echo "Local-source validation on ogstun is already at its normal setting."
fi

mapfile -t ueransim_rule_priorities < <(
  ip rule show |
    awk -v table="$ueransim_table" '
      $0 ~ ("lookup " table "$") {
        gsub(":", "", $1)
        print $1
      }
    '
)

if ((${#ueransim_rule_priorities[@]})); then
  for priority in "${ueransim_rule_priorities[@]}"; do
    sudo ip rule del priority "$priority"
  done
  echo "Removed stale root-namespace UERANSIM source rules."
else
  echo "No stale root-namespace UERANSIM source rules are present."
fi

sudo ip route flush table "$ueransim_table" 2>/dev/null || true

echo
echo "Remaining relevant policy-routing rules:"
if ! ip rule show | grep -E 'iif ogstun lookup main|lookup rt_uesimtun0'; then
  echo "None"
fi

echo
echo "Diagnostic routing workarounds removed."

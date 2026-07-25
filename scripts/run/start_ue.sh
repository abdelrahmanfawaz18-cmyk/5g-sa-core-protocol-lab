#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
ueransim_root="${UERANSIM_ROOT:-${HOME}/UERANSIM}"
ue_binary="$ueransim_root/build/nr-ue"
ue_config="$repository_root/configs/ueransim/open5gs-ue.yaml"

if [[ ! -x "$ue_binary" ]]; then
  echo "ERROR: UERANSIM UE executable was not found at:" >&2
  echo "  $ue_binary" >&2
  echo "Set UERANSIM_ROOT if UERANSIM is installed elsewhere." >&2
  exit 1
fi

if [[ ! -r "$ue_config" ]]; then
  echo "ERROR: UE configuration is not readable:" >&2
  echo "  $ue_config" >&2
  exit 1
fi

if pgrep -x nr-ue >/dev/null; then
  echo "ERROR: nr-ue is already running." >&2
  exit 1
fi

echo "Starting UERANSIM UE in the foreground."
echo "Executable:    $ue_binary"
echo "Configuration: $ue_config"
echo "Root privileges are required to create the UE TUN interface."
echo "Stop it with Ctrl+C."
echo

if ((EUID == 0)); then
  exec "$ue_binary" -c "$ue_config"
else
  exec sudo -- "$ue_binary" -c "$ue_config"
fi

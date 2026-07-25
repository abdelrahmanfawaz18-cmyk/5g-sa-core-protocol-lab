#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
ueransim_root="${UERANSIM_ROOT:-${HOME}/UERANSIM}"
gnb_binary="$ueransim_root/build/nr-gnb"
gnb_config="$repository_root/configs/ueransim/open5gs-gnb.yaml"

if [[ ! -x "$gnb_binary" ]]; then
  echo "ERROR: UERANSIM gNB executable was not found at:" >&2
  echo "  $gnb_binary" >&2
  echo "Set UERANSIM_ROOT if UERANSIM is installed elsewhere." >&2
  exit 1
fi

if [[ ! -r "$gnb_config" ]]; then
  echo "ERROR: gNB configuration is not readable:" >&2
  echo "  $gnb_config" >&2
  exit 1
fi

if pgrep -x nr-gnb >/dev/null; then
  echo "ERROR: nr-gnb is already running." >&2
  exit 1
fi

echo "Starting UERANSIM gNB in the foreground."
echo "Executable:    $gnb_binary"
echo "Configuration: $gnb_config"
echo "Stop it with Ctrl+C."
echo

exec "$gnb_binary" -c "$gnb_config"

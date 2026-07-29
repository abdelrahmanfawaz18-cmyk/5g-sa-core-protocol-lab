#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
ueransim_root="${UERANSIM_ROOT:-${HOME}/UERANSIM}"
ue_binary="$ueransim_root/build/nr-ue"
ue_config="$repository_root/configs/failures/wrong_subscriber_key/open5gs-ue-wrong-key.yaml"
baseline_config="$repository_root/configs/ueransim/open5gs-ue.yaml"
default_log="$repository_root/captures/failures/wrong_subscriber_key/ue_console_raw.log"
log_file="${1:-$default_log}"
log_directory="$(dirname -- "$log_file")"

if [[ ! -x "$ue_binary" ]]; then
  echo "ERROR: UERANSIM UE executable was not found at:" >&2
  echo "  $ue_binary" >&2
  echo "Set UERANSIM_ROOT if UERANSIM is installed elsewhere." >&2
  exit 1
fi

if [[ ! -r "$ue_config" || ! -r "$baseline_config" ]]; then
  echo "ERROR: a required wrong-key or baseline UE configuration is unreadable." >&2
  exit 1
fi

if pgrep -x nr-ue >/dev/null; then
  echo "ERROR: nr-ue is already running." >&2
  echo "Stop the existing UE before starting the controlled scenario." >&2
  exit 1
fi

if [[ -e "$log_file" ]]; then
  echo "ERROR: refusing to overwrite existing raw UE log:" >&2
  echo "  $log_file" >&2
  exit 1
fi

mkdir -p "$log_directory"

echo "Starting the isolated wrong-subscriber-key UE scenario."
echo "Executable:        $ue_binary"
echo "Failure config:    $ue_config"
echo "Baseline config:   $baseline_config"
echo "Intentional fault: final synthetic key digit C changed to D"
echo "Raw local log:     $log_file"
echo
echo "Expected boundary:"
echo "  Cell selection, RRC, and Registration Request should succeed."
echo "  5G-AKA authentication should fail before NAS security."
echo
echo "Root privileges are required to create a UE TUN interface if a session"
echo "unexpectedly succeeds. Stop the UE with Ctrl+C after the failure."
echo

set +e
sudo "$ue_binary" -c "$ue_config" 2>&1 | tee "$log_file"
ue_status=${PIPESTATUS[0]}
set -e

exit "$ue_status"

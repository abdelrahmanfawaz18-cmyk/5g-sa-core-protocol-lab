#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
ueransim_root="${UERANSIM_ROOT:-${HOME}/UERANSIM}"
gnb_binary="$ueransim_root/build/nr-gnb"
gnb_config="$repository_root/configs/failures/wrong_tac/open5gs-gnb-wrong-tac.yaml"
baseline_config="$repository_root/configs/ueransim/open5gs-gnb.yaml"
default_log="$repository_root/captures/failures/wrong_tac/gnb_console_raw.log"
log_file="${1:-$default_log}"
log_directory="$(dirname -- "$log_file")"

if [[ ! -x "$gnb_binary" ]]; then
  echo "ERROR: UERANSIM gNB executable was not found at:" >&2
  echo "  $gnb_binary" >&2
  echo "Set UERANSIM_ROOT if UERANSIM is installed elsewhere." >&2
  exit 1
fi

if [[ ! -r "$gnb_config" || ! -r "$baseline_config" ]]; then
  echo "ERROR: a required wrong-TAC or baseline gNB configuration is unreadable." >&2
  exit 1
fi

if pgrep -x nr-gnb >/dev/null; then
  echo "ERROR: nr-gnb is already running." >&2
  echo "Stop the existing gNB before starting the controlled scenario." >&2
  exit 1
fi

if [[ -e "$log_file" ]]; then
  echo "ERROR: refusing to overwrite existing raw gNB log:" >&2
  echo "  $log_file" >&2
  exit 1
fi

mkdir -p "$log_directory"

echo "Starting the isolated wrong-TAC gNB scenario."
echo "Executable:        $gnb_binary"
echo "Failure config:    $gnb_config"
echo "Baseline config:   $baseline_config"
echo "Intentional fault: gNB TAC 2; AMF baseline TAC 1"
echo "Raw local log:     $log_file"
echo
echo "Expected boundary:"
echo "  NG Setup may succeed because the PLMN is correct."
echo "  If it succeeds, UE registration will test whether TAC 2 is served."
echo
echo "Keep this gNB running if NG Setup succeeds."
echo "Stop it with Ctrl+C after the UE result has been captured."
echo

set +e
"$gnb_binary" -c "$gnb_config" 2>&1 | tee "$log_file"
gnb_status=${PIPESTATUS[0]}
set -e

exit "$gnb_status"

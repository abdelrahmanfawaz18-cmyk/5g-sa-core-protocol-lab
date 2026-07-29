#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
default_capture="$repository_root/captures/failures/wrong_tac/wrong_tac_raw.pcap"
capture_file="${1:-$default_capture}"
capture_directory="$(dirname -- "$capture_file")"
capture_filter='sctp port 38412'

if [[ -e "$capture_file" ]]; then
  echo "ERROR: refusing to overwrite existing capture:" >&2
  echo "  $capture_file" >&2
  exit 1
fi

mkdir -p "$capture_directory"

echo "Capturing the wrong-TAC N2 experiment in the foreground."
echo "Interface: any"
echo "Filter:    SCTP port 38412"
echo "Output:    $capture_file"
echo "Stop the capture with Ctrl+C after the observed failure is complete."
echo

if command -v dumpcap >/dev/null &&
  dumpcap -D >/dev/null 2>&1; then
  exec dumpcap -q -P -i any -s 0 -f "$capture_filter" -w "$capture_file"
fi

echo "dumpcap capture permission is unavailable; trying tcpdump with sudo."
exec sudo tcpdump -i any -s 0 -U -nn -w "$capture_file" "$capture_filter"

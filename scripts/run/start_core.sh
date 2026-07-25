#!/usr/bin/env bash

set -Eeuo pipefail

services=(
  mongod
  open5gs-nrfd
  open5gs-amfd
  open5gs-smfd
  open5gs-upfd
  open5gs-ausfd
  open5gs-udmd
  open5gs-udrd
  open5gs-pcfd
  open5gs-nssfd
)

inactive_services=()

for service in "${services[@]}"; do
  if ! systemctl is-active --quiet "$service"; then
    inactive_services+=("$service")
  fi
done

if ((${#inactive_services[@]} > 0)); then
  echo "Starting inactive MongoDB/Open5GS services:"
  printf '  %s\n' "${inactive_services[@]}"
  sudo systemctl start "${inactive_services[@]}"
else
  echo "MongoDB and all required Open5GS services are already active."
fi

echo
echo "Service verification:"
for service in "${services[@]}"; do
  state="$(systemctl is-active "$service")"
  printf '  %-18s %s\n' "$service" "$state"
  if [[ "$state" != "active" ]]; then
    echo "ERROR: $service is not active." >&2
    exit 1
  fi
done

echo
echo "AMF N2 listener:"
if ! ss -H -lnA sctp | grep -F '127.0.0.5:38412'; then
  echo "ERROR: AMF is not listening on 127.0.0.5:38412/SCTP." >&2
  exit 1
fi

echo
echo "Core readiness check passed."

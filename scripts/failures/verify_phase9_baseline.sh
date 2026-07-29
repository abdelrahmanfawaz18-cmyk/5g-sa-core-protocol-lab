#!/usr/bin/env bash

set -Eeuo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/../.." && pwd)"
ueransim_root="${UERANSIM_ROOT:-${HOME}/UERANSIM}"
gnb_binary="$ueransim_root/build/nr-gnb"
ue_binary="$ueransim_root/build/nr-ue"
gnb_config="$repository_root/configs/ueransim/open5gs-gnb.yaml"
ue_config="$repository_root/configs/ueransim/open5gs-ue.yaml"

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

failures=0

pass() {
  printf 'PASS: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

echo "Phase 9 known-good baseline preflight"
echo "Repository: $repository_root"
echo

kernel_release="$(uname -r)"
if [[ "$kernel_release" == 6.17.* ]]; then
  pass "working kernel family is active ($kernel_release)"
else
  fail "kernel is $kernel_release; this lab requires the verified 6.17.x family"
fi

for service in "${services[@]}"; do
  if systemctl is-active --quiet "$service"; then
    pass "$service is active"
  else
    fail "$service is not active"
  fi
done

if ss -H -lnA sctp | grep -Fq '127.0.0.5:38412'; then
  pass "AMF listens on 127.0.0.5:38412/SCTP"
else
  fail "AMF SCTP listener 127.0.0.5:38412 was not found"
fi

if ip link show dev ogstun >/dev/null 2>&1; then
  pass "UPF-side ogstun interface exists"
else
  fail "UPF-side ogstun interface does not exist"
fi

if [[ -x "$gnb_binary" ]]; then
  pass "UERANSIM gNB executable is available"
else
  fail "UERANSIM gNB executable is missing: $gnb_binary"
fi

if [[ -x "$ue_binary" ]]; then
  pass "UERANSIM UE executable is available"
else
  fail "UERANSIM UE executable is missing: $ue_binary"
fi

if [[ -r "$gnb_config" && -r "$ue_config" ]]; then
  pass "known-good UERANSIM configurations are readable"
else
  fail "one or both known-good UERANSIM configurations are unreadable"
fi

if git -C "$repository_root" diff --quiet -- \
  configs/ueransim/open5gs-gnb.yaml \
  configs/ueransim/open5gs-ue.yaml &&
  git -C "$repository_root" diff --cached --quiet -- \
  configs/ueransim/open5gs-gnb.yaml \
  configs/ueransim/open5gs-ue.yaml; then
  pass "known-good UERANSIM configurations have no uncommitted changes"
else
  fail "known-good UERANSIM configurations contain uncommitted changes"
fi

if grep -Eq "^mcc: '999'" "$gnb_config" &&
  grep -Eq "^mnc: '70'" "$gnb_config" &&
  grep -Eq '^tac: 1' "$gnb_config"; then
  pass "gNB baseline identity is PLMN 999-70, TAC 1"
else
  fail "gNB baseline identity does not match PLMN 999-70, TAC 1"
fi

if grep -Eq "^mcc: '999'" "$ue_config" &&
  grep -Eq "^mnc: '70'" "$ue_config" &&
  grep -Eq "^[[:space:]]+apn: 'internet'" "$ue_config"; then
  pass "UE baseline uses PLMN 999-70 and DNN internet"
else
  fail "UE baseline identity or DNN does not match the known-good contract"
fi

if pgrep -x nr-gnb >/dev/null; then
  fail "nr-gnb is already running; stop it before a controlled test"
else
  pass "no nr-gnb process is running"
fi

if pgrep -x nr-ue >/dev/null; then
  fail "nr-ue is already running; stop it before a controlled test"
else
  pass "no nr-ue process is running"
fi

if command -v tshark >/dev/null; then
  pass "tshark is available"
else
  fail "tshark is not available"
fi

if command -v dumpcap >/dev/null || command -v tcpdump >/dev/null; then
  pass "at least one packet-capture program is available"
else
  fail "neither dumpcap nor tcpdump is available"
fi

echo
if ((failures > 0)); then
  echo "Phase 9 baseline preflight FAILED with $failures problem(s)." >&2
  echo "Do not start a failure experiment until every check passes." >&2
  exit 1
fi

echo "Phase 9 baseline preflight PASSED."
echo "The host is ready for one controlled failure experiment."

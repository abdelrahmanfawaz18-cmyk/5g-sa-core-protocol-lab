# Open5GS Baseline Configuration

These YAML files are reviewed Phase 5 copies of the active sections under
`/etc/open5gs/` for Open5GS `2.8.0~noble5`.

They document the single-host baseline:

- PLMN `999-70`
- TAC `1`
- SST `1` with no SD
- AMF N2 at `127.0.0.5`
- SMF PFCP at `127.0.0.4`
- UPF PFCP and GTP-U at `127.0.0.7`
- UE IPv4 subnet `10.45.0.0/16`
- UE gateway `10.45.0.1`

The runtime services still read `/etc/open5gs/*.yaml`. Editing a repository
copy does not modify the running system.

Subscriber authentication data is stored in MongoDB rather than these YAML
files. The synthetic subscriber values are documented in
`docs/configuration_map.md` and match the UERANSIM UE baseline.

The copies intentionally omit the large commented example sections shipped in
the package while retaining every active key from the corresponding runtime
section.

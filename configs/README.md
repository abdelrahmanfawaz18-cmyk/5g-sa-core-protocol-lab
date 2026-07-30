# Configurations

This directory contains documented, lab-only copies of configurations used by the project.

The validated UERANSIM baseline and its field guide are under `ueransim/`.
Reviewed copies of the active Open5GS baseline sections are under `open5gs/`.
System configuration remains under `/etc/open5gs/`.

Controlled fault configuration variants are under `failures/`. They must
never replace the known-good files. Each variant changes one documented value
so its protocol effect can be isolated and reversed.

Real subscriber credentials and production network data must never be stored
here.

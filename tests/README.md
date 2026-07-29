# Tests

The test suite verifies the Python lab validator without requiring a running
5G core, gNB, UE, root privilege, or external network.

Run it from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover:

- required-command discovery and missing-command failure;
- UERANSIM binary discovery outside `PATH`;
- combined TCP, UDP, and SCTP endpoint inspection;
- SCTP success versus NG Setup success or failure;
- successful UE registration and PDU-session parsing;
- authentication failure parsing;
- successful registration with wrong-DNN session failure;
- namespace auto-discovery;
- UE tunnel address and default-route validation;
- successful and failed UE connectivity;
- deterministic Markdown rendering and file output;
- first-failure suggested-action selection;
- external-command timeout handling.

Controlled fake command results keep the tests deterministic. The separate
live run validates the real Open5GS/UERANSIM environment.

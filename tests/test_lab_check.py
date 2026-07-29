"""Unit tests for the read-only 5G SA lab validator."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from tools.lab_check import (
    FAIL,
    PASS,
    CheckResult,
    CommandResult,
    CommandRunner,
    check_connectivity,
    check_expected_ports,
    check_required_commands,
    check_ue_tunnel,
    discover_binary,
    discover_namespace,
    display_path,
    overall_status,
    parse_gnb_log,
    parse_ue_log,
    render_report,
    suggested_next_action,
    write_report,
)


class FakeRunner:
    """Return controlled command results without touching the host."""

    def __init__(self, handler):
        self.handler = handler
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv, *, timeout=None):
        command = tuple(argv)
        self.calls.append(command)
        return self.handler(command, timeout)


class BinaryDiscoveryTests(unittest.TestCase):
    def test_ueransim_binary_is_found_outside_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "build" / "nr-ue"
            binary.parent.mkdir()
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o755)

            found = discover_binary("nr-ue", root, which=lambda _name: None)

            self.assertEqual(found, binary)

    def test_missing_command_is_reported_as_failure(self):
        def finder(name):
            return None if name == "tshark" else f"/usr/bin/{name}"

        result = check_required_commands(Path("/unused"), which=finder)

        self.assertEqual(result.status, FAIL)
        self.assertIn("tshark", result.evidence)

    def test_home_path_is_rendered_without_account_name(self):
        result = display_path(Path.home() / "UERANSIM" / "build" / "nr-ue")

        self.assertEqual(result, "~/UERANSIM/build/nr-ue")


class LogParserTests(unittest.TestCase):
    def test_gnb_parser_requires_sctp_and_ng_setup(self):
        result = parse_gnb_log(
            "SCTP connection established\nNG Setup procedure is successful\n"
        )

        self.assertEqual(result.status, PASS)
        self.assertIn("NG Setup", result.evidence)

    def test_gnb_parser_reports_ng_setup_failure(self):
        result = parse_gnb_log(
            "SCTP connection established\n"
            "NG Setup procedure is failed. Cause: unknown-PLMN-or-SNPN\n"
        )

        self.assertEqual(result.status, FAIL)
        self.assertIn("unknown-PLMN-or-SNPN", result.evidence)

    def test_ue_parser_separates_registration_and_session_success(self):
        registration, session = parse_ue_log(
            "Security Mode Command received\n"
            "Initial Registration is successful\n"
            "PDU Session establishment is successful PSI[1]\n"
        )

        self.assertEqual(registration.status, PASS)
        self.assertEqual(session.status, PASS)

    def test_ue_parser_detects_authentication_failure(self):
        registration, session = parse_ue_log(
            "Authentication Request received\n"
            "Sending Authentication Failure with cause [MAC_FAILURE]\n"
        )

        self.assertEqual(registration.status, FAIL)
        self.assertIn("MAC_FAILURE", registration.evidence)
        self.assertEqual(session.status, FAIL)

    def test_ue_parser_keeps_registration_pass_when_dnn_fails(self):
        registration, session = parse_ue_log(
            "Initial Registration is successful\n"
            "MM status received with cause "
            "[DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED]\n"
        )

        self.assertEqual(registration.status, PASS)
        self.assertEqual(session.status, FAIL)
        self.assertIn("DNN_NOT_SUPPORTED", session.evidence)


class NamespaceAndConnectivityTests(unittest.TestCase):
    def test_one_namespace_is_auto_detected(self):
        runner = FakeRunner(
            lambda command, _timeout: CommandResult(
                command,
                0,
                "ueransim-999700000000001-internet-psi1 (id: 0)",
            )
        )

        namespace, error = discover_namespace(runner, None)

        self.assertIsNone(error)
        self.assertEqual(
            namespace, "ueransim-999700000000001-internet-psi1"
        )

    def test_tunnel_requires_address_and_default_route(self):
        def handler(command, _timeout):
            if command[-2:] == ("show", "uesimtun0"):
                return CommandResult(
                    command,
                    0,
                    "uesimtun0 UNKNOWN 10.45.0.2/24",
                )
            return CommandResult(
                command,
                0,
                "default dev uesimtun0 scope link",
            )

        result = check_ue_tunnel(FakeRunner(handler), "test-namespace")

        self.assertEqual(result.status, PASS)
        self.assertIn("10.45.0.2", result.evidence)
        self.assertNotIn("fe80", result.evidence)

    def test_connectivity_uses_packet_summary(self):
        runner = FakeRunner(
            lambda command, _timeout: CommandResult(
                command,
                0,
                "3 packets transmitted, 3 received, 0% packet loss",
            )
        )

        result = check_connectivity(runner, "test-namespace", "8.8.8.8", 3)

        self.assertEqual(result.status, PASS)
        self.assertIn("0% packet loss", result.evidence)

    def test_connectivity_failure_suggests_user_plane_checks(self):
        runner = FakeRunner(
            lambda command, _timeout: CommandResult(
                command,
                1,
                "3 packets transmitted, 0 received, 100% packet loss",
            )
        )

        result = check_connectivity(runner, "test-namespace", "8.8.8.8", 3)

        self.assertEqual(result.status, FAIL)
        self.assertIn("100% packet loss", result.evidence)
        self.assertIn("GTP-U", result.action)


class PortCheckTests(unittest.TestCase):
    def test_tcp_udp_and_sctp_socket_views_are_combined(self):
        def handler(command, _timeout):
            if "--sctp" in command:
                return CommandResult(
                    command,
                    0,
                    "sctp LISTEN 0 5 127.0.0.5:38412 0.0.0.0:*",
                )
            return CommandResult(
                command,
                0,
                "\n".join(
                    (
                        "udp UNCONN 0 0 127.0.0.7:8805 0.0.0.0:*",
                        "udp UNCONN 0 0 127.0.0.7:2152 0.0.0.0:*",
                        "tcp LISTEN 0 5 127.0.0.5:7777 0.0.0.0:*",
                        "tcp LISTEN 0 5 127.0.0.1:27017 0.0.0.0:*",
                    )
                ),
            )

        result = check_expected_ports(FakeRunner(handler))

        self.assertEqual(result.status, PASS)
        self.assertIn("38412", result.evidence)


class ReportTests(unittest.TestCase):
    def test_report_generation_is_deterministic(self):
        checks = [CheckResult("Example", PASS, "Synthetic evidence")]
        generated = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)

        report = render_report(
            checks,
            {"Python": "3.x"},
            generated=generated,
        )

        self.assertIn("Overall status: **PASS**", report)
        self.assertIn("2026-07-29 12:00:00 UTC", report)
        self.assertIn("| Example | **PASS** | Synthetic evidence |", report)

    def test_report_is_written_to_requested_location(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "report.md"

            write_report(path, "# Report\n")

            self.assertEqual(path.read_text(encoding="utf-8"), "# Report\n")

    def test_first_failure_controls_suggested_action(self):
        checks = [
            CheckResult("Commands", PASS, "found"),
            CheckResult("AMF", FAIL, "inactive", "Start AMF."),
            CheckResult("Ping", FAIL, "loss", "Check NAT."),
        ]

        self.assertEqual(overall_status(checks), FAIL)
        self.assertEqual(suggested_next_action(checks), "AMF: Start AMF.")


class CommandRunnerTests(unittest.TestCase):
    def test_timeout_becomes_command_result(self):
        runner = CommandRunner(timeout=0.1)
        with patch(
            "tools.lab_check.subprocess.run",
            side_effect=subprocess.TimeoutExpired(("ping",), 0.1),
        ):
            result = runner.run(("ping",))

        self.assertEqual(result.returncode, 124)
        self.assertIn("timed out", result.error)


if __name__ == "__main__":
    unittest.main()

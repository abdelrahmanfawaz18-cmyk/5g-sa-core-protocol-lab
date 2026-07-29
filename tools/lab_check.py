#!/usr/bin/env python3
"""Read-only validation and Markdown reporting for the 5G SA lab."""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence


PASS = "PASS"
FAIL = "FAIL"

REQUIRED_COMMANDS = ("ip", "ping", "tcpdump", "tshark", "nr-gnb", "nr-ue")
CORE_SERVICES = (
    "mongod",
    "open5gs-nrfd",
    "open5gs-amfd",
    "open5gs-smfd",
    "open5gs-upfd",
    "open5gs-ausfd",
    "open5gs-udmd",
    "open5gs-udrd",
    "open5gs-pcfd",
    "open5gs-nssfd",
)
EXPECTED_PORTS = {
    "38412": "N2 SCTP",
    "8805": "N4 PFCP",
    "2152": "N3 GTP-U",
    "7777": "Open5GS SBI",
    "27017": "MongoDB",
}


@dataclass(frozen=True)
class CommandResult:
    """Result of one safely executed external command."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    error: str = ""


@dataclass(frozen=True)
class CheckResult:
    """One validation outcome rendered into the final report."""

    name: str
    status: str
    evidence: str
    action: str = "No action needed."


class CommandRunner:
    """Run commands without a shell and convert OS errors into results."""

    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout: float | None = None,
    ) -> CommandResult:
        command = tuple(str(part) for part in argv)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=self.timeout if timeout is None else timeout,
            )
        except FileNotFoundError:
            return CommandResult(
                command,
                127,
                error=f"command not found: {command[0]}",
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command,
                124,
                error=f"command timed out after {timeout or self.timeout:g}s",
            )
        except OSError as exc:
            return CommandResult(command, 126, error=f"OS error: {exc}")

        return CommandResult(
            command,
            completed.returncode,
            completed.stdout.strip(),
            completed.stderr.strip(),
        )


def discover_binary(
    name: str,
    ueransim_root: Path,
    *,
    which: Callable[[str], str | None] = shutil.which,
) -> Path | None:
    """Find a command in PATH or a UERANSIM build directory."""

    path_match = which(name)
    if path_match:
        return Path(path_match)

    if name in {"nr-gnb", "nr-ue"}:
        candidate = ueransim_root / "build" / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate

    return None


def check_required_commands(
    ueransim_root: Path,
    *,
    which: Callable[[str], str | None] = shutil.which,
) -> CheckResult:
    """Confirm all roadmap-required commands are available."""

    found: list[str] = []
    missing: list[str] = []
    for name in REQUIRED_COMMANDS:
        path = discover_binary(name, ueransim_root, which=which)
        if path is None:
            missing.append(name)
        else:
            found.append(f"{name}={display_path(path)}")

    if missing:
        return CheckResult(
            "Required commands",
            FAIL,
            f"Missing: {', '.join(missing)}. Found: {', '.join(found)}",
            "Install the missing program or correct the UERANSIM root.",
        )

    return CheckResult("Required commands", PASS, "; ".join(found))


def check_core_services(runner: CommandRunner) -> CheckResult:
    """Check MongoDB and the Open5GS network-function services."""

    active: list[str] = []
    inactive: list[str] = []
    for service in CORE_SERVICES:
        result = runner.run(("systemctl", "is-active", service))
        if result.returncode == 0 and result.stdout == "active":
            active.append(service)
        else:
            detail = result.stdout or result.stderr or result.error or "inactive"
            inactive.append(f"{service} ({detail})")

    if inactive:
        return CheckResult(
            "Core services",
            FAIL,
            f"Inactive: {', '.join(inactive)}. Active: {', '.join(active)}",
            "Inspect the failed unit with systemctl status and journalctl.",
        )

    return CheckResult(
        "Core services",
        PASS,
        f"All {len(active)} required MongoDB/Open5GS services are active.",
    )


def check_expected_ports(runner: CommandRunner) -> CheckResult:
    """Confirm the core exposes its expected local protocol endpoints."""

    internet = runner.run(("ss", "-H", "-lntup"))
    sctp = runner.run(("ss", "-H", "-ln", "--sctp"))
    if internet.returncode != 0 and sctp.returncode != 0:
        detail = (
            internet.stderr
            or internet.error
            or sctp.stderr
            or sctp.error
            or "socket inspection failed"
        )
        return CheckResult(
            "Expected ports",
            FAIL,
            f"Could not inspect listening sockets: {detail}",
            "Confirm that the ss command is installed and readable.",
        )

    socket_text = "\n".join((internet.stdout, sctp.stdout))
    found: list[str] = []
    missing: list[str] = []
    for port, purpose in EXPECTED_PORTS.items():
        if re.search(rf":{re.escape(port)}(?:\s|$)", socket_text):
            found.append(f"{port} ({purpose})")
        else:
            missing.append(f"{port} ({purpose})")

    if missing:
        return CheckResult(
            "Expected ports",
            FAIL,
            f"Missing: {', '.join(missing)}. Found: {', '.join(found)}",
            "Check the network function that owns the first missing endpoint.",
        )

    return CheckResult("Expected ports", PASS, f"Listening: {', '.join(found)}")


def read_log(path: Path | None, label: str) -> tuple[str | None, CheckResult | None]:
    """Read an explicitly supplied log without exposing its full contents."""

    if path is None:
        return None, CheckResult(
            label,
            FAIL,
            "No log path was supplied.",
            f"Capture a current {label.lower()} log and pass its path.",
        )
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, CheckResult(
            label,
            FAIL,
            f"Cannot read {path}: {exc}",
            "Check the path and file permissions.",
        )
    return text, None


def parse_gnb_log(text: str) -> CheckResult:
    """Distinguish SCTP reachability from successful NGAP NG Setup."""

    if "NG Setup procedure is failed" in text:
        cause = _matching_line(text, "NG Setup procedure is failed")
        return CheckResult(
            "gNB connection",
            FAIL,
            cause,
            "Compare gNB PLMN/TAC values with the AMF served configuration.",
        )

    sctp_ok = "SCTP connection established" in text
    ng_setup_ok = "NG Setup procedure is successful" in text
    if sctp_ok and ng_setup_ok:
        return CheckResult(
            "gNB connection",
            PASS,
            "SCTP association established and NG Setup accepted.",
        )

    observed = []
    if sctp_ok:
        observed.append("SCTP established")
    if ng_setup_ok:
        observed.append("NG Setup accepted")
    evidence = ", ".join(observed) if observed else "No gNB success marker found."
    return CheckResult(
        "gNB connection",
        FAIL,
        evidence,
        "Start the baseline gNB and provide its current console log.",
    )


def parse_ue_log(text: str) -> tuple[CheckResult, CheckResult]:
    """Return separate registration and PDU-session results."""

    registration_ok = "Initial Registration is successful" in text
    session_ok = "PDU Session establishment is successful" in text

    authentication_failure = _first_marker(
        text,
        (
            "MAC_FAILURE",
            "Authentication Reject received",
            "Network failing the authentication check",
        ),
    )
    registration_failure = _first_marker(
        text,
        (
            "Registration reject received",
            "PLMN selection failure",
            "no cells in coverage",
        ),
    )
    session_failure = _first_marker(
        text,
        (
            "DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED",
            "PDU Session Establishment Reject",
            "PDU Session establishment failure",
        ),
    )

    if registration_ok:
        registration = CheckResult(
            "UE registration",
            PASS,
            "Authentication, NAS security, and initial registration completed.",
        )
    else:
        marker = authentication_failure or registration_failure
        evidence = marker or "No successful-registration marker found."
        registration = CheckResult(
            "UE registration",
            FAIL,
            evidence,
            "Inspect UE and AMF logs around authentication and registration.",
        )

    if session_ok:
        session = CheckResult(
            "PDU session",
            PASS,
            "PDU Session Establishment completed successfully.",
        )
    else:
        evidence = session_failure or "No successful PDU-session marker found."
        session = CheckResult(
            "PDU session",
            FAIL,
            evidence,
            "Check DNN, slice, subscriber, SMF, and UPF evidence.",
        )

    return registration, session


def discover_namespace(
    runner: CommandRunner,
    requested: str | None,
) -> tuple[str | None, CheckResult | None]:
    """Resolve one live UERANSIM PDU-session namespace."""

    if requested:
        return requested, None

    result = runner.run(("ip", "netns", "list"))
    if result.returncode != 0:
        detail = result.stderr or result.error or f"exit {result.returncode}"
        return None, CheckResult(
            "UE tunnel interface",
            FAIL,
            f"Could not list network namespaces: {detail}",
            "Confirm iproute2 permissions and that the UE is running.",
        )

    names = [
        line.split()[0]
        for line in result.stdout.splitlines()
        if line.startswith("ueransim-") and "-psi" in line
    ]
    if len(names) == 1:
        return names[0], None
    if not names:
        return None, CheckResult(
            "UE tunnel interface",
            FAIL,
            "No live UERANSIM PDU-session namespace was found.",
            "Start the baseline UE and wait for PDU-session establishment.",
        )
    return None, CheckResult(
        "UE tunnel interface",
        FAIL,
        f"Multiple UERANSIM namespaces found: {', '.join(names)}",
        "Pass --namespace with the intended UE session.",
    )


def check_ue_tunnel(
    runner: CommandRunner,
    namespace: str,
) -> CheckResult:
    """Inspect uesimtun0 and the UE route from its network namespace."""

    address = runner.run(
        ("sudo", "-n", "ip", "netns", "exec", namespace, "ip", "-brief", "address",
         "show", "uesimtun0")
    )
    if address.returncode != 0:
        detail = address.stderr or address.error or f"exit {address.returncode}"
        return CheckResult(
            "UE tunnel interface",
            FAIL,
            f"Cannot inspect uesimtun0 in {namespace}: {detail}",
            "Run sudo -v in this terminal and confirm the live namespace name.",
        )

    route = runner.run(
        ("sudo", "-n", "ip", "netns", "exec", namespace, "ip", "route")
    )
    address_ok = "uesimtun0" in address.stdout and "10.45." in address.stdout
    route_ok = route.returncode == 0 and "default dev uesimtun0" in route.stdout
    if address_ok and route_ok:
        ipv4_match = re.search(r"\b10\.45\.\d{1,3}\.\d{1,3}/\d{1,2}\b", address.stdout)
        compact_address = ipv4_match.group(0) if ipv4_match else "10.45.x.x"
        return CheckResult(
            "UE tunnel interface",
            PASS,
            f"uesimtun0 address {compact_address}; default route uses uesimtun0.",
        )

    evidence = (
        f"Address: {address.stdout or 'missing'}; "
        f"route: {route.stdout or route.stderr or route.error or 'missing'}"
    )
    return CheckResult(
        "UE tunnel interface",
        FAIL,
        evidence,
        "Check PDU-session acceptance and UERANSIM namespace creation.",
    )


def check_connectivity(
    runner: CommandRunner,
    namespace: str,
    target: str,
    ping_count: int,
) -> CheckResult:
    """Ping an IP from the UE namespace, not from the Ubuntu host."""

    result = runner.run(
        (
            "sudo",
            "-n",
            "ip",
            "netns",
            "exec",
            namespace,
            "ping",
            "-c",
            str(ping_count),
            "-W",
            "2",
            target,
        ),
        timeout=max(8.0, ping_count * 3.0),
    )
    summary = _ping_summary(result.stdout)
    if result.returncode == 0 and "0% packet loss" in result.stdout:
        return CheckResult(
            "UE connectivity",
            PASS,
            summary or f"{ping_count} replies received from {target}.",
        )

    detail = summary or result.stderr or result.error or f"exit {result.returncode}"
    return CheckResult(
        "UE connectivity",
        FAIL,
        detail,
        "Check the UE route, GTP-U, UPF, forwarding, and scoped NAT rule.",
    )


def collect_environment(ueransim_root: Path) -> dict[str, str]:
    """Collect concise, non-identifying environment metadata."""

    os_name = platform.system()
    os_release = Path("/etc/os-release")
    if os_release.is_file():
        for line in os_release.read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                os_name = line.partition("=")[2].strip().strip('"')
                break

    return {
        "Operating system": os_name,
        "Kernel": platform.release(),
        "Python": platform.python_version(),
        "Open5GS": "systemd-managed local services",
        "UERANSIM": display_path(ueransim_root),
    }


def overall_status(checks: Sequence[CheckResult]) -> str:
    """PASS only when every required check passes."""

    return PASS if checks and all(check.status == PASS for check in checks) else FAIL


def suggested_next_action(checks: Sequence[CheckResult]) -> str:
    """Use the first failure in dependency order as the next action."""

    for check in checks:
        if check.status == FAIL:
            return f"{check.name}: {check.action}"
    return "No action needed."


def render_report(
    checks: Sequence[CheckResult],
    environment: dict[str, str],
    *,
    generated: datetime | None = None,
) -> str:
    """Render one complete Markdown report."""

    timestamp = (generated or datetime.now().astimezone()).strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )
    lines = [
        "# 5G SA Lab Check Report",
        "",
        f"Generated: {timestamp}",
        "",
        "## Summary",
        "",
        f"Overall status: **{overall_status(checks)}**",
        "",
        "## Environment",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in environment.items())
    lines.extend(
        (
            "",
            "## Checks",
            "",
            "| Check | Status | Evidence |",
            "| --- | --- | --- |",
        )
    )
    for check in checks:
        lines.append(
            f"| {_md_cell(check.name)} | **{check.status}** | "
            f"{_md_cell(check.evidence)} |"
        )
    lines.extend(
        (
            "",
            "## Suggested Next Action",
            "",
            suggested_next_action(checks),
            "",
        )
    )
    return "\n".join(lines)


def write_report(path: Path, report: str) -> None:
    """Create parent directories and write a UTF-8 Markdown report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def run_checks(args: argparse.Namespace, runner: CommandRunner) -> list[CheckResult]:
    """Execute checks in dependency order."""

    checks = [
        check_required_commands(args.ueransim_root),
        check_core_services(runner),
        check_expected_ports(runner),
    ]

    gnb_text, gnb_error = read_log(args.gnb_log, "gNB connection")
    checks.append(gnb_error or parse_gnb_log(gnb_text or ""))

    ue_text, ue_error = read_log(args.ue_log, "UE registration")
    if ue_error:
        checks.append(ue_error)
        checks.append(
            CheckResult(
                "PDU session",
                FAIL,
                "No readable UE log was available.",
                "Capture a current baseline UE log and pass --ue-log.",
            )
        )
    else:
        checks.extend(parse_ue_log(ue_text or ""))

    namespace, namespace_error = discover_namespace(runner, args.namespace)
    if namespace_error:
        checks.append(namespace_error)
        checks.append(
            CheckResult(
                "UE connectivity",
                FAIL,
                "No unambiguous live UE namespace was available.",
                "Start the baseline UE or pass --namespace.",
            )
        )
    else:
        checks.append(check_ue_tunnel(runner, namespace or ""))
        checks.append(
            check_connectivity(
                runner,
                namespace or "",
                args.target,
                args.ping_count,
            )
        )

    return checks


def build_parser(repository_root: Path) -> argparse.ArgumentParser:
    """Build the command-line interface."""

    default_ueransim = Path(
        os.environ.get("UERANSIM_ROOT", str(Path.home() / "UERANSIM"))
    ).expanduser()
    parser = argparse.ArgumentParser(
        description=(
            "Run read-only 5G SA lab checks and generate a Markdown report."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repository_root / "reports" / "latest_lab_check.md",
        help="Markdown report path (default: reports/latest_lab_check.md)",
    )
    parser.add_argument("--gnb-log", type=Path, help="current UERANSIM gNB log")
    parser.add_argument("--ue-log", type=Path, help="current UERANSIM UE log")
    parser.add_argument(
        "--namespace",
        help="live UERANSIM PDU-session namespace; auto-detected when omitted",
    )
    parser.add_argument(
        "--target",
        default="8.8.8.8",
        help="UE connectivity target IP (default: 8.8.8.8)",
    )
    parser.add_argument(
        "--ping-count",
        type=int,
        default=3,
        help="number of UE Echo Requests (default: 3)",
    )
    parser.add_argument(
        "--command-timeout",
        type=float,
        default=5.0,
        help="default external-command timeout in seconds",
    )
    parser.add_argument(
        "--ueransim-root",
        type=Path,
        default=default_ueransim,
        help="UERANSIM source/build root",
    )
    return parser


def _matching_line(text: str, marker: str) -> str:
    for line in text.splitlines():
        if marker in line:
            return line.strip()
    return marker


def _first_marker(text: str, markers: Sequence[str]) -> str | None:
    for marker in markers:
        if marker in text:
            return marker
    return None


def _ping_summary(text: str) -> str:
    for line in text.splitlines():
        if "packets transmitted" in line:
            return line.strip()
    return ""


def _md_cell(value: str) -> str:
    return " ".join(value.replace("|", r"\|").split())


def display_path(path: Path) -> str:
    """Display home-directory paths without exposing the local account name."""

    expanded = path.expanduser()
    try:
        relative = expanded.relative_to(Path.home())
    except ValueError:
        return str(expanded)
    return str(Path("~") / relative)


def main(argv: Sequence[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parents[1]
    parser = build_parser(repository_root)
    args = parser.parse_args(argv)
    if args.ping_count < 1:
        parser.error("--ping-count must be at least 1")
    if args.command_timeout <= 0:
        parser.error("--command-timeout must be positive")

    runner = CommandRunner(timeout=args.command_timeout)
    checks = run_checks(args, runner)
    report = render_report(checks, collect_environment(args.ueransim_root))
    write_report(args.output, report)

    print(f"Overall status: {overall_status(checks)}")
    print(f"Report written to: {args.output}")
    if overall_status(checks) == FAIL:
        print(f"Suggested next action: {suggested_next_action(checks)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

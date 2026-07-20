"""Cross-platform ping connectivity testing."""

from __future__ import annotations

import platform
import re
import subprocess
from collections.abc import Sequence

from network_reliability.models import PingResult


_LATENCY_PATTERN = re.compile(
    r"[=<]\s*(?P<latency>\d+(?:\.\d+)?)\s*ms",
    re.IGNORECASE,
)


def build_ping_command(
    target: str,
    count: int,
    timeout_seconds: float,
    system_name: str | None = None,
) -> list[str]:
    """Build the correct ping command for the current operating system.

    Args:
        target: Hostname or IP address to test.
        count: Number of ping packets to send.
        timeout_seconds: Timeout for each ping response.
        system_name: Optional operating-system name used mainly for testing.

    Returns:
        A list containing the command and its arguments.

    Raises:
        ValueError: If the target, count, or timeout is invalid.
    """
    cleaned_target = target.strip()

    if not cleaned_target:
        raise ValueError("Target must not be empty.")

    if count <= 0:
        raise ValueError("Ping count must be greater than zero.")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than zero.")

    operating_system = system_name or platform.system()

    if operating_system == "Windows":
        timeout_milliseconds = max(1, round(timeout_seconds * 1000))

        return [
            "ping",
            "-n",
            str(count),
            "-w",
            str(timeout_milliseconds),
            cleaned_target,
        ]

    # Linux uses -c for packet count and -W for reply timeout.
    # This command also works for the project's initial macOS use case,
    # while the overall subprocess timeout prevents indefinite execution.
    timeout_whole_seconds = max(1, round(timeout_seconds))

    return [
        "ping",
        "-c",
        str(count),
        "-W",
        str(timeout_whole_seconds),
        cleaned_target,
    ]


def extract_latencies(output: str) -> list[float]:
    """Extract latency measurements from individual ping responses."""
    latencies: list[float] = []

    for line in output.splitlines():
        normalized_line = line.strip().lower()

        is_windows_reply = normalized_line.startswith("reply from")
        is_unix_reply = "bytes from" in normalized_line

        if not is_windows_reply and not is_unix_reply:
            continue

        match = _LATENCY_PATTERN.search(line)

        if match is None:
            continue

        latency = float(match.group("latency"))

        if "<" in match.group(0):
            latency /= 2

        latencies.append(latency)

    return latencies

def calculate_ping_result(
    target: str,
    packets_sent: int,
    latencies: Sequence[float],
    error: str | None = None,
) -> PingResult:
    """Create a structured ping result from collected latency values."""
    packets_received = len(latencies)

    packet_loss_percent = (
        ((packets_sent - packets_received) / packets_sent) * 100
    )

    if not latencies:
        return PingResult(
            target=target,
            reachable=False,
            packets_sent=packets_sent,
            packets_received=0,
            packet_loss_percent=100.0,
            minimum_latency_ms=None,
            maximum_latency_ms=None,
            average_latency_ms=None,
            error=error,
        )

    return PingResult(
        target=target,
        reachable=True,
        packets_sent=packets_sent,
        packets_received=packets_received,
        packet_loss_percent=round(packet_loss_percent, 2),
        minimum_latency_ms=min(latencies),
        maximum_latency_ms=max(latencies),
        average_latency_ms=round(sum(latencies) / packets_received, 2),
        error=error,
    )


def ping_host(
    target: str,
    count: int = 4,
    timeout_seconds: float = 2.0,
) -> PingResult:
    """Ping a host and return a structured connectivity result.

    Args:
        target: Hostname or IP address to test.
        count: Number of packets to send.
        timeout_seconds: Timeout for each response.

    Returns:
        A PingResult containing availability, packet loss, and latency data.
    """
   
    cleaned_target = target.strip()

    command = build_ping_command(
        target=cleaned_target,
        count=count,
        timeout_seconds=timeout_seconds,
    )

    overall_timeout = count * timeout_seconds + 5

    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=overall_timeout,
            check=False,
        )
    except FileNotFoundError:
        return calculate_ping_result(
            target=cleaned_target,
            packets_sent=count,
            latencies=[],
            error="The operating system ping command was not found.",
        )
    except subprocess.TimeoutExpired:
        return calculate_ping_result(
            target=cleaned_target,
            packets_sent=count,
            latencies=[],
            error="The ping command exceeded the allowed execution time.",
        )
    except OSError as exc:
        return calculate_ping_result(
            target=cleaned_target,
            packets_sent=count,
            latencies=[],
            error=f"Failed to execute ping: {exc}",
        )

    combined_output = (
        f"{completed_process.stdout}\n{completed_process.stderr}"
    )

    latencies = extract_latencies(combined_output)

    error: str | None = None

    if not latencies:
        error = "No ICMP responses were received. The host may be unavailable, " \
            "or ICMP may be blocked by a firewall."

    return calculate_ping_result(
        target=cleaned_target,
        packets_sent=count,
        latencies=latencies,
        error=error,
    )
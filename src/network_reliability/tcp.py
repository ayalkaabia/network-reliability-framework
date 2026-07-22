"""TCP port availability testing."""

from __future__ import annotations

import socket
import time

from network_reliability.models import TcpResult


def validate_tcp_arguments(
    target: str,
    port: int,
    timeout_seconds: float,
) -> str:
    """Validate TCP test arguments and return the cleaned target."""
    cleaned_target = target.strip()

    if not cleaned_target:
        raise ValueError("Target must not be empty.")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than zero.")

    return cleaned_target


def test_tcp_port(
    target: str,
    port: int,
    timeout_seconds: float = 3.0,
) -> TcpResult:
    """Attempt to connect to a TCP port.

    A successful result means that a TCP connection was established.
    A failed result does not necessarily mean that the host is offline;
    the specific port may be closed or filtered.
    """
    cleaned_target = validate_tcp_arguments(
        target=target,
        port=port,
        timeout_seconds=timeout_seconds,
    )

    start_time = time.perf_counter()

    try:
        with socket.create_connection(
            (cleaned_target, port),
            timeout=timeout_seconds,
        ) as connection:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            resolved_ip = connection.getpeername()[0]

            return TcpResult(
                target=cleaned_target,
                port=port,
                connected=True,
                connection_time_ms=round(elapsed_ms, 2),
                resolved_ip=resolved_ip,
            )

    except socket.gaierror:
        return TcpResult(
            target=cleaned_target,
            port=port,
            connected=False,
            connection_time_ms=None,
            resolved_ip=None,
            error="The hostname could not be resolved.",
        )

    except ConnectionRefusedError:
        return TcpResult(
            target=cleaned_target,
            port=port,
            connected=False,
            connection_time_ms=None,
            resolved_ip=None,
            error="The connection was refused. The port may be closed.",
        )

    except TimeoutError:
        return TcpResult(
            target=cleaned_target,
            port=port,
            connected=False,
            connection_time_ms=None,
            resolved_ip=None,
            error="The connection attempt timed out.",
        )

    except OSError as exc:
        return TcpResult(
            target=cleaned_target,
            port=port,
            connected=False,
            connection_time_ms=None,
            resolved_ip=None,
            error=f"TCP connection failed: {exc}",
        )
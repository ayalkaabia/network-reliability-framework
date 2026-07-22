"""Tests for TCP port availability functionality."""

from __future__ import annotations

import socket
import threading

import pytest

from network_reliability.tcp import (
    test_tcp_port as run_tcp_test,
    validate_tcp_arguments,
)



def start_local_tcp_server() -> tuple[socket.socket, int]:
    """Start a temporary local TCP server on an available port."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)

    port = server.getsockname()[1]

    def accept_connection() -> None:
        try:
            connection, _ = server.accept()
            connection.close()
        finally:
            server.close()

    thread = threading.Thread(
        target=accept_connection,
        daemon=True,
    )
    thread.start()

    return server, port


def test_validate_tcp_arguments() -> None:
    """Valid arguments should return the cleaned hostname."""
    target = validate_tcp_arguments(
        target="  localhost  ",
        port=443,
        timeout_seconds=2,
    )

    assert target == "localhost"

""" this test only passes if the port is outside the valid TCP range """
@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_port_is_rejected(port: int) -> None:
    """Ports outside the valid TCP range should be rejected."""
    with pytest.raises(
        ValueError,
        match="Port must be between 1 and 65535",
    ):
        validate_tcp_arguments(
            target="localhost",
            port=port,
            timeout_seconds=2,
        )


def test_empty_target_is_rejected() -> None:
    """An empty target should be rejected."""
    with pytest.raises(ValueError, match="Target must not be empty"):
        validate_tcp_arguments(
            target="   ",
            port=443,
            timeout_seconds=2,
        )


@pytest.mark.parametrize("timeout_seconds", [0, -1, -0.5])
def test_invalid_timeout_is_rejected(
    timeout_seconds: float,
) -> None:
    """Non-positive timeouts should be rejected."""
    with pytest.raises(
        ValueError,
        match="Timeout must be greater than zero",
    ):
        validate_tcp_arguments(
            target="localhost",
            port=443,
            timeout_seconds=timeout_seconds,
        )

def test_successful_local_tcp_connection() -> None:
    """The test should connect to a listening local TCP server."""
    _, port = start_local_tcp_server()

    result = run_tcp_test(
        target="127.0.0.1",
        port=port,
        timeout_seconds=2,
    )

    assert result.connected is True
    assert result.target == "127.0.0.1"
    assert result.port == port
    assert result.connection_time_ms is not None
    assert result.connection_time_ms >= 0
    assert result.resolved_ip == "127.0.0.1"
    assert result.error is None


def test_unresolvable_hostname() -> None:
    """An invalid hostname should return a DNS-related failure."""
    result = run_tcp_test(
        target="host-that-does-not-exist.invalid",
        port=443,
        timeout_seconds=1,
    )

    assert result.connected is False
    assert result.connection_time_ms is None
    assert result.resolved_ip is None
    assert result.error == "The hostname could not be resolved."
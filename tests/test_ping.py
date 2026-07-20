"""Tests for cross-platform ping functionality."""

import pytest

from network_reliability.ping import (
    build_ping_command,
    calculate_ping_result,
    extract_latencies,
)


def test_build_windows_ping_command() -> None:
    """Windows should use -n for count and -w for timeout."""
    command = build_ping_command(
        target="google.com",
        count=4,
        timeout_seconds=2,
        system_name="Windows",
    )

    assert command == [
        "ping",
        "-n",
        "4",
        "-w",
        "2000",
        "google.com",
    ]


def test_build_linux_ping_command() -> None:
    """Linux should use -c for count and -W for timeout."""
    command = build_ping_command(
        target="google.com",
        count=4,
        timeout_seconds=2,
        system_name="Linux",
    )

    assert command == [
        "ping",
        "-c",
        "4",
        "-W",
        "2",
        "google.com",
    ]


def test_empty_target_is_rejected() -> None:
    """An empty hostname should raise a validation error."""
    with pytest.raises(ValueError, match="Target must not be empty"):
        build_ping_command(
            target="   ",
            count=4,
            timeout_seconds=2,
        )


def test_invalid_packet_count_is_rejected() -> None:
    """Packet count must be positive."""
    with pytest.raises(
        ValueError,
        match="Ping count must be greater than zero",
    ):
        build_ping_command(
            target="google.com",
            count=0,
            timeout_seconds=2,
        )


def test_invalid_timeout_is_rejected() -> None:
    """Timeout must be positive."""
    with pytest.raises(
        ValueError,
        match="Timeout must be greater than zero",
    ):
        build_ping_command(
            target="google.com",
            count=4,
            timeout_seconds=0,
        )


def test_extract_integer_latencies() -> None:
    """Integer latency values should be extracted."""
    output = """
    Reply from 8.8.8.8: bytes=32 time=20ms TTL=117
    Reply from 8.8.8.8: bytes=32 time=24ms TTL=117
    """

    assert extract_latencies(output) == [20.0, 24.0]


def test_extract_decimal_and_less_than_latencies() -> None:
    """Decimal values and sub-millisecond estimates should be supported."""
    output = """
    64 bytes from 8.8.8.8: time=14.5 ms
    Reply from 8.8.8.8: time<1ms
    """

    assert extract_latencies(output) == [14.5, 0.5]


def test_calculate_successful_ping_result() -> None:
    """Latency statistics and packet loss should be calculated."""
    result = calculate_ping_result(
        target="google.com",
        packets_sent=4,
        latencies=[20.0, 22.0, 24.0],
    )

    assert result.reachable is True
    assert result.packets_sent == 4
    assert result.packets_received == 3
    assert result.packet_loss_percent == 25.0
    assert result.minimum_latency_ms == 20.0
    assert result.maximum_latency_ms == 24.0
    assert result.average_latency_ms == 22.0
    assert result.error is None


def test_calculate_failed_ping_result() -> None:
    """No responses should produce an unreachable result."""
    result = calculate_ping_result(
        target="invalid.example",
        packets_sent=4,
        latencies=[],
        error="No ping responses were received.",
    )

    assert result.reachable is False
    assert result.packets_received == 0
    assert result.packet_loss_percent == 100.0
    assert result.minimum_latency_ms is None
    assert result.maximum_latency_ms is None
    assert result.average_latency_ms is None
    assert result.error == "No ping responses were received."
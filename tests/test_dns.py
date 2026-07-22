"""Tests for DNS hostname resolution functionality."""

from __future__ import annotations

import socket
from unittest.mock import patch

import pytest

from network_reliability.dns import (
    _unique_addresses,
    resolve_host,
    validate_dns_target,
)
from network_reliability.main import create_argument_parser
from network_reliability.models import DnsAddress


def _ipv4_addrinfo(address: str) -> tuple:
    """Build a realistic IPv4 getaddrinfo() result tuple."""
    return (
        socket.AF_INET,
        socket.SOCK_STREAM,
        6,
        "",
        (address, 0),
    )


def _ipv6_addrinfo(address: str) -> tuple:
    """Build a realistic IPv6 getaddrinfo() result tuple."""
    return (
        socket.AF_INET6,
        socket.SOCK_STREAM,
        6,
        "",
        (address, 0, 0, 0),
    )


def test_validate_dns_target_trims_whitespace() -> None:
    """Valid targets should be trimmed."""
    assert validate_dns_target("  google.com  ") == "google.com"


def test_empty_target_is_rejected() -> None:
    """An empty target should be rejected."""
    with pytest.raises(ValueError, match="Target must not be empty"):
        validate_dns_target("   ")


def test_successful_ipv4_resolution() -> None:
    """IPv4-only resolution should return a structured success result."""
    mocked_results = [_ipv4_addrinfo("142.250.185.78")]

    with patch("socket.getaddrinfo", return_value=mocked_results):
        result = resolve_host("google.com")

    assert result.resolved is True
    assert result.target == "google.com"
    assert result.error is None
    assert result.addresses == (
        DnsAddress(address="142.250.185.78", version="IPv4"),
    )


def test_successful_ipv6_resolution() -> None:
    """IPv6-only resolution should return a structured success result."""
    mocked_results = [_ipv6_addrinfo("2a00:1450:4006:80e::200e")]

    with patch("socket.getaddrinfo", return_value=mocked_results):
        result = resolve_host("google.com")

    assert result.resolved is True
    assert result.addresses == (
        DnsAddress(address="2a00:1450:4006:80e::200e", version="IPv6"),
    )


def test_combined_ipv4_and_ipv6_resolution() -> None:
    """Both address families should be collected when present."""
    mocked_results = [
        _ipv4_addrinfo("142.250.185.78"),
        _ipv6_addrinfo("2a00:1450:4006:80e::200e"),
    ]

    with patch("socket.getaddrinfo", return_value=mocked_results):
        result = resolve_host("google.com")

    assert result.resolved is True
    assert result.addresses == (
        DnsAddress(address="142.250.185.78", version="IPv4"),
        DnsAddress(address="2a00:1450:4006:80e::200e", version="IPv6"),
    )


def test_duplicate_addresses_are_removed() -> None:
    """Duplicate IP addresses should be removed while preserving order."""
    mocked_results = [
        _ipv4_addrinfo("142.250.185.78"),
        _ipv4_addrinfo("142.250.185.78"),
        _ipv6_addrinfo("2a00:1450:4006:80e::200e"),
        _ipv6_addrinfo("2a00:1450:4006:80e::200e"),
    ]

    addresses = _unique_addresses(mocked_results)

    assert addresses == (
        DnsAddress(address="142.250.185.78", version="IPv4"),
        DnsAddress(address="2a00:1450:4006:80e::200e", version="IPv6"),
    )


def test_address_version_labels() -> None:
    """Resolved addresses should be labeled as IPv4 or IPv6."""
    mocked_results = [
        _ipv4_addrinfo("8.8.8.8"),
        _ipv6_addrinfo("2001:4860:4860::8888"),
    ]

    addresses = _unique_addresses(mocked_results)

    assert addresses[0].version == "IPv4"
    assert addresses[1].version == "IPv6"


def test_successful_result_fields() -> None:
    """A successful result should expose the expected fields."""
    mocked_results = [
        _ipv4_addrinfo("1.1.1.1"),
        _ipv6_addrinfo("2606:4700:4700::1111"),
    ]

    with (
        patch("socket.getaddrinfo", return_value=mocked_results),
        patch("time.perf_counter", side_effect=[1.0, 1.015]),
    ):
        result = resolve_host("  cloudflare.com  ")

    assert result.target == "cloudflare.com"
    assert result.resolved is True
    assert result.resolution_time_ms == 15.0
    assert len(result.addresses) == 2
    assert result.error is None


def test_gaierror_is_handled() -> None:
    """socket.gaierror should produce a stable unresolved result."""
    with patch(
        "socket.getaddrinfo",
        side_effect=socket.gaierror(socket.EAI_NONAME, "Name or service not known"),
    ):
        result = resolve_host("host-that-does-not-exist.invalid")

    assert result.resolved is False
    assert result.resolution_time_ms is None
    assert result.addresses == ()
    assert result.error == "The hostname could not be resolved."


def test_oserror_is_handled() -> None:
    """A general OSError should produce a stable failure message."""
    with patch("socket.getaddrinfo", side_effect=OSError("unexpected failure")):
        result = resolve_host("example.com")

    assert result.resolved is False
    assert result.resolution_time_ms is None
    assert result.addresses == ()
    assert result.error == (
        "DNS resolution failed due to an operating system error."
    )


def test_resolution_time_calculation() -> None:
    """Resolution time should be derived from perf_counter measurements."""
    mocked_results = [_ipv4_addrinfo("8.8.8.8")]

    with (
        patch("socket.getaddrinfo", return_value=mocked_results),
        patch("time.perf_counter", side_effect=[10.0, 10.0425]),
    ):
        result = resolve_host("dns.google")

    assert result.resolution_time_ms == 42.5


def test_cli_parser_accepts_dns_subcommand() -> None:
    """The CLI parser should accept the dns subcommand."""
    parser = create_argument_parser()
    arguments = parser.parse_args(["dns", "google.com"])

    assert arguments.command == "dns"
    assert arguments.target == "google.com"

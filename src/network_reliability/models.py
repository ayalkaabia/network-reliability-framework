"""Data models used by the network reliability framework."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PingResult:
    """Represent the result of an ICMP ping test.

    The reachable field indicates whether at least one ICMP response was
    received. A false value does not necessarily mean that other services,
    such as HTTP or HTTPS, are unavailable.
    """
    target: str
    reachable: bool
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    minimum_latency_ms: float | None
    maximum_latency_ms: float | None
    average_latency_ms: float | None
    error: str | None = None
    
@dataclass(frozen=True)
class TcpResult:
    """Represent the result of a TCP port connectivity test."""

    target: str
    port: int
    connected: bool
    connection_time_ms: float | None
    resolved_ip: str | None
    error: str | None = None

@dataclass(frozen=True)
class DnsAddress:
    """A single resolved IP address and its IP version label."""

    address: str
    version: str  # "IPv4" or "IPv6"


@dataclass(frozen=True)
class DnsResult:
    """Represent the result of a DNS resolution test.

    A successful result means the hostname mapped to one or more addresses.
    It does not prove that the host or any service on it is reachable.
    """

    target: str
    resolved: bool
    resolution_time_ms: float | None
    addresses: tuple[DnsAddress, ...]
    error: str | None = None
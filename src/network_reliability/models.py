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
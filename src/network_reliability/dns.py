"""DNS hostname resolution testing."""

from __future__ import annotations

import socket
import time
from collections.abc import Sequence

from network_reliability.models import DnsAddress, DnsResult

# socket.getaddrinfo() returns a list of 5-tuples:
# (family, type, proto, canonname, sockaddr)
AddrInfoResult = tuple[
    socket.AddressFamily,
    socket.SocketKind,
    int,
    str,
    tuple,
]

_UNRESOLVED_MESSAGE = "The hostname could not be resolved."
_OS_ERROR_MESSAGE = "DNS resolution failed due to an operating system error."


def validate_dns_target(target: str) -> str:
    """Validate and return the cleaned DNS target hostname."""
    cleaned_target = target.strip()

    if not cleaned_target:
        raise ValueError("Target must not be empty.")

    return cleaned_target


def _unique_addresses(
    addrinfo_results: Sequence[AddrInfoResult],
) -> tuple[DnsAddress, ...]:
    """Extract unique IPv4/IPv6 addresses, preserving resolver order."""
    seen: set[str] = set()
    addresses: list[DnsAddress] = []

    for family, _type, _proto, _canonname, sockaddr in addrinfo_results:
        ip_address = sockaddr[0]

        if ip_address in seen:
            continue

        seen.add(ip_address)

        if family == socket.AF_INET:
            version = "IPv4"
        elif family == socket.AF_INET6:
            version = "IPv6"
        else:
            continue

        addresses.append(DnsAddress(address=ip_address, version=version))

    return tuple(addresses)


def resolve_host(target: str) -> DnsResult:
    """Resolve a hostname to IPv4 and IPv6 addresses.

    A successful result means the hostname mapped to one or more addresses.
    It does not prove that the host or any service on it is reachable.
    """
    cleaned_target = validate_dns_target(target)

    start_time = time.perf_counter()

    try:
        addrinfo_results = socket.getaddrinfo(
            cleaned_target,
            None,
            family=0,
            type=socket.SOCK_STREAM,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        addresses = _unique_addresses(addrinfo_results)

        if not addresses:
            return DnsResult(
                target=cleaned_target,
                resolved=False,
                resolution_time_ms=None,
                addresses=(),
                error=_UNRESOLVED_MESSAGE,
            )

        return DnsResult(
            target=cleaned_target,
            resolved=True,
            resolution_time_ms=round(elapsed_ms, 2),
            addresses=addresses,
        )

    except socket.gaierror:
        return DnsResult(
            target=cleaned_target,
            resolved=False,
            resolution_time_ms=None,
            addresses=(),
            error=_UNRESOLVED_MESSAGE,
        )

    except OSError:
        return DnsResult(
            target=cleaned_target,
            resolved=False,
            resolution_time_ms=None,
            addresses=(),
            error=_OS_ERROR_MESSAGE,
        )

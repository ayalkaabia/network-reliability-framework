"""Command-line entry point for the network reliability framework."""

import argparse

from network_reliability.dns import resolve_host
from network_reliability.models import DnsResult, PingResult, TcpResult
from network_reliability.ping import ping_host
from network_reliability.tcp import test_tcp_port


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Test network connectivity and service availability."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    ping_parser = subparsers.add_parser(
        "ping",
        help="Run an ICMP ping connectivity test.",
    )

    ping_parser.add_argument(
        "target",
        help="Hostname or IP address to ping.",
    )

    ping_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=4,
        help="Number of ping packets to send (default: 4).",
    )

    ping_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=2.0,
        help="Timeout in seconds for each response (default: 2).",
    )

    tcp_parser = subparsers.add_parser(
        "tcp",
        help="Test whether a TCP port accepts connections.",
    )

    tcp_parser.add_argument(
        "target",
        help="Hostname or IP address to test.",
    )

    tcp_parser.add_argument(
        "port",
        type=int,
        help="TCP port number to test.",
    )

    tcp_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3.0,
        help="Connection timeout in seconds (default: 3).",
    )

    dns_parser = subparsers.add_parser(
        "dns",
        help="Resolve a hostname to IPv4 and IPv6 addresses.",
    )

    dns_parser.add_argument(
        "target",
        help="Hostname to resolve.",
    )

    return parser


def display_ping_result(result: PingResult) -> None:
    """Display a ping result in a readable terminal format."""
    reachability = "Yes" if result.reachable else "No"

    print("\nPing Connectivity Test")
    print("-" * 30)
    print(f"Target:           {result.target}")
    print(f"Reachable:        {reachability}")
    print(f"Packets sent:     {result.packets_sent}")
    print(f"Packets received: {result.packets_received}")
    print(f"Packet loss:      {result.packet_loss_percent:.2f}%")

    if result.average_latency_ms is not None:
        print(f"Minimum latency:  {result.minimum_latency_ms:.2f} ms")
        print(f"Maximum latency:  {result.maximum_latency_ms:.2f} ms")
        print(f"Average latency:  {result.average_latency_ms:.2f} ms")

    if result.error:
        print(f"Message:          {result.error}")


def display_tcp_result(result: TcpResult) -> None:
    """Display a TCP test result in a readable terminal format."""
    connection_status = "Yes" if result.connected else "No"

    print("\nTCP Port Availability Test")
    print("-" * 30)
    print(f"Target:              {result.target}")
    print(f"Port:                {result.port}")
    print(f"Connected:           {connection_status}")

    if result.resolved_ip is not None:
        print(f"Resolved IP:         {result.resolved_ip}")

    if result.connection_time_ms is not None:
        print(f"Connection time:     {result.connection_time_ms:.2f} ms")

    if result.error:
        print(f"Message:             {result.error}")


def display_dns_result(result: DnsResult) -> None:
    """Display a DNS resolution result in a readable terminal format."""
    resolution_status = "Yes" if result.resolved else "No"

    print("\nDNS Resolution Test")
    print("-" * 30)
    print(f"Target:           {result.target}")
    print(f"Resolved:         {resolution_status}")

    if result.resolution_time_ms is not None:
        print(f"Resolution time:  {result.resolution_time_ms:.2f} ms")

    if result.addresses:
        print("Addresses:")
        for address in result.addresses:
            print(f"  - {address.address} ({address.version})")

    if result.error:
        print(f"Message:          {result.error}")


def main() -> None:
    """Run the requested network test."""
    parser = create_argument_parser()
    arguments = parser.parse_args()

    try:
        if arguments.command == "ping":
            result = ping_host(
                target=arguments.target,
                count=arguments.count,
                timeout_seconds=arguments.timeout,
            )
            display_ping_result(result)

        elif arguments.command == "tcp":
            result = test_tcp_port(
                target=arguments.target,
                port=arguments.port,
                timeout_seconds=arguments.timeout,
            )
            display_tcp_result(result)

        elif arguments.command == "dns":
            result = resolve_host(target=arguments.target)
            display_dns_result(result)

    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
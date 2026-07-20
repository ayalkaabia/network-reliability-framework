"""Command-line entry point for the network reliability framework."""

import argparse

from network_reliability.models import PingResult
from network_reliability.ping import ping_host


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Test the connectivity and reliability of a network host."
    )

    parser.add_argument(
        "target",
        help="Hostname or IP address to test, such as google.com or 8.8.8.8",
    )

    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=4,
        help="Number of ping packets to send (default: 4)",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=2.0,
        help="Timeout in seconds for each response (default: 2)",
    )

    return parser


def display_ping_result(result: PingResult) -> None:
    """Display a ping result in a readable terminal format."""
    reachability = "Yes" if result.reachable else "No"

    print("\nPing Connectivity Test")
    print("-" * 30)
    print(f"Target:          {result.target}")
    print(f"Reachable:       {reachability}")
    print(f"Packets sent:    {result.packets_sent}")
    print(f"Packets received: {result.packets_received}")
    print(f"Packet loss:     {result.packet_loss_percent:.2f}%")

    if result.average_latency_ms is not None:
        print(f"Minimum latency: {result.minimum_latency_ms:.2f} ms")
        print(f"Maximum latency: {result.maximum_latency_ms:.2f} ms")
        print(f"Average latency: {result.average_latency_ms:.2f} ms")

    if result.error:
        print(f"Message:         {result.error}")


def main() -> None:
    """Run the command-line application."""
    parser = create_argument_parser()
    arguments = parser.parse_args()

    try:
        result = ping_host(
            target=arguments.target,
            count=arguments.count,
            timeout_seconds=arguments.timeout,
        )
    except ValueError as exc:
        parser.error(str(exc))

    display_ping_result(result)


if __name__ == "__main__":
    main()
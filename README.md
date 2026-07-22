# Network Reliability Testing Framework

A Python-based command-line framework for testing network connectivity and service availability.

## Features

* [x] Cross-platform ICMP ping connectivity testing
* [x] TCP port availability testing
* [x] Dedicated DNS resolution testing
* [x] Packet-loss calculation
* [x] Minimum, maximum, and average ping latency
* [x] TCP connection-time measurement
* [x] Hostname resolution error handling
* [x] Automated tests with pytest
* [ ] Repeated reliability monitoring
* [ ] JSON and CSV report generation
* [ ] Logging and configuration files
* [ ] GitHub Actions integration

## Technologies

* Python
* pytest
* Git
* GitHub

## Project Structure

```text
network-reliability-framework/
├── src/
│   └── network_reliability/
│       ├── __init__.py
│       ├── dns.py
│       ├── main.py
│       ├── models.py
│       ├── ping.py
│       └── tcp.py
├── tests/
│   ├── __init__.py
│   ├── test_dns.py
│   ├── test_ping.py
│   └── test_tcp.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/ayalkaabia/network-reliability-framework.git
cd network-reliability-framework
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Install the project in editable mode:

```bash
pip install -e .
```

## Usage

### Ping Connectivity Test

Run an ICMP ping test:

```bash
python -m network_reliability.main ping google.com
```

Specify the number of packets:

```bash
python -m network_reliability.main ping google.com --count 5
```

Specify the timeout in seconds:

```bash
python -m network_reliability.main ping google.com --count 5 --timeout 2
```

Example output:

```text
Ping Connectivity Test
------------------------------
Target:           google.com
Reachable:        Yes
Packets sent:     4
Packets received: 4
Packet loss:      0.00%
Minimum latency:  24.00 ms
Maximum latency:  52.00 ms
Average latency:  38.50 ms
```

### TCP Port Availability Test

Test whether a TCP service accepts connections:

```bash
python -m network_reliability.main tcp google.com 443
```

Specify a custom timeout:

```bash
python -m network_reliability.main tcp google.com 443 --timeout 5
```

Example successful result:

```text
TCP Port Availability Test
------------------------------
Target:              google.com
Port:                443
Connected:           Yes
Resolved IP:         2a00:1450:4028:80b::200e
Connection time:     131.54 ms
```

Example hostname-resolution failure:

```text
TCP Port Availability Test
------------------------------
Target:              host-that-does-not-exist.invalid
Port:                443
Connected:           No
Message:             The hostname could not be resolved.
```

### DNS Resolution Test

Resolve a hostname to IPv4 and IPv6 addresses:

```bash
python -m network_reliability.main dns google.com
```

DNS resolution confirms that a hostname can be mapped to one or more IP addresses. It does not prove that the host or any service on it is reachable.

Example successful result:

```text
DNS Resolution Test
------------------------------
Target:           google.com
Resolved:         Yes
Resolution time:  15.42 ms
Addresses:
  - 142.250.185.78 (IPv4)
  - 2a00:1450:4006:80e::200e (IPv6)
```

Example resolution failure:

```text
DNS Resolution Test
------------------------------
Target:           host-that-does-not-exist.invalid
Resolved:         No
Message:          The hostname could not be resolved.
```

## Testing

Run all automated tests:

```bash
python -m pytest
```

Run the tests with detailed output:

```bash
python -m pytest -v
```

Current test coverage includes:

* Windows and Linux ping command construction
* Ping latency parsing
* Packet-loss calculations
* Invalid ping arguments
* TCP argument validation
* Successful local TCP connections
* Invalid hostname handling
* Invalid port and timeout handling
* DNS target validation
* IPv4 and IPv6 DNS resolution
* Duplicate DNS address removal
* DNS resolution timing
* DNS error handling without live network access
* DNS CLI subcommand parsing

## Limitations

Ping testing depends on ICMP echo responses. Some reachable hosts or networks may block ICMP traffic, so a failed ping does not necessarily mean that the target or its services are unavailable.

TCP testing checks only the specified port. A failed TCP connection may mean that the port is closed, filtered by a firewall, timed out, or unavailable even when the host itself is online.

DNS resolution confirms hostname-to-address mapping only. A successful DNS result does not mean that the host is online or that any application service is reachable. Address order follows the operating system resolver and may differ across machines.

Connection times vary depending on network conditions, DNS resolution, IPv4 or IPv6 selection, and the remote service.

## Project Status

The project is under active development. The current version supports cross-platform ping testing, TCP port availability testing, and dedicated DNS resolution testing.

## Author

Ayal Kaabia

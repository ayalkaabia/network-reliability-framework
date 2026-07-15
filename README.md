# Network Reliability Testing Framework

A Python-based framework for testing and monitoring network reliability.

The framework will measure:

* Host availability
* Network latency
* Packet loss
* TCP port availability
* DNS resolution
* Repeated connection reliability
* Test history and reporting

## Project Status

Currently under active development.

## Planned Features

* Command-line interface
* Cross-platform host testing
* Structured test results
* JSON and CSV reports
* Automated tests with pytest
* Configurable test scenarios
* Logging and error handling

## Technologies

* Python
* pytest
* Git
* GitHub

## Installation

Clone the repository:

```bash
git clone https://github.com/ayalKaabia/network-reliability-framework.git
cd network-reliability-framework
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python src/network_reliability/main.py
```

More usage instructions will be added as the framework is developed.

## Testing

Run the automated tests:

```bash
pytest
```

## Author

Ayal Kaabia

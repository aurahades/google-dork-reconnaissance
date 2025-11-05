# Google Dork Reconnaissance Tool

An automated security reconnaissance tool that performs surface-level vulnerability assessment using Google dork queries through the SearchAPI.io service.

## Register Searchapi.io
- **sign up searchapi**: get api-key from searchapi.io

## Features

- **Automated Dork Scanning**: Pre-configured with 18 common Google dork patterns for security research
- **Multiple API Key Support**: Rotate between multiple API keys automatically when rate limits are hit
- **Comprehensive Coverage**: Tests for exposed files, error messages, login pages, backup files, and more
- **Professional Reporting**: Clean, organized output with detailed statistics and results
- **Error Handling**: Robust error handling with automatic failover between API keys

## Installation

1. Save the script as `dork_scanner.py`
2. Install dependencies:
```bash
pip install -r requirements.txt

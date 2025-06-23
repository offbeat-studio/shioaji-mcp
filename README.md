# Shioaji MCP Server

A Model Context Protocol (MCP) server that provides access to Shioaji trading API functionality through standardized tools.

## Features

### Authentication & Connection
- `get_account_info` - Get account information and connection status

### Market Data
- `search_contracts` - Search for trading contracts by keyword, exchange, or category
- `get_snapshots` - Get real-time market snapshots for specified contracts
- `get_kbars` - Get historical K-bar data for contracts

### Trading Operations
- `place_order` - Place buy/sell orders with specified parameters
- `cancel_order` - Cancel existing orders by order ID
- `list_orders` - List all orders with their status
- `get_positions` - Get current positions and P&L
- `get_account_balance` - Get account balance and margin information

### Service Terms & Compliance
- `check_terms_status` - Check service terms signing status and API testing completion
- `run_api_test` - Run API test for service terms compliance (login and order tests)

## Prerequisites

1. **SinoPac Securities Account**: You need a [SinoPac Securities account](https://www.sinotrade.com.tw/openact)
2. **API Credentials**: Apply for and obtain API Key and Secret Key
3. **Service Terms**: Complete document signing and API testing (see [docs/SERVICE_TERMS.md](docs/SERVICE_TERMS.md))

## Installation & Usage

### Docker (Recommended)

Due to Shioaji dependency issues on macOS, Docker is recommended:

```bash
# Build Docker image
docker build -t shioaji-mcp .

# Run MCP server
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  shioaji-mcp
```

### MCP Client Configuration

Add the following configuration to your MCP client:

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_api_key",
        "-e", "SHIOAJI_SECRET_KEY=your_secret_key",
        "shioaji-mcp"
      ]
    }
  }
}
```

### Local Development (Linux/WSL)

```bash
# Clone repository
git clone <repository-url>
cd shioaji-mcp

# Install dependencies
uv sync

# Set environment variables
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# Run MCP server
uv run python -m shioaji_mcp.server
```

## Development Guide

### Environment Setup

```bash
# Install development dependencies
uv sync --extra test --extra lint

# Set environment variables
cp .env.example .env
# Edit .env and fill in your API credentials
```

### Testing

```bash
# Run tests
uv run pytest

# Test coverage
uv run pytest --cov=src/shioaji_mcp
```

### Code Quality

```bash
# Check code style
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

### Docker Development

```bash
# Build development Docker image
docker build -t shioaji-mcp-dev .

# Test Docker container
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=test_key \
  -e SHIOAJI_SECRET_KEY=test_secret \
  shioaji-mcp-dev
```

## Architecture

```
src/shioaji_mcp/
├── server.py          # MCP server main program
├── tools/             # Tool modules
│   ├── contracts.py   # Contract search
│   ├── market_data.py # Market data
│   ├── orders.py      # Order operations
│   ├── positions.py   # Position queries
│   └── terms.py       # Service terms
└── utils/             # Utilities
    ├── auth.py        # Authentication management
    ├── formatters.py  # Data formatting
    └── shioaji_wrapper.py # Shioaji wrapper
```

## Important Notes

⚠️ **Real Trading API**
- This MCP server connects to the real SinoPac Securities API
- All trading operations will execute real orders
- Make sure you understand the risks before trading
- Recommend testing with small amounts first
- This software is provided "as is" without warranty of any kind
- Users are responsible for their own trading decisions and compliance with regulations

⚠️ **Compatibility**
- Python 3.10-3.12
- Recommended to run in Linux environment or Docker
- macOS users should use Docker

## Troubleshooting

### macOS Dependency Issues
```bash
# Use Docker to resolve
docker run --platform=linux/amd64 ...
```

### API Connection Issues
```bash
# Check environment variables
echo $SHIOAJI_API_KEY
echo $SHIOAJI_SECRET_KEY

# Check if API credentials are valid
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_key \
  -e SHIOAJI_SECRET_KEY=your_secret \
  shioaji-mcp python -c "from shioaji_mcp.utils.auth import auth_manager; print(auth_manager.is_connected())"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes with tests
4. Run code checks and tests
5. Submit a Pull Request
# Shioaji MCP Server

A Model Context Protocol (MCP) server that provides access to Shioaji trading API functionality through standardized tools.

## Features

### Authentication & Connection
- `shioaji_login` - Login to Shioaji API with credentials
- `shioaji_logout` - Logout from Shioaji API
- `get_account_info` - Get account information

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

## Installation

### From PyPI (Recommended)

```bash
# Install directly with uvx (no local setup needed)
uvx shioaji-mcp
```

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd shioaji-mcp

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

## Configuration

Create a `.env` file with your Shioaji credentials:

```env
SHIOAJI_API_KEY=your_api_key_here
SHIOAJI_SECRET_KEY=your_secret_key_here
SHIOAJI_PERSON_ID=your_person_id_here
SHIOAJI_PASSWORD=your_password_here
```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "shioaji-mcp": {
      "command": "uvx",
      "args": ["shioaji-mcp"],
      "env": {
        "SHIOAJI_API_KEY": "your_api_key_here",
        "SHIOAJI_SECRET_KEY": "your_secret_key_here",
        "SHIOAJI_PERSON_ID": "your_person_id_here", 
        "SHIOAJI_PASSWORD": "your_password_here"
      }
    }
  }
}
```

### Direct Usage

```python
from shioaji_mcp.server import handle_call_tool

# Login
result = await handle_call_tool("shioaji_login", {
    "api_key": "your_key",
    "secret_key": "your_secret", 
    "person_id": "your_id",
    "password": "your_password"
})

# Search contracts
contracts = await handle_call_tool("search_contracts", {
    "keyword": "台積電"
})

# Place order
order = await handle_call_tool("place_order", {
    "contract": "2330",
    "action": "Buy", 
    "quantity": 1000,
    "price": 500.0
})
```

## Development

### Running Tests

```bash
# Run all tests
uv run --extra test pytest

# Run with coverage
uv run --extra test pytest --cov=src/shioaji_mcp
```

### Linting

```bash
# Run linter
uv run --extra lint ruff check src/ tests/

# Format code
uv run --extra lint black src/ tests/

# Sort imports
uv run --extra lint isort src/ tests/
```

### Example Usage

```bash
# Run the basic usage example
uv run python examples/basic_usage.py
```

## Architecture

- **Server**: Main MCP server implementation with tool registration
- **Tools**: Modular tool implementations for different functionality areas
- **Utils**: Authentication management and data formatting utilities
- **Mock Support**: Fallback mock implementation for development

## Compatibility

- Python 3.10-3.12
- Shioaji API (with mock fallback for development)
- MCP Protocol 1.0+

## License

[Add your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request
"""Simplified MCP server with only 4 high-level tools for better AI comprehension."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, Tool

from .tools_simplified import (
    account_status,
    compliance_check,
    market_query,
    order_management,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("shioaji-mcp-simple")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available simplified tools."""
    return [
        Tool(
            name="account_status",
            description=(
                "Get comprehensive account overview including account info, "
                "positions, and balance. Use this to check your account status, "
                "holdings, and available funds."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account_type": {
                        "type": "string",
                        "enum": ["all", "stock", "futures"],
                        "default": "all",
                        "description": "Type of account to query",
                    },
                    "include_positions": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include current positions",
                    },
                    "include_balance": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include account balance",
                    },
                },
            },
        ),
        Tool(
            name="market_query",
            description=(
                "Query market data - search for stocks, get real-time quotes, "
                "or retrieve historical price data. This intelligent tool "
                "determines what you need based on the parameters provided."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search keyword to find contracts (e.g., '台積電' or '2330')",
                    },
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock codes for real-time quotes (e.g., ['2330', '2317'])",
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Single stock code for historical data (e.g., '2330')",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for historical data (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for historical data (YYYY-MM-DD)",
                    },
                    "days": {
                        "type": "integer",
                        "default": 30,
                        "description": "Number of days of historical data (if dates not specified)",
                    },
                    "exchange": {
                        "type": "string",
                        "description": "Exchange filter for search (TSE, OTC, etc.)",
                    },
                },
            },
        ),
        Tool(
            name="order_management",
            description=(
                "Manage trading orders - place new orders, cancel existing ones, "
                "or list all orders. Trading operations require SHIOAJI_TRADING_ENABLED=true."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["place", "cancel", "list"],
                        "description": "Action to perform: place (new order), cancel (existing order), or list (all orders)",
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Stock code for placing order (e.g., '2330')",
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "Buy or sell",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Order quantity",
                    },
                    "price": {
                        "type": "number",
                        "description": "Order price (optional, omit for market order)",
                    },
                    "order_type": {
                        "type": "string",
                        "enum": ["ROD", "IOC", "FOK"],
                        "default": "ROD",
                        "description": "Order type: ROD (Rest of Day), IOC (Immediate or Cancel), FOK (Fill or Kill)",
                    },
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to cancel (for cancel action)",
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="compliance_check",
            description=(
                "Check service terms signing status and run API compliance tests. "
                "Use this to ensure your account is properly set up and verified."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "test"],
                        "default": "status",
                        "description": "status: Check signing status, test: Run API test",
                    }
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
    """Handle tool calls."""
    if name == "account_status":
        return await account_status(arguments or {})
    elif name == "market_query":
        return await market_query(arguments or {})
    elif name == "order_management":
        return await order_management(arguments or {})
    elif name == "compliance_check":
        return await compliance_check(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Main entry point for the simplified MCP server."""
    logger.info("Starting Shioaji MCP Server (Simplified Mode - 4 tools)")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="shioaji-mcp-simple",
                server_version="0.2.0",
                capabilities=ServerCapabilities(tools={}),
            ),
        )


def cli_main() -> None:
    """CLI entry point for simplified server."""
    import sys

    # Store original stdout for MCP communication
    original_stdout = sys.stdout

    # Create a custom stdout that filters out Shioaji messages
    class FilteredStdout:
        def __init__(self, original):
            self.original = original

        def write(self, text):
            # Only allow JSON-RPC messages to pass through
            if text.strip().startswith('{"jsonrpc"'):
                self.original.write(text)
            elif text.strip() == "":
                self.original.write(text)
            # Suppress Shioaji connection messages
            return len(text)

        def flush(self):
            self.original.flush()

        def __getattr__(self, name):
            return getattr(self.original, name)

    try:
        # Replace stdout with filtered version
        sys.stdout = FilteredStdout(original_stdout)

        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Restore original stdout
        sys.stdout = original_stdout


if __name__ == "__main__":
    cli_main()

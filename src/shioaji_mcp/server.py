"""Main MCP server implementation for Shioaji."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
)

from .tools.contracts import search_contracts
from .tools.market_data import get_kbars, get_snapshots
from .tools.orders import cancel_order, list_orders, place_order
from .tools.positions import get_account_balance, get_positions
from .utils.auth import auth_manager
from .utils.formatters import format_error_response, format_success_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("shioaji-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="shioaji_login",
            description="Login to Shioaji API",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "description": "API key"},
                    "secret_key": {"type": "string", "description": "Secret key"},
                    "person_id": {"type": "string", "description": "Person ID"},
                    "password": {"type": "string", "description": "Password"},
                },
                "required": ["api_key", "secret_key", "person_id", "password"],
            },
        ),
        Tool(
            name="get_account_info",
            description="Get account information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="shioaji_logout",
            description="Logout from Shioaji API",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="search_contracts",
            description="Search for trading contracts",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword for contract name or code",
                    },
                    "exchange": {
                        "type": "string",
                        "description": "Exchange filter (TSE, OTC, etc.)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category filter (Stock, Future, Option, etc.)",
                    },
                },
            },
        ),
        Tool(
            name="get_snapshots",
            description="Get real-time market snapshots",
            inputSchema={
                "type": "object",
                "properties": {
                    "contracts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of contract codes",
                    },
                },
                "required": ["contracts"],
            },
        ),
        Tool(
            name="get_kbars",
            description="Get historical K-bar data",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract": {"type": "string", "description": "Contract code"},
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe (1D, 1H, 5M, etc.)",
                    },
                },
                "required": ["contract"],
            },
        ),
        Tool(
            name="place_order",
            description="Place a trading order",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract": {"type": "string", "description": "Contract code"},
                    "action": {"type": "string", "description": "Buy or Sell"},
                    "quantity": {"type": "integer", "description": "Order quantity"},
                    "price": {"type": "number", "description": "Order price (optional for market orders)"},
                    "order_type": {"type": "string", "description": "Order type (ROD, IOC, FOK)"},
                },
                "required": ["contract", "action", "quantity"],
            },
        ),
        Tool(
            name="cancel_order",
            description="Cancel an existing order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID to cancel"},
                },
                "required": ["order_id"],
            },
        ),
        Tool(
            name="list_orders",
            description="List all orders",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_positions",
            description="Get current positions",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_account_balance",
            description="Get account balance information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
    """Handle tool calls."""
    if name == "shioaji_login":
        return await handle_login(arguments or {})
    elif name == "get_account_info":
        return await handle_get_account_info()
    elif name == "shioaji_logout":
        return await handle_logout()
    elif name == "search_contracts":
        return await search_contracts(arguments or {})
    elif name == "get_snapshots":
        return await get_snapshots(arguments or {})
    elif name == "get_kbars":
        return await get_kbars(arguments or {})
    elif name == "place_order":
        return await place_order(arguments or {})
    elif name == "cancel_order":
        return await cancel_order(arguments or {})
    elif name == "list_orders":
        return await list_orders(arguments or {})
    elif name == "get_positions":
        return await get_positions(arguments or {})
    elif name == "get_account_balance":
        return await get_account_balance(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_login(arguments: dict[str, Any]) -> list[Any]:
    """Handle Shioaji login."""
    try:
        result = await auth_manager.login(
            api_key=arguments.get("api_key"),
            secret_key=arguments.get("secret_key"),
            person_id=arguments.get("person_id"),
            password=arguments.get("password"),
        )

        if result["success"]:
            return format_success_response(result, "Successfully logged in to Shioaji")
        else:
            return format_error_response(Exception(result["message"]))

    except Exception as e:
        logger.error(f"Login error: {e}")
        return format_error_response(e)


async def handle_logout() -> list[Any]:
    """Handle Shioaji logout."""
    try:
        result = await auth_manager.logout()

        if result["success"]:
            return format_success_response(None, result["message"])
        else:
            return format_error_response(Exception(result["message"]))

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return format_error_response(e)


async def handle_get_account_info() -> list[Any]:
    """Handle get account info."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        api = auth_manager.get_api()
        accounts = api.list_accounts()

        account_info = []
        for account in accounts:
            account_info.append(
                {
                    "account_id": account.account_id,
                    "broker_id": account.broker_id,
                    "account_type": account.account_type,
                    "signed": account.signed,
                }
            )

        return format_success_response(
            account_info, "Account information retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Get account info error: {e}")
        return format_error_response(e)


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Shioaji MCP Server")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="shioaji-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()

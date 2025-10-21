"""HTTP API server for Shioaji MCP."""

import asyncio
import logging
import os
from typing import Any

from aiohttp import web
from aiohttp.web import Request, Response, middleware

from .tools.contracts import search_contracts
from .tools.market_data import get_kbars, get_snapshots
from .tools.orders import cancel_order, list_orders, place_order
from .tools.positions import get_account_balance, get_positions
from .tools.terms import check_terms_status, run_api_test
from .utils.auth import auth_manager
from .utils.formatters import format_error_response, format_success_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPAPIServer:
    """HTTP API Server for Shioaji MCP."""

    def __init__(self) -> None:
        """Initialize HTTP API server."""
        self.app = web.Application(middlewares=[self.auth_middleware])
        self.api_key = os.getenv("HTTP_API_KEY")
        self.host = os.getenv("HTTP_LISTEN_HOST", "127.0.0.1")
        self.port = int(os.getenv("HTTP_LISTEN_PORT", "8080"))

        if not self.api_key:
            raise ValueError(
                "HTTP_API_KEY environment variable is required for HTTP mode"
            )

        # Setup routes
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/api/tools/list", self.list_tools)
        self.app.router.add_post("/api/tools/call", self.call_tool)

    @middleware
    async def auth_middleware(self, request: Request, handler: Any) -> Response:
        """Authentication middleware."""
        # Skip auth for health check
        if request.path == "/health":
            return await handler(request)

        # Check Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return web.json_response(
                {"success": False, "error": "Missing or invalid Authorization header"},
                status=401,
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        if token != self.api_key:
            logger.warning(f"Invalid API key attempt from {request.remote}")
            return web.json_response(
                {"success": False, "error": "Invalid API key"}, status=401
            )

        return await handler(request)

    async def health_check(self, request: Request) -> Response:
        """Health check endpoint."""
        health_status = {
            "status": "healthy",
            "connected": auth_manager.is_connected(),
            "version": "0.1.0",
        }
        return web.json_response(health_status)

    async def list_tools(self, request: Request) -> Response:
        """List available tools."""
        tools = [
            {
                "name": "get_account_info",
                "description": "Get account information",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "search_contracts",
                "description": "Search for trading contracts",
                "inputSchema": {
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
            },
            {
                "name": "get_snapshots",
                "description": "Get real-time market snapshots",
                "inputSchema": {
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
            },
            {
                "name": "get_kbars",
                "description": "Get historical K-bar data",
                "inputSchema": {
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
            },
            {
                "name": "place_order",
                "description": "Place a trading order (requires SHIOAJI_TRADING_ENABLED=true)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract": {"type": "string", "description": "Contract code"},
                        "action": {"type": "string", "description": "Buy or Sell"},
                        "quantity": {
                            "type": "integer",
                            "description": "Order quantity",
                        },
                        "price": {
                            "type": "number",
                            "description": "Order price (optional for market orders)",
                        },
                        "order_type": {
                            "type": "string",
                            "description": "Order type (ROD, IOC, FOK)",
                        },
                    },
                    "required": ["contract", "action", "quantity"],
                },
            },
            {
                "name": "cancel_order",
                "description": "Cancel an existing order (requires SHIOAJI_TRADING_ENABLED=true)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "Order ID to cancel",
                        },
                    },
                    "required": ["order_id"],
                },
            },
            {
                "name": "list_orders",
                "description": "List all orders",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_positions",
                "description": "Get current positions from stock and/or futures accounts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account_type": {
                            "type": "string",
                            "description": "Account type to query (all, stock, futures)",
                            "enum": ["all", "stock", "futures"],
                            "default": "all",
                        }
                    },
                },
            },
            {
                "name": "get_account_balance",
                "description": "Get account balance information for stock and/or futures accounts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account_type": {
                            "type": "string",
                            "description": "Account type to query (all, stock, futures)",
                            "enum": ["all", "stock", "futures"],
                            "default": "all",
                        }
                    },
                },
            },
            {
                "name": "check_terms_status",
                "description": "Check service terms signing status and API testing completion",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "run_api_test",
                "description": "Run API test for service terms compliance (login and order tests)",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]
        return web.json_response({"success": True, "tools": tools})

    async def call_tool(self, request: Request) -> Response:
        """Execute a tool."""
        try:
            data = await request.json()
            tool_name = data.get("tool")
            arguments = data.get("arguments", {})

            if not tool_name:
                return web.json_response(
                    {"success": False, "error": "Missing 'tool' parameter"}, status=400
                )

            logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")

            # Execute the tool
            result = await self._execute_tool(tool_name, arguments)

            # The result from MCP tools is already a list of formatted responses
            # We wrap it in our HTTP response format
            if isinstance(result, list) and len(result) > 0:
                # Extract the first item (MCP tools return a list)
                mcp_response = result[0]

                # Check if it's a TextContent object
                if hasattr(mcp_response, "text"):
                    import json

                    response_data = json.loads(mcp_response.text)
                    return web.json_response(response_data)
                else:
                    # Fallback for direct dict response
                    return web.json_response(mcp_response)
            else:
                return web.json_response(
                    {"success": False, "error": "Unexpected response format"}
                )

        except ValueError as e:
            logger.error(f"Tool execution error: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return web.json_response(
                {"success": False, "error": f"Internal server error: {str(e)}"},
                status=500,
            )

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> list[Any]:
        """Execute a tool by name."""
        if name == "get_account_info":
            return await self._handle_get_account_info()
        elif name == "search_contracts":
            return await search_contracts(arguments)
        elif name == "get_snapshots":
            return await get_snapshots(arguments)
        elif name == "get_kbars":
            return await get_kbars(arguments)
        elif name == "place_order":
            return await place_order(arguments)
        elif name == "cancel_order":
            return await cancel_order(arguments)
        elif name == "list_orders":
            return await list_orders(arguments)
        elif name == "get_positions":
            return await get_positions(arguments)
        elif name == "get_account_balance":
            return await get_account_balance(arguments)
        elif name == "check_terms_status":
            return await check_terms_status(arguments)
        elif name == "run_api_test":
            return await run_api_test(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _handle_get_account_info(self) -> list[Any]:
        """Handle get account info."""
        try:
            if not auth_manager.is_connected():
                return format_error_response(
                    Exception(
                        "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                    )
                )

            api = auth_manager.get_api()
            accounts = api.list_accounts()

            account_info = []
            for account in accounts:
                # Determine account type
                acc_type = "unknown"
                if hasattr(account, "account_type"):
                    acc_type_str = str(account.account_type).upper()

                    # Handle both enum string format and short code format
                    if "STOCK" in acc_type_str or acc_type_str == "S":
                        acc_type = "stock"
                    elif "FUTURE" in acc_type_str or acc_type_str == "F":
                        acc_type = "futures"
                    elif acc_type_str == "H" or "HONG" in acc_type_str:
                        acc_type = "hk_stock"

                account_data = {
                    "account_id": account.account_id,
                    "broker_id": account.broker_id,
                    "account_type": account.account_type,
                    "account_type_parsed": acc_type,
                    "signed": account.signed,
                    "is_stock_account": acc_type == "stock",
                    "is_futures_account": acc_type == "futures",
                }

                # Add API shortcuts information
                if acc_type == "stock" and hasattr(api, "stock_account"):
                    account_data["api_shortcut_available"] = True
                elif acc_type == "futures" and hasattr(api, "futopt_account"):
                    account_data["api_shortcut_available"] = True
                else:
                    account_data["api_shortcut_available"] = False

                account_info.append(account_data)

            return format_success_response(
                account_info, f"Retrieved {len(account_info)} account(s) information"
            )

        except Exception as e:
            logger.error(f"Get account info error: {e}")
            return format_error_response(e)

    async def run(self) -> None:
        """Run the HTTP server."""
        logger.info(f"Starting HTTP API server on {self.host}:{self.port}")
        logger.info("Authentication: API Key required (Bearer token)")
        logger.info("Endpoints:")
        logger.info("  - GET  /health")
        logger.info("  - GET  /api/tools/list")
        logger.info("  - POST /api/tools/call")

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"HTTP API server is running at http://{self.host}:{self.port}")

        # Keep the server running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down HTTP API server...")
        finally:
            await runner.cleanup()


def http_main() -> None:
    """Entry point for HTTP mode."""
    try:
        server = HTTPAPIServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    http_main()

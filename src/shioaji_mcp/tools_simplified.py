"""Simplified MCP tools - Combining multiple operations into intuitive high-level tools."""

import logging
from typing import Any

from .tools.contracts import search_contracts as _search_contracts
from .tools.market_data import get_kbars as _get_kbars
from .tools.market_data import get_snapshots as _get_snapshots
from .tools.orders import cancel_order as _cancel_order
from .tools.orders import list_orders as _list_orders
from .tools.orders import place_order as _place_order
from .tools.positions import get_account_balance as _get_account_balance
from .tools.positions import get_positions as _get_positions
from .tools.terms import check_terms_status as _check_terms_status
from .tools.terms import run_api_test as _run_api_test
from .utils.auth import auth_manager
from .utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def account_status(arguments: dict[str, Any]) -> list[Any]:
    """
    Get comprehensive account status including account info, positions, and balance.

    This unified tool provides a complete overview of your trading account,
    combining multiple data points into a single convenient query.

    Args:
        arguments: {
            "account_type": "all" | "stock" | "futures" (optional, default: "all")
            "include_positions": bool (optional, default: true)
            "include_balance": bool (optional, default: true)
        }

    Returns:
        Combined account information including:
        - Basic account details (ID, broker, type, signed status)
        - Current positions (if requested)
        - Account balance (if requested)

    Example:
        # Get full account status
        {"account_type": "all"}

        # Get only stock account balance
        {"account_type": "stock", "include_positions": false}
    """
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        account_type = arguments.get("account_type", "all")
        include_positions = arguments.get("include_positions", True)
        include_balance = arguments.get("include_balance", True)

        api = auth_manager.get_api()
        result: dict[str, Any] = {}

        # Get basic account info
        accounts = api.list_accounts()
        account_info = []
        for account in accounts:
            acc_type = "unknown"
            if hasattr(account, "account_type"):
                acc_type_str = str(account.account_type).upper()
                if "STOCK" in acc_type_str or acc_type_str == "S":
                    acc_type = "stock"
                elif "FUTURE" in acc_type_str or acc_type_str == "F":
                    acc_type = "futures"

            account_info.append(
                {
                    "account_id": account.account_id,
                    "broker_id": account.broker_id,
                    "account_type": acc_type,
                    "signed": account.signed,
                }
            )

        result["accounts"] = account_info

        # Get positions if requested
        if include_positions:
            positions_response = await _get_positions({"account_type": account_type})
            # Extract data from the response
            if positions_response and len(positions_response) > 0:
                positions_data = positions_response[0]
                if hasattr(positions_data, "content"):
                    import json

                    positions_text = (
                        positions_data.content[0].text
                        if hasattr(positions_data.content[0], "text")
                        else str(positions_data.content)
                    )
                    try:
                        result["positions"] = json.loads(positions_text)
                    except Exception:
                        result["positions"] = positions_text
                else:
                    result["positions"] = positions_data

        # Get balance if requested
        if include_balance:
            balance_response = await _get_account_balance(
                {"account_type": account_type}
            )
            if balance_response and len(balance_response) > 0:
                balance_data = balance_response[0]
                if hasattr(balance_data, "content"):
                    import json

                    balance_text = (
                        balance_data.content[0].text
                        if hasattr(balance_data.content[0], "text")
                        else str(balance_data.content)
                    )
                    try:
                        result["balance"] = json.loads(balance_text)
                    except Exception:
                        result["balance"] = balance_text
                else:
                    result["balance"] = balance_data

        return format_success_response(
            result, f"Retrieved complete account status for {account_type} account(s)"
        )

    except Exception as e:
        logger.error(f"Account status error: {e}")
        return format_error_response(e)


async def market_query(arguments: dict[str, Any]) -> list[Any]:
    """
    Query market data - search contracts, get quotes, or retrieve historical data.

    This unified tool intelligently determines what type of market data you need
    based on the parameters provided.

    Args:
        arguments: {
            # For searching contracts:
            "search": str (search keyword for contracts)
            "exchange": str (optional, filter by exchange)

            # For real-time quotes:
            "symbols": list[str] (list of contract codes for quotes)

            # For historical data:
            "symbol": str (single contract for historical data)
            "start_date": str (optional, YYYY-MM-DD)
            "end_date": str (optional, YYYY-MM-DD)
            "days": int (optional, default: 30)
        }

    Returns:
        Market data based on query type:
        - Search results (if "search" provided)
        - Real-time quotes (if "symbols" provided)
        - Historical K-bars (if "symbol" with dates provided)

    Examples:
        # Search for stocks
        {"search": "台積電"}

        # Get real-time quotes
        {"symbols": ["2330", "2317", "2454"]}

        # Get historical data
        {"symbol": "2330", "days": 30}

        # Get specific date range
        {"symbol": "2330", "start_date": "2024-01-01", "end_date": "2024-01-31"}
    """
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        # Determine query type based on arguments
        search_keyword = arguments.get("search")
        symbols = arguments.get("symbols")
        single_symbol = arguments.get("symbol")

        # Priority: search > symbols > single_symbol with history
        if search_keyword:
            # Search contracts
            return await _search_contracts(
                {
                    "keyword": search_keyword,
                    "exchange": arguments.get("exchange"),
                    "category": arguments.get("category"),
                }
            )

        elif symbols:
            # Get real-time snapshots
            return await _get_snapshots({"contracts": symbols})

        elif single_symbol:
            # Check if historical data is requested
            if (
                arguments.get("start_date")
                or arguments.get("end_date")
                or arguments.get("days")
            ):
                # Get historical K-bars
                return await _get_kbars(
                    {
                        "contract": single_symbol,
                        "start_date": arguments.get("start_date"),
                        "end_date": arguments.get("end_date"),
                        "timeframe": arguments.get("timeframe"),
                    }
                )
            else:
                # Get single snapshot
                return await _get_snapshots({"contracts": [single_symbol]})

        else:
            return format_error_response(
                ValueError(
                    "Please provide either 'search' for searching, "
                    "'symbols' for quotes, or 'symbol' for historical data"
                )
            )

    except Exception as e:
        logger.error(f"Market query error: {e}")
        return format_error_response(e)


async def order_management(arguments: dict[str, Any]) -> list[Any]:
    """
    Manage orders - place new orders, cancel existing ones, or list all orders.

    This unified tool handles all order-related operations in one place.

    Args:
        arguments: {
            "action": "place" | "cancel" | "list" (required)

            # For placing orders (action: "place"):
            "symbol": str (contract code)
            "side": "buy" | "sell"
            "quantity": int
            "price": float (optional, omit for market order)
            "order_type": "ROD" | "IOC" | "FOK" (optional, default: "ROD")

            # For canceling orders (action: "cancel"):
            "order_id": str (order ID to cancel)

            # For listing orders (action: "list"):
            # No additional parameters needed
        }

    Returns:
        Order operation result:
        - Order confirmation (for place)
        - Cancellation status (for cancel)
        - List of all orders (for list)

    Examples:
        # List all orders
        {"action": "list"}

        # Place market buy order
        {"action": "place", "symbol": "2330", "side": "buy", "quantity": 1000}

        # Place limit sell order
        {
            "action": "place",
            "symbol": "2330",
            "side": "sell",
            "quantity": 1000,
            "price": 500.0
        }

        # Cancel an order
        {"action": "cancel", "order_id": "abc123"}

    Note:
        Trading operations require SHIOAJI_TRADING_ENABLED=true
    """
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        action = arguments.get("action", "").lower()

        if action == "list":
            # List all orders
            return await _list_orders({})

        elif action == "place":
            # Place new order
            required_fields = ["symbol", "side", "quantity"]
            missing = [f for f in required_fields if f not in arguments]
            if missing:
                return format_error_response(
                    ValueError(f"Missing required fields for placing order: {missing}")
                )

            return await _place_order(
                {
                    "contract": arguments["symbol"],
                    "action": arguments["side"].capitalize(),
                    "quantity": arguments["quantity"],
                    "price": arguments.get("price"),
                    "order_type": arguments.get("order_type", "ROD"),
                }
            )

        elif action == "cancel":
            # Cancel order
            if "order_id" not in arguments:
                return format_error_response(
                    ValueError("Missing 'order_id' for canceling order")
                )

            return await _cancel_order({"order_id": arguments["order_id"]})

        else:
            return format_error_response(
                ValueError(
                    f"Invalid action: {action}. Must be 'place', 'cancel', or 'list'"
                )
            )

    except Exception as e:
        logger.error(f"Order management error: {e}")
        return format_error_response(e)


async def compliance_check(arguments: dict[str, Any]) -> list[Any]:
    """
    Check compliance status and run API tests for service terms.

    This tool helps ensure your account meets all regulatory requirements
    and API functionality is working correctly.

    Args:
        arguments: {
            "action": "status" | "test" (required)
            # "status" - Check current signing status
            # "test" - Run API compliance test
        }

    Returns:
        Compliance information:
        - Service terms signing status (for status check)
        - API test results (for test execution)

    Examples:
        # Check terms status
        {"action": "status"}

        # Run API test
        {"action": "test"}
    """
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        action = arguments.get("action", "status").lower()

        if action == "status":
            return await _check_terms_status({})
        elif action == "test":
            return await _run_api_test({})
        else:
            return format_error_response(
                ValueError(f"Invalid action: {action}. Must be 'status' or 'test'")
            )

    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        return format_error_response(e)

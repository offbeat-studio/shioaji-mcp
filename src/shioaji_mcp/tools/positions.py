"""Position management tools for Shioaji MCP server."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def get_positions(arguments: dict[str, Any]) -> list[Any]:
    """Get current positions."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        # Mock positions data
        mock_positions = [
            {
                "contract": "2330",
                "name": "台積電",
                "quantity": 1000,
                "avg_price": 480.0,
                "current_price": 500.0,
                "unrealized_pnl": 20000.0,
                "realized_pnl": 0.0,
            },
            {
                "contract": "2317",
                "name": "鴻海",
                "quantity": -500,
                "avg_price": 105.0,
                "current_price": 100.0,
                "unrealized_pnl": 2500.0,
                "realized_pnl": 0.0,
            },
        ]

        return format_success_response(
            mock_positions, f"Retrieved {len(mock_positions)} positions"
        )

    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return format_error_response(e)


async def get_account_balance(arguments: dict[str, Any]) -> list[Any]:
    """Get account balance information."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        # Mock account balance
        mock_balance = {
            "account_id": "1234567890",
            "currency": "TWD",
            "cash_balance": 1000000.0,
            "available_balance": 800000.0,
            "margin_used": 200000.0,
            "total_equity": 1200000.0,
            "unrealized_pnl": 22500.0,
            "realized_pnl": 0.0,
        }

        return format_success_response(mock_balance, "Account balance retrieved")

    except Exception as e:
        logger.error(f"Get account balance error: {e}")
        return format_error_response(e)

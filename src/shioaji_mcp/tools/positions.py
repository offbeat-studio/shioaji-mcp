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
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        api = auth_manager.get_api()
        
        try:
            # Get real positions from API
            positions = api.list_positions()
            
            position_list = []
            for position in positions:
                position_data = {
                    "contract": position.contract.code if hasattr(position.contract, 'code') else str(position.contract),
                    "name": position.contract.name if hasattr(position.contract, 'name') else "",
                    "quantity": position.quantity,
                    "avg_price": position.price,
                    "current_price": getattr(position, 'last_price', 0.0),
                    "unrealized_pnl": getattr(position, 'pnl', 0.0),
                    "realized_pnl": getattr(position, 'realized_pnl', 0.0),
                }
                position_list.append(position_data)

            return format_success_response(
                position_list, f"Retrieved {len(position_list)} positions"
            )
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return format_error_response(e)


async def get_account_balance(arguments: dict[str, Any]) -> list[Any]:
    """Get account balance information."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        api = auth_manager.get_api()
        
        try:
            # Get real account balance from API
            accounts = api.list_accounts()
            if not accounts:
                return format_error_response(Exception("No accounts found"))
            
            # Use the first account
            account = accounts[0]
            
            # Get account balance
            balance = api.account_balance()
            
            balance_data = {
                "account_id": account.account_id,
                "currency": "TWD",
                "cash_balance": getattr(balance, 'acc_balance', 0.0),
                "available_balance": getattr(balance, 'available_balance', 0.0),
                "margin_used": getattr(balance, 'margin_used', 0.0),
                "total_equity": getattr(balance, 'total_balance', 0.0),
                "unrealized_pnl": getattr(balance, 'unrealized_pnl', 0.0),
                "realized_pnl": getattr(balance, 'realized_pnl', 0.0),
            }

            return format_success_response(balance_data, "Account balance retrieved")
            
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Get account balance error: {e}")
        return format_error_response(e)

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
            from ..utils.shioaji_wrapper import get_shioaji
            sj = get_shioaji()
            
            # Get positions in shares instead of lots
            positions = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)
            
            if not positions:
                return format_success_response([], "No positions found")
            
            position_list = []
            for i, position in enumerate(positions):
                position_data = {
                    "index": i,
                    "type": type(position).__name__,
                    "raw_data": str(position)[:200],
                }
                
                # Extract position attributes
                for attr in ['code', 'symbol', 'quantity', 'price', 'pnl', 'direction', 'account', 'yd_quantity']:
                    if hasattr(position, attr):
                        value = getattr(position, attr)
                        if attr in ['quantity', 'yd_quantity'] and isinstance(value, (int, float)):
                            position_data[f'{attr}_shares'] = value
                            position_data[f'{attr}_lots'] = value // 1000
                            position_data[attr] = value
                        else:
                            position_data[attr] = str(value) if not isinstance(value, (int, float, bool)) else value
                
                # Calculate actual holding
                current_qty = position_data.get('quantity', 0)
                yd_qty = position_data.get('yd_quantity', 0)
                actual_holding = max(current_qty, yd_qty)
                
                position_data['actual_holding'] = actual_holding
                position_data['holding_lots'] = actual_holding // 1000
                position_data['holding_odd_shares'] = actual_holding % 1000
                        
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
            accounts = api.list_accounts()
            if not accounts:
                return format_error_response(Exception("No accounts found"))
            
            account = accounts[0]
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

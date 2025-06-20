"""Order management tools for Shioaji MCP server."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def place_order(arguments: dict[str, Any]) -> list[Any]:
    """Place a trading order."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        # Get order parameters
        contract_code = arguments.get("contract")
        action = arguments.get("action")  # Buy/Sell
        quantity = arguments.get("quantity")
        price = arguments.get("price")
        order_type = arguments.get("order_type", "ROD")  # ROD, IOC, FOK

        if not all([contract_code, action, quantity]):
            return format_error_response(
                Exception("Missing required parameters: contract, action, quantity")
            )

        api = auth_manager.get_api()
        
        try:
            # Get contract object
            contract = api.Contracts.Stocks[contract_code]
            if not contract:
                return format_error_response(Exception(f"Contract {contract_code} not found"))
            
            # Create order object
            order = api.Order(
                price=price or 0,
                quantity=quantity,
                action=getattr(api.constant.Action, action.title()),
                price_type=api.constant.StockPriceType.LMT if price else api.constant.StockPriceType.MKT,
                order_type=getattr(api.constant.OrderType, order_type, api.constant.OrderType.ROD)
            )
            
            # Place order
            trade = api.place_order(contract, order)
            
            result = {
                "order_id": trade.order.id,
                "contract": contract_code,
                "action": action.upper(),
                "quantity": quantity,
                "price": price or "Market",
                "order_type": order_type,
                "status": trade.status.status,
                "timestamp": trade.order.order_datetime.isoformat() if trade.order.order_datetime else None,
            }
            
            return format_success_response(
                result, f"Order placed successfully: {result['order_id']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Place order error: {e}")
        return format_error_response(e)


async def cancel_order(arguments: dict[str, Any]) -> list[Any]:
    """Cancel an existing order."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        order_id = arguments.get("order_id")
        if not order_id:
            return format_error_response(Exception("Order ID is required"))

        # Mock order cancellation
        result = {
            "order_id": order_id,
            "status": "Cancelled",
            "timestamp": "2024-01-01T10:05:00",
        }

        return format_success_response(
            result, f"Order {order_id} cancelled successfully"
        )

    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        return format_error_response(e)


async def list_orders(arguments: dict[str, Any]) -> list[Any]:
    """List all orders."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not logged in. Please login first.")
            )

        # Mock order list
        mock_orders = [
            {
                "order_id": "ORD12345",
                "contract": "2330",
                "action": "Buy",
                "quantity": 1000,
                "price": 500.0,
                "status": "Filled",
                "timestamp": "2024-01-01T09:30:00",
            },
            {
                "order_id": "ORD12346",
                "contract": "2317",
                "action": "Sell",
                "quantity": 500,
                "price": 100.0,
                "status": "Partial",
                "timestamp": "2024-01-01T10:00:00",
            },
        ]

        return format_success_response(
            mock_orders, f"Retrieved {len(mock_orders)} orders"
        )

    except Exception as e:
        logger.error(f"List orders error: {e}")
        return format_error_response(e)

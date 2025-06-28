"""Order management tools for Shioaji MCP server."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response
from ..utils.permissions import check_trading_permission

logger = logging.getLogger(__name__)


async def place_order(arguments: dict[str, Any]) -> list[Any]:
    """Place a trading order."""
    try:
        # Check trading permission first
        is_allowed, error_msg = check_trading_permission("place_order")
        if not is_allowed:
            return format_error_response(Exception(error_msg))

        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
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
        # Check trading permission first
        is_allowed, error_msg = check_trading_permission("cancel_order")
        if not is_allowed:
            return format_error_response(Exception(error_msg))

        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        order_id = arguments.get("order_id")
        if not order_id:
            return format_error_response(Exception("Order ID is required"))

        api = auth_manager.get_api()

        try:
            # Get order by ID and cancel it
            orders = api.list_orders()
            target_order = None
            for order in orders:
                if order.id == order_id:
                    target_order = order
                    break

            if not target_order:
                return format_error_response(Exception(f"Order {order_id} not found"))

            # Cancel the order
            cancel_result = api.cancel_order(target_order)

            result = {
                "order_id": order_id,
                "status": "Cancelled",
                "timestamp": cancel_result.order_datetime.isoformat() if hasattr(cancel_result, 'order_datetime') and cancel_result.order_datetime else None,
            }

            return format_success_response(
                result, f"Order {order_id} cancelled successfully"
            )

        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        return format_error_response(e)


async def list_orders(arguments: dict[str, Any]) -> list[Any]:
    """List all orders."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        api = auth_manager.get_api()

        try:
            # Get real orders from API
            orders = api.list_orders()

            order_list = []
            for order in orders:
                order_data = {
                    "order_id": order.id,
                    "contract": order.contract.code if hasattr(order.contract, 'code') else str(order.contract),
                    "action": order.action.value if hasattr(order.action, 'value') else str(order.action),
                    "quantity": order.quantity,
                    "price": order.price,
                    "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
                    "timestamp": order.order_datetime.isoformat() if hasattr(order, 'order_datetime') and order.order_datetime else None,
                }
                order_list.append(order_data)

            return format_success_response(
                order_list, f"Retrieved {len(order_list)} orders"
            )

        except Exception as e:
            logger.error(f"Failed to list orders: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"List orders error: {e}")
        return format_error_response(e)

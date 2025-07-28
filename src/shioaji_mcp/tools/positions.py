"""Position management tools for Shioaji MCP server."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def get_positions(arguments: dict[str, Any]) -> list[Any]:
    """Get current positions from both stock and futures accounts."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        api = auth_manager.get_api()
        account_type = arguments.get("account_type", "all")  # all, stock, futures
        logger.info(f"get_positions called with account_type: '{account_type}'")

        try:
            from ..utils.shioaji_wrapper import get_shioaji

            sj = get_shioaji()

            all_positions = []

            # Get stock positions
            if (
                account_type in ["all", "stock"]
                and hasattr(api, "stock_account")
                and api.stock_account
            ):
                try:
                    stock_positions = api.list_positions(
                        api.stock_account, unit=sj.constant.Unit.Share
                    )
                    for i, position in enumerate(stock_positions):
                        position_data = {
                            "index": i,
                            "account_type": "stock",
                            "type": type(position).__name__,
                            "raw_data": str(position)[:200],
                        }

                        # Extract position attributes
                        for attr in [
                            "code",
                            "symbol",
                            "quantity",
                            "price",
                            "pnl",
                            "direction",
                            "account",
                            "yd_quantity",
                        ]:
                            if hasattr(position, attr):
                                value = getattr(position, attr)
                                if attr in ["quantity", "yd_quantity"] and isinstance(
                                    value, (int, float)
                                ):
                                    position_data[f"{attr}_shares"] = value
                                    position_data[f"{attr}_lots"] = value // 1000
                                    position_data[attr] = value
                                else:
                                    position_data[attr] = (
                                        str(value)
                                        if not isinstance(value, (int, float, bool))
                                        else value
                                    )

                        # Calculate actual holding for stocks
                        current_qty = position_data.get("quantity", 0)
                        yd_qty = position_data.get("yd_quantity", 0)
                        actual_holding = max(current_qty, yd_qty)

                        position_data["actual_holding"] = actual_holding
                        position_data["holding_lots"] = actual_holding // 1000
                        position_data["holding_odd_shares"] = actual_holding % 1000

                        all_positions.append(position_data)

                except Exception as e:
                    logger.warning(f"Failed to get stock positions: {e}")

            # Get futures positions
            logger.info(f"Checking futures account: has_futopt_account={hasattr(api, 'futopt_account')}, futopt_account={getattr(api, 'futopt_account', None)}")
            if (
                account_type in ["all", "futures"]
                and hasattr(api, "futopt_account")
                and api.futopt_account
            ):
                try:
                    logger.info("Attempting to get futures positions...")
                    futures_positions = api.list_positions(api.futopt_account)
                    logger.info(f"Got {len(futures_positions)} futures positions")
                    for i, position in enumerate(futures_positions):
                        position_data = {
                            "index": i
                            + len(
                                [
                                    p
                                    for p in all_positions
                                    if p.get("account_type") == "stock"
                                ]
                            ),
                            "account_type": "futures",
                            "type": type(position).__name__,
                            "raw_data": str(position)[:200],
                        }

                        # Extract position attributes for futures
                        for attr in [
                            "code",
                            "symbol",
                            "quantity",
                            "price",
                            "pnl",
                            "direction",
                            "account",
                            "yd_quantity",
                        ]:
                            if hasattr(position, attr):
                                value = getattr(position, attr)
                                position_data[attr] = (
                                    str(value)
                                    if not isinstance(value, (int, float, bool))
                                    else value
                                )

                        all_positions.append(position_data)

                except Exception as e:
                    logger.warning(f"Failed to get futures positions: {e}")

            # Filter positions based on account_type after collecting all
            if account_type != "all":
                filtered_positions = [
                    pos for pos in all_positions 
                    if pos.get("account_type") == account_type
                ]
                all_positions = filtered_positions
                logger.info(f"Filtered to {len(all_positions)} positions for account_type: {account_type}")

            if not all_positions:
                account_msg = (
                    f" for {account_type} account(s)" if account_type != "all" else ""
                )
                return format_success_response([], f"No positions found{account_msg}")

            # Create appropriate message
            if account_type == "all":
                result_msg = f"Retrieved {len(all_positions)} positions (all accounts)"
            else:
                result_msg = f"Retrieved {len(all_positions)} positions ({account_type} account only)"

            return format_success_response(all_positions, result_msg)

        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return format_error_response(e)


async def get_account_balance(arguments: dict[str, Any]) -> list[Any]:
    """Get account balance information for both stock and futures accounts."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception(
                    "Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            )

        api = auth_manager.get_api()
        account_type = arguments.get("account_type", "all")  # all, stock, futures

        try:
            accounts = api.list_accounts()
            if not accounts:
                return format_error_response(Exception("No accounts found"))

            balance_data = []

            for account in accounts:
                try:
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

                    # Skip if not requested account type
                    if account_type != "all" and acc_type != account_type:
                        continue

                    # Get balance for this account
                    logger.info(f"Getting balance for account {getattr(account, 'account_id', 'unknown')} type: {acc_type}")
                    if (
                        acc_type == "stock"
                        and hasattr(api, "stock_account")
                        and api.stock_account
                    ):
                        balance = api.account_balance(api.stock_account)
                        logger.info("Got stock account balance")
                    elif (
                        acc_type == "futures"
                        and hasattr(api, "futopt_account")
                        and api.futopt_account
                    ):
                        balance = api.account_balance(api.futopt_account)
                        logger.info("Got futures account balance")
                    else:
                        # Fallback - try with account directly
                        balance = api.account_balance(account)

                    account_balance = {
                        "account_id": getattr(account, "account_id", "N/A"),
                        "account_type": acc_type,
                        "currency": "TWD",
                        "cash_balance": getattr(balance, "acc_balance", 0.0),
                        "available_balance": getattr(balance, "available_balance", 0.0),
                        "margin_used": getattr(balance, "margin_used", 0.0),
                        "total_equity": getattr(balance, "total_balance", 0.0),
                        "unrealized_pnl": getattr(balance, "unrealized_pnl", 0.0),
                        "realized_pnl": getattr(balance, "realized_pnl", 0.0),
                    }

                    # Add futures-specific fields if available
                    if acc_type == "futures":
                        account_balance.update(
                            {
                                "maintenance_margin": getattr(
                                    balance, "maintenance_margin", 0.0
                                ),
                                "initial_margin": getattr(
                                    balance, "initial_margin", 0.0
                                ),
                                "option_market_value": getattr(
                                    balance, "option_market_value", 0.0
                                ),
                            }
                        )

                    balance_data.append(account_balance)

                except Exception as e:
                    logger.warning(
                        f"Failed to get balance for account {getattr(account, 'account_id', 'unknown')}: {e}"
                    )
                    continue

            if not balance_data:
                account_msg = (
                    f" for {account_type} account(s)" if account_type != "all" else ""
                )
                return format_error_response(
                    Exception(f"No account balance found{account_msg}")
                )

            result_msg = f"Retrieved balance for {len(balance_data)} account(s)"
            if account_type != "all":
                result_msg += f" ({account_type})"

            return format_success_response(balance_data, result_msg)

        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Get account balance error: {e}")
        return format_error_response(e)

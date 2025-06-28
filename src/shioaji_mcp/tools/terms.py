"""Service terms and API testing tools for Shioaji."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response
from ..utils.shioaji_wrapper import get_shioaji

logger = logging.getLogger(__name__)


async def check_terms_status(arguments: dict[str, Any]) -> list[Any]:
    """Check service terms signing status."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        api = auth_manager.get_api()
        accounts = api.list_accounts()

        status_info = []
        for account in accounts:
            account_info = {
                "account_id": account.account_id,
                "broker_id": account.broker_id,
                "account_type": getattr(account, 'account_type', 'Unknown'),
                "signed": getattr(account, 'signed', False),
                "username": getattr(account, 'username', ''),
            }

            if hasattr(account, 'person_id'):
                account_info["person_id"] = account.person_id

            status_info.append(account_info)

        return format_success_response(
            status_info,
            "Service terms status retrieved successfully. 'signed=True' means API testing completed."
        )

    except Exception as e:
        logger.error(f"Check terms status error: {e}")
        return format_error_response(e)


async def run_api_test(arguments: dict[str, Any]) -> list[Any]:
    """Run API test for service terms compliance."""
    try:
        sj = get_shioaji()

        # Create simulation API instance
        test_api = sj.Shioaji(simulation=True)

        # Get credentials from auth manager
        import os
        api_key = os.getenv("SHIOAJI_API_KEY")
        secret_key = os.getenv("SHIOAJI_SECRET_KEY")

        if not all([api_key, secret_key]):
            return format_error_response(
                Exception("Missing SHIOAJI_API_KEY or SHIOAJI_SECRET_KEY environment variables")
            )

        # Step 1: Login test
        logger.info("Starting API login test...")
        accounts = test_api.login(api_key=api_key, secret_key=secret_key)

        test_results = {
            "login_test": {
                "status": "success",
                "message": "Login test completed successfully",
                "accounts": len(accounts) if accounts else 0
            }
        }

        # Step 2: Stock order test (if stock account available)
        stock_account = None
        for account in accounts:
            if hasattr(account, 'account_type') and 'stock' in str(account.account_type).lower():
                stock_account = account
                break

        if stock_account:
            try:
                logger.info("Starting stock order test...")

                # Get stock contract (2890 - 永豐金)
                contract = test_api.Contracts.Stocks.TSE["2890"]

                # Create test order
                order = test_api.Order(
                    price=18,
                    quantity=1,
                    action=sj.constant.Action.Buy,
                    price_type=sj.constant.StockPriceType.LMT,
                    order_type=sj.constant.OrderType.ROD,
                    account=stock_account
                )

                # Place test order
                trade = test_api.place_order(contract, order)

                test_results["stock_order_test"] = {
                    "status": "success" if trade.status.status != "Failed" else "failed",
                    "message": f"Stock order test completed. Status: {trade.status.status}",
                    "order_id": trade.status.id if hasattr(trade.status, 'id') else None
                }

            except Exception as e:
                test_results["stock_order_test"] = {
                    "status": "error",
                    "message": f"Stock order test failed: {str(e)}"
                }

        # Step 3: Futures order test (if futures account available)
        futures_account = None
        for account in accounts:
            if hasattr(account, 'account_type') and 'future' in str(account.account_type).lower():
                futures_account = account
                break

        if futures_account:
            try:
                logger.info("Starting futures order test...")

                # Get nearest TXF contract
                txf_contracts = [
                    x for x in test_api.Contracts.Futures.TXF
                    if x.code[-2:] not in ["R1", "R2"]
                ]
                contract = min(txf_contracts, key=lambda x: x.delivery_date)

                # Create test order
                order = test_api.Order(
                    action=sj.constant.Action.Buy,
                    price=15000,
                    quantity=1,
                    price_type=sj.constant.FuturesPriceType.LMT,
                    order_type=sj.constant.OrderType.ROD,
                    octype=sj.constant.FuturesOCType.Auto,
                    account=futures_account
                )

                # Place test order
                trade = test_api.place_order(contract, order)

                test_results["futures_order_test"] = {
                    "status": "success" if trade.status.status != "Failed" else "failed",
                    "message": f"Futures order test completed. Status: {trade.status.status}",
                    "order_id": trade.status.id if hasattr(trade.status, 'id') else None
                }

            except Exception as e:
                test_results["futures_order_test"] = {
                    "status": "error",
                    "message": f"Futures order test failed: {str(e)}"
                }

        # Logout from test API
        test_api.logout()

        # Add important notes
        test_results["notes"] = [
            "API testing can only be performed during business hours (Mon-Fri 08:00-20:00)",
            "18:00-20:00: Only Taiwan IP addresses allowed",
            "Stock and futures accounts need separate testing",
            "Orders must be placed with at least 1 second interval",
            "API signing must be completed before API testing",
            "Wait ~5 minutes for test review after completion"
        ]

        return format_success_response(
            test_results,
            "API test completed. Check results for each test component."
        )

    except Exception as e:
        logger.error(f"API test error: {e}")
        return format_error_response(e)

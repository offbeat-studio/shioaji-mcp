"""Market data tools for Shioaji MCP server."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def get_snapshots(arguments: dict[str, Any]) -> list[Any]:
    """Get real-time market snapshots."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        # Get contract codes
        contracts = arguments.get("contracts", [])
        if not contracts:
            return format_error_response(Exception("No contracts specified"))

        api = auth_manager.get_api()
        snapshots = []

        for contract_code in contracts:
            try:
                # Get contract object
                contract = api.Contracts.Stocks[contract_code]
                if not contract:
                    continue

                # Get snapshot data
                snapshot = api.snapshots([contract])[0]

                snapshots.append({
                    "code": contract_code,
                    "name": contract.name,
                    "close": snapshot.close,
                    "open": snapshot.open,
                    "high": snapshot.high,
                    "low": snapshot.low,
                    "volume": snapshot.volume,
                    "bid_price": snapshot.bid_price,
                    "ask_price": snapshot.ask_price,
                    "timestamp": snapshot.ts.isoformat() if snapshot.ts else datetime.now().isoformat(),
                })
            except Exception as e:
                logger.warning(f"Failed to get snapshot for {contract_code}: {e}")
                continue

        return format_success_response(
            snapshots, f"Retrieved snapshots for {len(snapshots)} contracts"
        )

    except Exception as e:
        logger.error(f"Get snapshots error: {e}")
        return format_error_response(e)


async def get_kbars(arguments: dict[str, Any]) -> list[Any]:
    """Get historical K-bar data."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        # Get parameters
        contract_code = arguments.get("contract")

        if not contract_code:
            return format_error_response(Exception("Contract code is required"))

        api = auth_manager.get_api()

        try:
            # Get contract object
            contract = api.Contracts.Stocks[contract_code]
            if not contract:
                return format_error_response(Exception(f"Contract {contract_code} not found"))

            # Get parameters with defaults
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")

            # Set default date range if not provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")

            # Get K-bar data
            kbars = api.kbars(
                contract=contract,
                start=start_date,
                end=end_date,
                timeout=30000
            )

            # Format K-bar data
            formatted_kbars = []
            for kbar in kbars:
                formatted_kbars.append({
                    "date": kbar.ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": kbar.Open,
                    "high": kbar.High,
                    "low": kbar.Low,
                    "close": kbar.Close,
                    "volume": kbar.Volume,
                })

            return format_success_response(
                formatted_kbars, f"Retrieved {len(formatted_kbars)} K-bars for {contract_code}"
            )

        except Exception as e:
            logger.error(f"Failed to get K-bars for {contract_code}: {e}")
            return format_error_response(e)

    except Exception as e:
        logger.error(f"Get K-bars error: {e}")
        return format_error_response(e)

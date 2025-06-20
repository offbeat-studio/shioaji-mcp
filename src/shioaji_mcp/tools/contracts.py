"""Contract search tools for Shioaji MCP server."""

import logging
from typing import Any

from ..utils.auth import auth_manager
from ..utils.formatters import format_error_response, format_success_response

logger = logging.getLogger(__name__)


async def search_contracts(arguments: dict[str, Any]) -> list[Any]:
    """Search for trading contracts."""
    try:
        if not auth_manager.is_connected():
            return format_error_response(
                Exception("Not connected. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
            )

        # Get search parameters
        keyword = arguments.get("keyword", "")
        exchange = arguments.get("exchange", "")
        category = arguments.get("category", "")

        api = auth_manager.get_api()
        contracts = []
        
        # Search in different contract types
        contract_sources = [
            ("Stock", "TSE", api.Contracts.Stocks),
        ]
        
        for cat, exch, source in contract_sources:
            if category and category.lower() != cat.lower():
                continue
            if exchange and exchange.upper() != exch:
                continue
                
            try:
                for code, contract in source.items():
                    if keyword:
                        if (keyword.lower() not in contract.name.lower() and 
                            keyword not in code):
                            continue
                    
                    contracts.append({
                        "code": code,
                        "symbol": getattr(contract, "symbol", code),
                        "name": contract.name,
                        "category": cat,
                        "exchange": exch,
                        "currency": getattr(contract, "currency", "TWD")
                    })
                    
                    # Limit results
                    if len(contracts) >= 50:
                        break
            except Exception as e:
                logger.warning(f"Error searching {cat} contracts: {e}")
                continue
                
            if len(contracts) >= 50:
                break

        return format_success_response(
            contracts,
            f"Found {len(contracts)} contracts"
        )

    except Exception as e:
        logger.error(f"Contract search error: {e}")
        return format_error_response(e)

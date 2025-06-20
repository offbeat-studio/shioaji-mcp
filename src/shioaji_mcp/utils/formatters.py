"""Data formatting utilities."""

import json
from typing import Any


def format_account_info(account_data: Any) -> dict[str, Any]:
    """Format account information for MCP response."""
    if hasattr(account_data, "__dict__"):
        return {
            "account_id": getattr(account_data, "account_id", "N/A"),
            "broker_id": getattr(account_data, "broker_id", "N/A"),
            "account_type": getattr(account_data, "account_type", "N/A"),
            "signed": getattr(account_data, "signed", False),
        }
    return {"raw_data": str(account_data)}


def format_contract_info(contract: Any) -> dict[str, Any]:
    """Format contract information for MCP response."""
    if hasattr(contract, "__dict__"):
        return {
            "code": getattr(contract, "code", "N/A"),
            "symbol": getattr(contract, "symbol", "N/A"),
            "name": getattr(contract, "name", "N/A"),
            "category": getattr(contract, "category", "N/A"),
            "exchange": getattr(contract, "exchange", "N/A"),
        }
    return {"raw_data": str(contract)}


def format_error_response(error: Exception) -> list[dict[str, str]]:
    """Format error response for MCP."""
    return [{"type": "text", "text": f"Error: {str(error)}"}]


def format_success_response(data: Any, message: str = None) -> list[dict[str, Any]]:
    """Format success response for MCP."""
    response = []

    if message:
        response.append({"type": "text", "text": message})

    if data:
        if isinstance(data, dict | list):
            response.append(
                {"type": "text", "text": json.dumps(data, indent=2, default=str)}
            )
        else:
            response.append({"type": "text", "text": str(data)})

    return response

"""Permission management for Shioaji MCP server."""

import os
import logging

logger = logging.getLogger(__name__)


def is_trading_enabled() -> bool:
    """
    Check if trading operations are enabled based on environment variable.
    
    Returns:
        bool: True if trading is allowed, False otherwise
    """
    # Get the environment variable (case-insensitive)
    trading_enabled = os.getenv('SHIOAJI_TRADING_ENABLED', 'false').lower()
    
    # Only allow trading if explicitly set to 'true'
    enabled = trading_enabled in ['true', '1', 'yes', 'on']
    
    if not enabled:
        logger.info("Trading operations are disabled. Set SHIOAJI_TRADING_ENABLED=true to enable.")
    
    return enabled


def check_trading_permission(operation_name: str) -> tuple[bool, str]:
    """
    Check if a trading operation is permitted.
    
    Args:
        operation_name (str): Name of the trading operation
        
    Returns:
        tuple[bool, str]: (is_allowed, error_message)
    """
    if not is_trading_enabled():
        error_msg = (
            f"Trading operation '{operation_name}' is not permitted. "
            "Set SHIOAJI_TRADING_ENABLED=true in your MCP configuration to enable trading operations."
        )
        logger.warning(f"Blocked trading operation: {operation_name}")
        return False, error_msg
    
    return True, ""
"""Shioaji wrapper with fallback to mock."""

import logging

logger = logging.getLogger(__name__)

def get_shioaji():
    """Get Shioaji module with fallback to mock."""
    try:
        import shioaji as sj
        return sj
    except (ImportError, OSError) as e:
        logger.warning(f"Failed to import shioaji: {e}. Using mock implementation.")
        from .mock_shioaji import sj
        return sj
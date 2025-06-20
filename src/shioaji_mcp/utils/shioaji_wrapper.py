"""Shioaji wrapper for real API access."""

import logging

logger = logging.getLogger(__name__)

def get_shioaji():
    """Get Shioaji module."""
    try:
        import shioaji as sj
        logger.info("Successfully imported real Shioaji module")
        return sj
    except ImportError as e:
        error_msg = str(e)
        if "libc++.1.dylib" in error_msg:
            logger.error(f"Shioaji library dependency issue: {e}")
            raise ImportError(
                "Shioaji has a library dependency issue. This is a known issue on some macOS systems. "
                "Try installing with conda or using a different Python environment."
            ) from e
        else:
            logger.error(f"Failed to import shioaji: {e}")
            raise ImportError(
                "Shioaji package not found. Please install it with: pip install shioaji"
            ) from e
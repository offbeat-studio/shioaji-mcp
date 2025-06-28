"""Authentication utilities for Shioaji API."""

import logging
import os

from dotenv import load_dotenv

from .shioaji_wrapper import get_shioaji

# Don't import shioaji at module level to avoid read-only filesystem issues

logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()


class ShioajiAuth:
    """Shioaji authentication manager."""

    def __init__(self):
        self.api = None
        self._is_connected = False
        self._sj = None

    def _auto_connect(self):
        """Auto-connect using environment variables."""
        if self._is_connected:
            return

        try:
            api_key = os.getenv("SHIOAJI_API_KEY")
            secret_key = os.getenv("SHIOAJI_SECRET_KEY")

            if not all([api_key, secret_key]):
                raise ValueError("Missing SHIOAJI_API_KEY or SHIOAJI_SECRET_KEY environment variables")

            # Test Shioaji import before attempting connection
            try:
                self._sj = get_shioaji()
                self.api = self._sj.Shioaji()
            except ImportError as import_error:
                raise RuntimeError(f"Shioaji import failed: {import_error}") from import_error

            # Login with API credentials only
            self.api.login(
                api_key=api_key,
                secret_key=secret_key,
            )

            self._is_connected = True
            logger.info("Successfully auto-connected to Shioaji")

        except Exception as e:
            error_msg = str(e)
            if "expired" in error_msg.lower():
                logger.error(f"API key expired: {e}")
                raise RuntimeError(f"Shioaji API key has expired. Please get a new API key from your broker: {e}") from e
            else:
                logger.error(f"Auto-connect failed: {e}")
            self._is_connected = False
            raise

    async def logout(self) -> dict:
        """Logout from Shioaji API."""
        try:
            if self.api and self._is_connected:
                self.api.logout()
                self._is_connected = False
                logger.info("Successfully logged out from Shioaji")
                return {"success": True, "message": "Logout successful"}
            else:
                return {"success": True, "message": "Already logged out"}
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {"success": False, "message": f"Logout failed: {str(e)}"}

    def is_connected(self) -> bool:
        """Check if connected to Shioaji API."""
        if not self._is_connected:
            try:
                self._auto_connect()
            except Exception:
                return False
        return self._is_connected and self.api is not None

    def get_api(self):
        """Get the Shioaji API instance."""
        if not self.is_connected():
            raise RuntimeError("Not connected to Shioaji API. Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables.")
        return self.api


# Global authentication instance
auth_manager = ShioajiAuth()

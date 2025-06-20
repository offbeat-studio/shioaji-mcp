"""Authentication utilities for Shioaji API."""

import logging
import os

from dotenv import load_dotenv

from .shioaji_wrapper import get_shioaji

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ShioajiAuth:
    """Shioaji authentication manager."""

    def __init__(self):
        self.api = None
        self._is_connected = False
        self._sj = None

    async def login(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        person_id: str | None = None,
        password: str | None = None,
    ) -> dict:
        """Login to Shioaji API."""
        try:
            # Use provided credentials or fall back to environment variables
            api_key = api_key or os.getenv("SHIOAJI_API_KEY")
            secret_key = secret_key or os.getenv("SHIOAJI_SECRET_KEY")
            person_id = person_id or os.getenv("SHIOAJI_PERSON_ID")
            password = password or os.getenv("SHIOAJI_PASSWORD")

            if not all([api_key, secret_key, person_id, password]):
                raise ValueError("Missing required credentials")

            # Get Shioaji module and create instance
            self._sj = get_shioaji()
            self.api = self._sj.Shioaji()

            # Login
            accounts = self.api.login(
                api_key=api_key,
                secret_key=secret_key,
                person_id=person_id,
                passwd=password,
            )

            self._is_connected = True
            logger.info("Successfully logged in to Shioaji")

            return {
                "success": True,
                "message": "Login successful",
                "accounts": [acc.account_id for acc in accounts] if accounts else [],
            }

        except Exception as e:
            logger.error(f"Login failed: {e}")
            self._is_connected = False
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
            }

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
        return self._is_connected and self.api is not None

    def get_api(self):
        """Get the Shioaji API instance."""
        if not self.is_connected():
            raise RuntimeError("Not connected to Shioaji API. Please login first.")
        return self.api


# Global authentication instance
auth_manager = ShioajiAuth()

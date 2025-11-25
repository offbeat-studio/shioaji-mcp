"""Simplified Python SDK for Shioaji - Direct usage without MCP."""

import os
from datetime import datetime, timedelta
from typing import Any

from .utils.auth import auth_manager


class ShioajiSDK:
    """
    Simplified Shioaji SDK for direct Python usage.

    This SDK provides a clean, Pythonic interface to Shioaji functionality
    without requiring MCP protocol.

    Example:
        >>> from shioaji_mcp.sdk import ShioajiSDK
        >>>
        >>> # Initialize (uses environment variables for credentials)
        >>> sdk = ShioajiSDK()
        >>>
        >>> # Or provide credentials directly
        >>> sdk = ShioajiSDK(api_key="your_key", secret_key="your_secret")
        >>>
        >>> # Get account info
        >>> accounts = sdk.get_accounts()
        >>>
        >>> # Search for stocks
        >>> results = sdk.search_stocks("台積電")
        >>>
        >>> # Get real-time quote
        >>> quote = sdk.get_quote("2330")
        >>> print(f"TSMC: ${quote['close']}")
    """

    def __init__(
        self, api_key: str | None = None, secret_key: str | None = None
    ) -> None:
        """
        Initialize Shioaji SDK.

        Args:
            api_key: Shioaji API key (optional, will use SHIOAJI_API_KEY env var)
            secret_key: Shioaji secret key (optional, will use SHIOAJI_SECRET_KEY env var)
        """
        # Set credentials if provided
        if api_key:
            os.environ["SHIOAJI_API_KEY"] = api_key
        if secret_key:
            os.environ["SHIOAJI_SECRET_KEY"] = secret_key

        self._api = None

    @property
    def api(self):
        """Get or create Shioaji API instance."""
        if self._api is None:
            if not auth_manager.is_connected():
                raise RuntimeError(
                    "Not connected to Shioaji. Please provide api_key and secret_key, "
                    "or set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables."
                )
            self._api = auth_manager.get_api()
        return self._api

    def get_accounts(self) -> list[dict[str, Any]]:
        """
        Get list of accounts.

        Returns:
            List of account dictionaries with account information

        Example:
            >>> accounts = sdk.get_accounts()
            >>> for acc in accounts:
            ...     print(f"{acc['account_id']}: {acc['account_type']}")
        """
        accounts = self.api.list_accounts()
        result = []

        for account in accounts:
            # Determine account type
            acc_type = "unknown"
            if hasattr(account, "account_type"):
                acc_type_str = str(account.account_type).upper()
                if "STOCK" in acc_type_str or acc_type_str == "S":
                    acc_type = "stock"
                elif "FUTURE" in acc_type_str or acc_type_str == "F":
                    acc_type = "futures"

            result.append(
                {
                    "account_id": account.account_id,
                    "broker_id": account.broker_id,
                    "account_type": acc_type,
                    "signed": account.signed,
                }
            )

        return result

    def search_stocks(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for stocks by keyword.

        Args:
            keyword: Search keyword (code or name)
            limit: Maximum number of results

        Returns:
            List of matching contracts

        Example:
            >>> results = sdk.search_stocks("台積電")
            >>> results = sdk.search_stocks("2330")
        """
        results = []
        for symbol, contract in self.api.Contracts.Stocks.items():
            if keyword.upper() in symbol.upper() or keyword in contract.name:
                results.append(
                    {
                        "code": symbol,
                        "name": contract.name,
                        "exchange": contract.exchange,
                        "category": contract.category,
                    }
                )
                if len(results) >= limit:
                    break

        return results

    def get_quote(self, symbol: str) -> dict[str, Any]:
        """
        Get real-time quote for a stock.

        Args:
            symbol: Stock symbol (e.g., "2330" for TSMC)

        Returns:
            Dictionary with quote information

        Raises:
            ValueError: If contract not found

        Example:
            >>> quote = sdk.get_quote("2330")
            >>> print(f"Price: ${quote['close']}, Volume: {quote['volume']}")
        """
        contract = self.api.Contracts.Stocks.get(symbol)
        if not contract:
            raise ValueError(f"Contract {symbol} not found")

        snapshot = self.api.snapshots([contract])[0]

        return {
            "code": symbol,
            "name": contract.name,
            "open": snapshot.open,
            "high": snapshot.high,
            "low": snapshot.low,
            "close": snapshot.close,
            "volume": snapshot.volume,
            "bid_price": snapshot.bid_price[0] if snapshot.bid_price else None,
            "ask_price": snapshot.ask_price[0] if snapshot.ask_price else None,
            "timestamp": (
                snapshot.ts.isoformat() if snapshot.ts else datetime.now().isoformat()
            ),
        }

    def get_quotes(self, symbols: list[str]) -> list[dict[str, Any]]:
        """
        Get real-time quotes for multiple stocks.

        Args:
            symbols: List of stock symbols

        Returns:
            List of quote dictionaries

        Example:
            >>> quotes = sdk.get_quotes(["2330", "2317", "2454"])
            >>> for quote in quotes:
            ...     print(f"{quote['name']}: ${quote['close']}")
        """
        return [self.get_quote(symbol) for symbol in symbols]

    def get_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Get historical K-bar data.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD format, optional)
            end_date: End date (YYYY-MM-DD format, optional)
            days: Number of days to fetch if dates not specified

        Returns:
            List of K-bar dictionaries

        Example:
            >>> # Get last 30 days
            >>> history = sdk.get_history("2330")
            >>>
            >>> # Get specific date range
            >>> history = sdk.get_history("2330", "2024-01-01", "2024-01-31")
        """
        contract = self.api.Contracts.Stocks.get(symbol)
        if not contract:
            raise ValueError(f"Contract {symbol} not found")

        # Set default date range if not provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        kbars = self.api.kbars(
            contract=contract, start=start_date, end=end_date, timeout=30000
        )

        return [
            {
                "date": kbar.ts.strftime("%Y-%m-%d %H:%M:%S"),
                "open": kbar.Open,
                "high": kbar.High,
                "low": kbar.Low,
                "close": kbar.Close,
                "volume": kbar.Volume,
            }
            for kbar in kbars
        ]

    def get_positions(
        self, account_type: str = "all"
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get current positions.

        Args:
            account_type: "all", "stock", or "futures"

        Returns:
            Dictionary with 'stock' and/or 'futures' keys containing position lists

        Example:
            >>> positions = sdk.get_positions()
            >>> for pos in positions['stock']:
            ...     print(f"{pos['code']}: {pos['quantity']} shares")
        """
        result: dict[str, list[dict[str, Any]]] = {}

        if account_type in ["all", "stock"]:
            try:
                stock_positions = self.api.list_positions(self.api.stock_account)
                if stock_positions:
                    result["stock"] = [
                        {
                            "code": pos.code,
                            "quantity": pos.quantity,
                            "price": pos.price,
                            "pnl": pos.pnl if hasattr(pos, "pnl") else 0,
                        }
                        for pos in stock_positions
                    ]
            except Exception:
                result["stock"] = []

        if account_type in ["all", "futures"]:
            try:
                futures_positions = self.api.list_positions(self.api.futopt_account)
                if futures_positions:
                    result["futures"] = [
                        {
                            "code": pos.code,
                            "quantity": pos.quantity,
                            "price": pos.price,
                            "pnl": pos.pnl if hasattr(pos, "pnl") else 0,
                        }
                        for pos in futures_positions
                    ]
            except Exception:
                result["futures"] = []

        return result

    def get_balance(self, account_type: str = "all") -> dict[str, dict[str, float]]:
        """
        Get account balance.

        Args:
            account_type: "all", "stock", or "futures"

        Returns:
            Dictionary with balance information

        Example:
            >>> balance = sdk.get_balance()
            >>> print(f"Stock available: ${balance['stock']['available']}")
            >>> print(f"Futures available: ${balance['futures']['available']}")
        """
        result: dict[str, dict[str, float]] = {}

        if account_type in ["all", "stock"]:
            try:
                stock_balance = self.api.account_balance()
                result["stock"] = {
                    "available": stock_balance.acc_balance,
                    "buying_power": stock_balance.available_balance,
                    "stock_value": stock_balance.stock_value,
                    "total": stock_balance.total,
                }
            except Exception as e:
                result["stock"] = {"error": str(e)}

        if account_type in ["all", "futures"]:
            try:
                futures_balance = self.api.futopt_account_balance()
                result["futures"] = {
                    "available": futures_balance.available_balance,
                    "margin_used": futures_balance.margin_used,
                    "initial_margin": futures_balance.initial_margin,
                    "maintenance_margin": futures_balance.maintenance_margin,
                }
            except Exception as e:
                result["futures"] = {"error": str(e)}

        return result

    def place_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float | None = None,
        order_type: str = "ROD",
    ) -> dict[str, Any]:
        """
        Place a trading order (requires SHIOAJI_TRADING_ENABLED=true).

        Args:
            symbol: Stock symbol
            action: "Buy" or "Sell"
            quantity: Order quantity
            price: Order price (None for market order)
            order_type: "ROD" (Rest of Day), "IOC" (Immediate or Cancel), "FOK" (Fill or Kill)

        Returns:
            Order confirmation dictionary

        Raises:
            RuntimeError: If trading is not enabled

        Example:
            >>> # Place market buy order
            >>> order = sdk.place_order("2330", "Buy", 1000)
            >>>
            >>> # Place limit sell order
            >>> order = sdk.place_order("2330", "Sell", 1000, price=500.0)
        """
        trading_enabled = (
            os.getenv("SHIOAJI_TRADING_ENABLED", "false").lower() == "true"
        )
        if not trading_enabled:
            raise RuntimeError(
                "Trading is disabled. Set SHIOAJI_TRADING_ENABLED=true to enable."
            )

        contract = self.api.Contracts.Stocks.get(symbol)
        if not contract:
            raise ValueError(f"Contract {symbol} not found")

        # This is a simplified version - actual implementation would need
        # to use Shioaji's order API properly
        return {
            "status": "pending",
            "message": "Order placement would be implemented here with proper Shioaji order API",
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "order_type": order_type,
        }

    def get_contract(self, symbol: str) -> Any | None:
        """
        Get contract object for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Shioaji contract object or None
        """
        return self.api.Contracts.Stocks.get(symbol)

    def disconnect(self) -> None:
        """Disconnect from Shioaji API."""
        if self._api:
            try:
                self.api.logout()
            except Exception:
                pass
            self._api = None

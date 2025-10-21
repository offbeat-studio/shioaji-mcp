"""
Shioaji MCP HTTP API Client Example

This example demonstrates how to use the HTTP API to interact with Shioaji MCP Server.
"""

import os
from typing import Any, Optional

import requests


class ShioajiHTTPClient:
    """HTTP client for Shioaji MCP Server."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the HTTP client.

        Args:
            base_url: Base URL of the HTTP API server (e.g., "http://localhost:8080")
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def health_check(self) -> dict[str, Any]:
        """Check server health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def list_tools(self) -> dict[str, Any]:
        """List available tools."""
        response = requests.get(
            f"{self.base_url}/api/tools/list", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def call_tool(self, tool: str, arguments: Optional[dict] = None) -> dict[str, Any]:
        """
        Execute a tool.

        Args:
            tool: Tool name
            arguments: Tool arguments (optional)

        Returns:
            API response
        """
        response = requests.post(
            f"{self.base_url}/api/tools/call",
            headers=self.headers,
            json={"tool": tool, "arguments": arguments or {}},
        )
        response.raise_for_status()
        return response.json()

    # Convenience methods for common operations
    def get_account_info(self) -> dict[str, Any]:
        """Get account information."""
        return self.call_tool("get_account_info")

    def search_contracts(
        self,
        keyword: Optional[str] = None,
        exchange: Optional[str] = None,
        category: Optional[str] = None,
    ) -> dict[str, Any]:
        """Search for trading contracts."""
        args = {}
        if keyword:
            args["keyword"] = keyword
        if exchange:
            args["exchange"] = exchange
        if category:
            args["category"] = category
        return self.call_tool("search_contracts", args)

    def get_snapshots(self, contracts: list[str]) -> dict[str, Any]:
        """Get real-time market snapshots."""
        return self.call_tool("get_snapshots", {"contracts": contracts})

    def get_kbars(
        self,
        contract: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get historical K-bar data."""
        args = {"contract": contract}
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        if timeframe:
            args["timeframe"] = timeframe
        return self.call_tool("get_kbars", args)

    def get_positions(self, account_type: str = "all") -> dict[str, Any]:
        """Get current positions."""
        return self.call_tool("get_positions", {"account_type": account_type})

    def get_account_balance(self, account_type: str = "all") -> dict[str, Any]:
        """Get account balance."""
        return self.call_tool("get_account_balance", {"account_type": account_type})

    def list_orders(self) -> dict[str, Any]:
        """List all orders."""
        return self.call_tool("list_orders")

    def place_order(
        self,
        contract: str,
        action: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Place a trading order.

        Args:
            contract: Contract code
            action: "Buy" or "Sell"
            quantity: Order quantity
            price: Order price (optional for market orders)
            order_type: Order type (ROD, IOC, FOK)
        """
        args = {"contract": contract, "action": action, "quantity": quantity}
        if price is not None:
            args["price"] = price
        if order_type:
            args["order_type"] = order_type
        return self.call_tool("place_order", args)

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        """Cancel an existing order."""
        return self.call_tool("cancel_order", {"order_id": order_id})

    def check_terms_status(self) -> dict[str, Any]:
        """Check service terms signing status."""
        return self.call_tool("check_terms_status")

    def run_api_test(self) -> dict[str, Any]:
        """Run API test for service terms compliance."""
        return self.call_tool("run_api_test")


def main():
    """Example usage."""
    # Configuration from environment variables
    base_url = os.getenv("SHIOAJI_HTTP_URL", "http://localhost:8080")
    api_key = os.getenv("HTTP_API_KEY")

    if not api_key:
        print("Error: HTTP_API_KEY environment variable is required")
        print("Usage: export HTTP_API_KEY=your_api_key")
        return

    # Create client
    client = ShioajiHTTPClient(base_url=base_url, api_key=api_key)

    print("=== Shioaji MCP HTTP Client Demo ===\n")

    # 1. Health check
    print("1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Connected: {health['connected']}")
    print(f"   Version: {health['version']}\n")

    # 2. List available tools
    print("2. Available Tools:")
    tools = client.list_tools()
    if tools["success"]:
        for tool in tools["tools"]:
            print(f"   - {tool['name']}: {tool['description']}")
    print()

    # 3. Get account info
    print("3. Account Information:")
    try:
        account_info = client.get_account_info()
        if account_info["success"]:
            for account in account_info["data"]:
                print(f"   Account ID: {account['account_id']}")
                print(f"   Type: {account['account_type_parsed']}")
                print(f"   Signed: {account['signed']}")
        else:
            print(f"   Error: {account_info['error']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

    # 4. Search contracts
    print("4. Search Contracts (台積電):")
    try:
        contracts = client.search_contracts(keyword="台積電")
        if contracts["success"] and contracts["data"]:
            for contract in contracts["data"][:3]:  # Show first 3 results
                print(f"   - {contract.get('code', 'N/A')}: {contract.get('name', 'N/A')}")
        else:
            print(f"   Error: {contracts.get('error', 'No results')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

    # 5. Get snapshots
    print("5. Market Snapshots (2330, 2317):")
    try:
        snapshots = client.get_snapshots(contracts=["2330", "2317"])
        if snapshots["success"] and snapshots["data"]:
            for snapshot in snapshots["data"]:
                print(
                    f"   - {snapshot.get('code', 'N/A')}: "
                    f"Close=${snapshot.get('close', 'N/A')}"
                )
        else:
            print(f"   Error: {snapshots.get('error', 'No data')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

    # 6. Get positions
    print("6. Current Positions:")
    try:
        positions = client.get_positions(account_type="all")
        if positions["success"]:
            if positions["data"]:
                print(f"   Found {len(positions['data'])} position(s)")
            else:
                print("   No positions")
        else:
            print(f"   Error: {positions['error']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()

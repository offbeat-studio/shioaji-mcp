"""Basic usage example for Shioaji MCP Server."""

import asyncio
import json

from shioaji_mcp.server import handle_call_tool, handle_list_tools


async def main():
    """Demonstrate basic Shioaji MCP server usage."""
    print("=== Shioaji MCP Server Demo ===\n")

    # List available tools
    print("1. Available Tools:")
    tools = await handle_list_tools()
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    print()

    # Login example
    print("2. Login Example:")
    login_result = await handle_call_tool(
        "shioaji_login",
        {
            "api_key": "demo_key",
            "secret_key": "demo_secret",
            "person_id": "demo_person",
            "password": "demo_password",
        },
    )
    print(f"   Result: {login_result[0]['text']}")
    print()

    # Get account info
    print("3. Account Info:")
    account_result = await handle_call_tool("get_account_info", {})
    print(f"   Result: {account_result[0]['text']}")
    print()

    # Search contracts
    print("4. Search Contracts:")
    search_result = await handle_call_tool(
        "search_contracts", {"keyword": "台積電"}
    )
    print(f"   Result: {search_result[0]['text']}")
    print()

    # Get market snapshots
    print("5. Market Snapshots:")
    snapshot_result = await handle_call_tool(
        "get_snapshots", {"contracts": ["2330", "2317"]}
    )
    print(f"   Result: {snapshot_result[0]['text']}")
    print()

    # Place order
    print("6. Place Order:")
    order_result = await handle_call_tool(
        "place_order",
        {
            "contract": "2330",
            "action": "Buy",
            "quantity": 1000,
            "price": 500.0,
        },
    )
    print(f"   Result: {order_result[0]['text']}")
    print()

    # Get positions
    print("7. Get Positions:")
    position_result = await handle_call_tool("get_positions", {})
    print(f"   Result: {position_result[0]['text']}")
    print()

    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
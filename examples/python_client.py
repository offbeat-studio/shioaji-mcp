#!/usr/bin/env python3
"""
Example Python client for Shioaji MCP server.

This script demonstrates how to connect to and use the Shioaji MCP server
from Python.

Requirements:
- Python 3.10+
- mcp-client package: pip install mcp-client

Usage:
1. Set your API credentials as environment variables:
   export SHIOAJI_API_KEY=your_api_key
   export SHIOAJI_SECRET_KEY=your_secret_key

2. Run the script:
   python python_client.py
"""

import asyncio
import json
import os
import sys

try:
    from mcp_client import McpClient
except ImportError:
    print("Error: mcp-client package not found.")
    print("Please install it with: pip install mcp-client")
    sys.exit(1)


async def main():
    # Configuration for the MCP server
    api_key = os.environ.get('SHIOAJI_API_KEY', '')
    secret_key = os.environ.get('SHIOAJI_SECRET_KEY', '')

    mcp_config = {
        "mcpServers": {
            "shioaji": {
                "command": "docker",
                "args": [
                    "run", "--rm", "-i", "--platform=linux/amd64",
                    "-e", f"SHIOAJI_API_KEY={api_key}",
                    "-e", f"SHIOAJI_SECRET_KEY={secret_key}",
                    "ghcr.io/musingfox/shioaji-mcp:latest"
                ]
            }
        }
    }

    # Check if API credentials are set
    if not api_key or not secret_key:
        print("Error: SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment "
              "variables must be set.")
        print("Please set them with:")
        print("  export SHIOAJI_API_KEY=your_api_key")
        print("  export SHIOAJI_SECRET_KEY=your_secret_key")
        sys.exit(1)

    # Create MCP client
    client = McpClient(mcp_config)

    try:
        # Connect to the MCP server
        print("Connecting to Shioaji MCP server...")
        await client.connect()
        print("Connected successfully!")

        # Get account information
        print("\n--- Account Information ---")
        account_info = await client.use_tool("shioaji", "get_account_info", {})
        print(json.dumps(account_info, indent=2))

        # Search for TSMC (Taiwan Semiconductor) contract
        print("\n--- Searching for TSMC Contract ---")
        contracts = await client.use_tool("shioaji", "search_contracts", {
            "keyword": "2330"  # TSMC stock code
        })
        print(json.dumps(contracts, indent=2))

        if contracts and len(contracts) > 0:
            # Get real-time snapshot for TSMC
            print("\n--- Getting Real-time Snapshot for TSMC ---")
            tsmc_code = contracts[0]["code"]
            snapshots = await client.use_tool("shioaji", "get_snapshots", {
                "contracts": [tsmc_code]
            })
            print(json.dumps(snapshots, indent=2))

            # Get historical K-bar data for TSMC
            print("\n--- Getting Historical K-bar Data for TSMC ---")
            kbars = await client.use_tool("shioaji", "get_kbars", {
                "contract": tsmc_code,
                "timeframe": "1D",  # Daily K-bars
                "start_date": "2023-01-01",
                "end_date": "2023-01-31"
            })
            print(f"Retrieved {len(kbars)} K-bars")
            print(json.dumps(kbars[:3], indent=2))  # Show first 3 K-bars

        # Get current positions
        print("\n--- Current Positions ---")
        positions = await client.use_tool("shioaji", "get_positions", {})
        print(json.dumps(positions, indent=2))

        # Get account balance
        print("\n--- Account Balance ---")
        balance = await client.use_tool("shioaji", "get_account_balance", {})
        print(json.dumps(balance, indent=2))

        print("\nAll operations completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from the MCP server
        await client.disconnect()
        print("Disconnected from Shioaji MCP server")


if __name__ == "__main__":
    asyncio.run(main())

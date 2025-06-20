#!/usr/bin/env python3
"""
Example of using Shioaji MCP with real API credentials.

Before running this example:
1. Copy .env.example to .env
2. Fill in your real Shioaji API credentials
3. Make sure you have shioaji installed: pip install shioaji[speed]
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_real_shioaji():
    """Test real Shioaji functionality."""
    
    # Check if credentials are set
    api_key = os.getenv("SHIOAJI_API_KEY")
    secret_key = os.getenv("SHIOAJI_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY in your .env file")
        return
    
    print("🚀 Testing real Shioaji MCP server...")
    
    # Import after checking credentials
    from shioaji_mcp.utils.auth import auth_manager
    from shioaji_mcp.tools.contracts import search_contracts
    from shioaji_mcp.tools.market_data import get_snapshots
    from shioaji_mcp.tools.positions import get_account_balance
    
    try:
        # Test connection
        print("📡 Testing connection...")
        if auth_manager.is_connected():
            print("✅ Successfully connected to Shioaji API")
        else:
            print("❌ Failed to connect to Shioaji API")
            return
        
        # Test account info
        print("\\n👤 Getting account information...")
        balance_result = await get_account_balance({})
        print(f"Account balance: {json.dumps(balance_result, indent=2, ensure_ascii=False)}")
        
        # Test contract search
        print("\\n🔍 Searching for contracts...")
        search_result = await search_contracts({"keyword": "台積電"})
        print(f"Search results: {json.dumps(search_result, indent=2, ensure_ascii=False)}")
        
        # Test market data
        print("\\n📊 Getting market snapshots...")
        snapshot_result = await get_snapshots({"contracts": ["2330", "2317"]})
        print(f"Snapshots: {json.dumps(snapshot_result, indent=2, ensure_ascii=False)}")
        
        print("\\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        # Cleanup
        try:
            await auth_manager.logout()
            print("\\n👋 Logged out successfully")
        except Exception as e:
            print(f"Warning: Logout error: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_shioaji())
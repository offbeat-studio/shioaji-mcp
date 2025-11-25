#!/usr/bin/env python3
"""
Simple example using Shioaji SDK directly without MCP.

This demonstrates how to use the simplified SDK for common tasks.

Requirements:
- Python 3.10+
- shioaji-mcp package installed

Setup:
1. Set environment variables:
   export SHIOAJI_API_KEY=your_api_key
   export SHIOAJI_SECRET_KEY=your_secret_key

2. Run:
   python sdk_example.py
"""

from shioaji_mcp.sdk import ShioajiSDK


def main():
    """Main example function."""
    print("=" * 60)
    print("Shioaji SDK Example")
    print("=" * 60)

    # Initialize SDK (uses environment variables)
    sdk = ShioajiSDK()
    print("\n✅ Connected to Shioaji")

    # Example 1: Get accounts
    print("\n" + "=" * 60)
    print("📋 Your Accounts")
    print("=" * 60)
    accounts = sdk.get_accounts()
    for acc in accounts:
        print(f"  • {acc['account_id']} ({acc['account_type']})")
        print(f"    Signed: {'✅ Yes' if acc['signed'] else '❌ No'}")

    # Example 2: Search for stocks
    print("\n" + "=" * 60)
    print("🔍 Search Example: 台積電")
    print("=" * 60)
    results = sdk.search_stocks("台積電", limit=3)
    for stock in results:
        print(f"  • {stock['code']}: {stock['name']} ({stock['exchange']})")

    # Example 3: Get real-time quote
    print("\n" + "=" * 60)
    print("📊 Real-time Quote: TSMC (2330)")
    print("=" * 60)
    try:
        quote = sdk.get_quote("2330")
        print(f"  Company: {quote['name']}")
        print(f"  Price: ${quote['close']:,.2f}")
        print(f"  Change: {quote['close'] - quote['open']:+,.2f} "
              f"({(quote['close'] - quote['open']) / quote['open'] * 100:+.2f}%)")
        print(f"  Volume: {quote['volume']:,}")
        print(f"  High: ${quote['high']:,.2f}")
        print(f"  Low: ${quote['low']:,.2f}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Example 4: Get multiple quotes
    print("\n" + "=" * 60)
    print("📊 Multiple Quotes")
    print("=" * 60)
    symbols = ["2330", "2317", "2454"]  # TSMC, Hon Hai, MediaTek
    try:
        quotes = sdk.get_quotes(symbols)
        for quote in quotes:
            change_pct = (quote['close'] - quote['open']) / quote['open'] * 100
            print(f"  • {quote['code']} {quote['name']}: "
                  f"${quote['close']:,.2f} ({change_pct:+.2f}%)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Example 5: Get historical data
    print("\n" + "=" * 60)
    print("📈 Historical Data: TSMC (Last 5 days)")
    print("=" * 60)
    try:
        history = sdk.get_history("2330", days=5)
        if history:
            print(f"  {'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
            print("  " + "-" * 66)
            for bar in history[-5:]:  # Last 5 bars
                date = bar['date'].split()[0]  # Just the date part
                print(f"  {date:<12} "
                      f"{bar['open']:>10,.2f} "
                      f"{bar['high']:>10,.2f} "
                      f"{bar['low']:>10,.2f} "
                      f"{bar['close']:>10,.2f} "
                      f"{bar['volume']:>12,}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Example 6: Get positions
    print("\n" + "=" * 60)
    print("💼 Your Positions")
    print("=" * 60)
    try:
        positions = sdk.get_positions()

        if positions.get('stock'):
            print("  📈 Stock Positions:")
            for pos in positions['stock']:
                print(f"    • {pos['code']}: {pos['quantity']:,} shares @ ${pos['price']:.2f}")
                if pos['pnl'] != 0:
                    print(f"      P&L: {pos['pnl']:+,.2f}")
        else:
            print("  📈 No stock positions")

        if positions.get('futures'):
            print("\n  📊 Futures Positions:")
            for pos in positions['futures']:
                print(f"    • {pos['code']}: {pos['quantity']:,} contracts @ ${pos['price']:.2f}")
                if pos['pnl'] != 0:
                    print(f"      P&L: {pos['pnl']:+,.2f}")
        else:
            print("\n  📊 No futures positions")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Example 7: Get account balance
    print("\n" + "=" * 60)
    print("💰 Account Balance")
    print("=" * 60)
    try:
        balance = sdk.get_balance()

        if 'stock' in balance and 'error' not in balance['stock']:
            stock_bal = balance['stock']
            print("  📈 Stock Account:")
            print(f"    Available: ${stock_bal['available']:,.2f}")
            print(f"    Buying Power: ${stock_bal['buying_power']:,.2f}")
            print(f"    Stock Value: ${stock_bal['stock_value']:,.2f}")
            print(f"    Total: ${stock_bal['total']:,.2f}")

        if 'futures' in balance and 'error' not in balance['futures']:
            fut_bal = balance['futures']
            print("\n  📊 Futures Account:")
            print(f"    Available: ${fut_bal['available']:,.2f}")
            print(f"    Margin Used: ${fut_bal['margin_used']:,.2f}")
            print(f"    Initial Margin: ${fut_bal['initial_margin']:,.2f}")
            print(f"    Maintenance Margin: ${fut_bal['maintenance_margin']:,.2f}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✨ All examples completed!")
    print("=" * 60)

    # Clean disconnect
    sdk.disconnect()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

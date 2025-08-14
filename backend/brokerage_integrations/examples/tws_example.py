#!/usr/bin/env python3
"""
IBKR TWS API Integration Example

This script demonstrates how to use the IBKR TWS API integration
to connect to TWS/Gateway and retrieve account data.

Prerequisites:
1. Install ibapi: pip install ibapi==10.19.2
2. Install TWS or Gateway from Interactive Brokers
3. Configure TWS/Gateway to allow API connections
4. Start TWS/Gateway and log in

Usage:
    python tws_example.py
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path to import the service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ibkr_tws_service import IBKRTWSService


def main():
    """Main function demonstrating TWS API usage"""
    
    print("=" * 60)
    print("IBKR TWS API Integration Example")
    print("=" * 60)
    
    # Create TWS service instance
    print("\n1. Creating TWS service instance...")
    try:
        tws_service = IBKRTWSService(
            host="127.0.0.1",
            port=7497,  # Use 4001 for Gateway
            client_id=1,
            timeout=20
        )
        print("✓ TWS service instance created")
    except ImportError as e:
        print(f"✗ Error: {e}")
        print("Please install ibapi: pip install ibapi==10.19.2")
        return
    except Exception as e:
        print(f"✗ Error creating service: {e}")
        return
    
    # Connect to TWS/Gateway
    print("\n2. Connecting to TWS/Gateway...")
    if not tws_service.authenticate():
        print("✗ Failed to connect to TWS/Gateway")
        print("\nTroubleshooting:")
        print("- Ensure TWS or Gateway is running")
        print("- Check if API connections are enabled in TWS settings")
        print("- Verify port number (7497 for TWS, 4001 for Gateway)")
        print("- Make sure you're logged into TWS/Gateway")
        return
    
    print("✓ Successfully connected to TWS/Gateway")
    
    try:
        # Get account information
        print("\n3. Getting account information...")
        account_info = tws_service.get_account_info()
        if account_info['success']:
            print("✓ Account information retrieved:")
            for key, value in account_info['data'].items():
                print(f"  {key}: {value}")
        else:
            print(f"✗ Error getting account info: {account_info['error']}")
        
        # Get account balance
        print("\n4. Getting account balance...")
        balance = tws_service.get_balance()
        if balance['success']:
            print("✓ Account balance retrieved:")
            for key, value in balance['data'].items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: ${value:,.2f}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"✗ Error getting balance: {balance['error']}")
        
        # Get portfolio positions
        print("\n5. Getting portfolio positions...")
        positions = tws_service.get_portfolio()
        if positions:
            print(f"✓ Found {len(positions)} positions:")
            for i, position in enumerate(positions, 1):
                print(f"\n  Position {i}:")
                for key, value in position.items():
                    if isinstance(value, (int, float)) and key in ['average_price', 'market_value', 'unrealized_pnl']:
                        print(f"    {key}: ${value:,.2f}")
                    else:
                        print(f"    {key}: {value}")
        else:
            print("✓ No positions found in portfolio")
        
        # Get market data for a sample symbol
        print("\n6. Getting market data for AAPL...")
        market_data = tws_service.get_market_data("AAPL")
        if market_data['success']:
            print("✓ Market data retrieved:")
            for key, value in market_data['data'].items():
                if isinstance(value, (int, float)) and key in ['bid', 'ask', 'last', 'high', 'low']:
                    print(f"  {key}: ${value:,.2f}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"✗ Error getting market data: {market_data['error']}")
        
        # Get open orders
        print("\n7. Getting open orders...")
        open_orders = tws_service.get_open_orders()
        if open_orders:
            print(f"✓ Found {len(open_orders)} open orders:")
            for i, order in enumerate(open_orders, 1):
                print(f"\n  Order {i}:")
                for key, value in order.items():
                    if isinstance(value, (int, float)) and key in ['quantity', 'limit_price', 'stop_price']:
                        print(f"    {key}: {value:,.2f}")
                    else:
                        print(f"    {key}: {value}")
        else:
            print("✓ No open orders found")
        
        # Demonstrate order placement (commented out for safety)
        print("\n8. Order placement demonstration (commented out for safety)")
        print("To place orders, uncomment the code below:")
        
        """
        # Example: Place a market buy order for 1 share of AAPL
        print("Placing market buy order for 1 AAPL...")
        order_result = tws_service.place_order(
            symbol="AAPL",
            action="BUY",
            quantity=1,
            order_type="MKT"
        )
        
        if order_result['success']:
            print(f"✓ Order placed successfully:")
            print(f"  Order ID: {order_result['data']['order_id']}")
            print(f"  Status: {order_result['data']['status']}")
        else:
            print(f"✗ Order placement failed: {order_result['error']}")
        """
        
        # Portfolio analysis
        print("\n9. Portfolio analysis...")
        if positions:
            total_value = 0
            total_pnl = 0
            position_count = len(positions)
            
            for position in positions:
                if position['market_value']:
                    total_value += float(position['market_value'])
                if position['unrealized_pnl']:
                    total_pnl += float(position['unrealized_pnl'])
            
            print("✓ Portfolio summary:")
            print(f"  Total positions: {position_count}")
            print(f"  Total market value: ${total_value:,.2f}")
            print(f"  Total unrealized P&L: ${total_pnl:,.2f}")
            
            if total_value > 0:
                pnl_percentage = (total_pnl / total_value) * 100
                print(f"  P&L percentage: {pnl_percentage:,.2f}%")
        else:
            print("✓ No positions to analyze")
        
    except Exception as e:
        print(f"✗ Error during data retrieval: {e}")
    
    finally:
        # Always disconnect
        print("\n10. Disconnecting from TWS/Gateway...")
        tws_service.disconnect()
        print("✓ Disconnected from TWS/Gateway")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


def demo_market_data():
    """Demonstrate getting market data for multiple symbols"""
    
    print("\n" + "=" * 60)
    print("Market Data Demo")
    print("=" * 60)
    
    try:
        tws_service = IBKRTWSService()
        
        if not tws_service.authenticate():
            print("✗ Failed to connect to TWS/Gateway")
            return
        
        # List of popular symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
        
        print(f"\nGetting market data for {len(symbols)} symbols...")
        print("-" * 40)
        
        for symbol in symbols:
            try:
                market_data = tws_service.get_market_data(symbol)
                if market_data['success']:
                    data = market_data['data']
                    print(f"{symbol:6} | ${data.get('last', 0):8.2f} | "
                          f"Bid: ${data.get('bid', 0):8.2f} | "
                          f"Ask: ${data.get('ask', 0):8.2f} | "
                          f"Vol: {data.get('volume', 0):,}")
                else:
                    print(f"{symbol:6} | Error: {market_data['error']}")
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"{symbol:6} | Error: {e}")
        
        tws_service.disconnect()
        
    except Exception as e:
        print(f"✗ Error in market data demo: {e}")


def demo_order_management():
    """Demonstrate order management (read-only)"""
    
    print("\n" + "=" * 60)
    print("Order Management Demo (Read-Only)")
    print("=" * 60)
    
    try:
        tws_service = IBKRTWSService()
        
        if not tws_service.authenticate():
            print("✗ Failed to connect to TWS/Gateway")
            return
        
        # Get open orders
        print("\n1. Current open orders:")
        open_orders = tws_service.get_open_orders()
        
        if open_orders:
            for i, order in enumerate(open_orders, 1):
                print(f"\n  Order {i}:")
                print(f"    ID: {order['order_id']}")
                print(f"    Symbol: {order['symbol']}")
                print(f"    Action: {order['action']}")
                print(f"    Quantity: {order['quantity']}")
                print(f"    Type: {order['order_type']}")
                print(f"    Status: {order['status']}")
                
                if order['limit_price']:
                    print(f"    Limit Price: ${order['limit_price']:,.2f}")
                if order['stop_price']:
                    print(f"    Stop Price: ${order['stop_price']:,.2f}")
        else:
            print("  No open orders found")
        
        # Demonstrate order cancellation (commented out for safety)
        print("\n2. Order cancellation demonstration:")
        print("To cancel orders, uncomment the code below:")
        
        """
        if open_orders:
            # Cancel the first open order
            first_order = open_orders[0]
            cancel_result = tws_service.cancel_order(first_order['order_id'])
            
            if cancel_result['success']:
                print(f"✓ Order {first_order['order_id']} cancellation requested")
            else:
                print(f"✗ Cancellation failed: {cancel_result['error']}")
        """
        
        tws_service.disconnect()
        
    except Exception as e:
        print(f"✗ Error in order management demo: {e}")


if __name__ == "__main__":
    # Run main example
    main()
    
    # Uncomment the lines below to run additional demos
    # demo_market_data()
    # demo_order_management()
    
    print("\nTo run additional demos, uncomment the demo calls at the bottom of the script.")

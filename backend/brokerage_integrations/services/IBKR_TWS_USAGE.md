# IBKR TWS API Integration Usage Guide

## Overview

The IBKR TWS API integration provides direct access to Interactive Brokers' Trader Workstation (TWS) or Gateway through the official `ibapi` Python package. This allows for real-time market data, account information, portfolio management, and order execution.

## Prerequisites

### 1. Install Dependencies

```bash
pip install ibapi==10.19.2
```

### 2. TWS/Gateway Setup

1. **Download and Install TWS or Gateway:**
   - TWS: https://www.interactivebrokers.com/en/trading/tws.php
   - Gateway: https://www.interactivebrokers.com/en/trading/ib-api.php

2. **Configure TWS/Gateway:**
   - Enable API connections in TWS: Edit → Global Configuration → API → Settings
   - Set Socket port: 7497 (TWS) or 4001 (Gateway)
   - Enable "Allow connections from localhost"
   - Set "Read-Only API" if you only need data access

3. **Start TWS/Gateway:**
   - Launch TWS or Gateway
   - Log in with your IBKR credentials
   - Ensure the application is running and connected

## Basic Usage

### 1. Create TWS Service Instance

```python
from brokerage_integrations.services.ibkr_tws_service import IBKRTWSService

# Basic connection (defaults to localhost:7497)
tws_service = IBKRTWSService()

# Custom connection settings
tws_service = IBKRTWSService(
    host="127.0.0.1",
    port=7497,  # 7497 for TWS, 4001 for Gateway
    client_id=1,
    timeout=20
)
```

### 2. Connect and Authenticate

```python
# Connect to TWS/Gateway
if tws_service.authenticate():
    print("Successfully connected to TWS/Gateway")
else:
    print("Failed to connect to TWS/Gateway")
```

### 3. Get Account Information

```python
# Get basic account info
account_info = tws_service.get_account_info()
if account_info['success']:
    print(f"Account ID: {account_info['data']['account_id']}")
    print(f"Account Type: {account_info['data']['account_type']}")
    print(f"Currency: {account_info['data']['currency']}")
else:
    print(f"Error: {account_info['error']}")
```

### 4. Get Account Balance

```python
# Get account balance
balance = tws_service.get_balance()
if balance['success']:
    print(f"Cash Balance: ${balance['data']['cash_balance']}")
    print(f"Total Value: ${balance['data']['total_value']}")
    print(f"Buying Power: ${balance['data']['buying_power']}")
    print(f"Available Funds: ${balance['data']['available_funds']}")
else:
    print(f"Error: {balance['error']}")
```

### 5. Get Portfolio Positions

```python
# Get current portfolio positions
positions = tws_service.get_portfolio()
for position in positions:
    print(f"Symbol: {position['symbol']}")
    print(f"Quantity: {position['quantity']}")
    print(f"Average Price: ${position['average_price']}")
    print(f"Market Value: ${position['market_value']}")
    print(f"Unrealized P&L: ${position['unrealized_pnl']}")
    print("---")
```

### 6. Get Market Data

```python
# Get real-time market data for a symbol
market_data = tws_service.get_market_data("AAPL")
if market_data['success']:
    print(f"Symbol: {market_data['data']['symbol']}")
    print(f"Bid: ${market_data['data']['bid']}")
    print(f"Ask: ${market_data['data']['ask']}")
    print(f"Last: ${market_data['data']['last']}")
    print(f"Volume: {market_data['data']['volume']}")
else:
    print(f"Error: {market_data['error']}")
```

### 7. Place Orders

```python
# Place a market buy order
order_result = tws_service.place_order(
    symbol="AAPL",
    action="BUY",
    quantity=10,
    order_type="MKT"
)

if order_result['success']:
    print(f"Order ID: {order_result['data']['order_id']}")
    print(f"Status: {order_result['data']['status']}")
else:
    print(f"Error: {order_result['error']}")

# Place a limit order
limit_order = tws_service.place_order(
    symbol="AAPL",
    action="SELL",
    quantity=5,
    order_type="LMT",
    limit_price=150.00
)
```

### 8. Get Open Orders

```python
# Get all open orders
open_orders = tws_service.get_open_orders()
for order in open_orders:
    print(f"Order ID: {order['order_id']}")
    print(f"Symbol: {order['symbol']}")
    print(f"Action: {order['action']}")
    print(f"Quantity: {order['quantity']}")
    print(f"Order Type: {order['order_type']}")
    print(f"Status: {order['status']}")
    print("---")
```

### 9. Cancel Orders

```python
# Cancel an order by ID
cancel_result = tws_service.cancel_order(order_id=12345)
if cancel_result['success']:
    print(f"Order {cancel_result['data']['order_id']} cancellation requested")
else:
    print(f"Error: {cancel_result['error']}")
```

### 10. Disconnect

```python
# Always disconnect when done
tws_service.disconnect()
```

## Advanced Usage

### 1. Multiple Symbols Market Data

```python
# Get market data for multiple symbols
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
for symbol in symbols:
    market_data = tws_service.get_market_data(symbol)
    if market_data['success']:
        print(f"{symbol}: ${market_data['data']['last']}")
    time.sleep(0.1)  # Rate limiting
```

### 2. Portfolio Analysis

```python
# Get portfolio and calculate total value
positions = tws_service.get_portfolio()
total_value = 0
total_pnl = 0

for position in positions:
    if position['market_value']:
        total_value += float(position['market_value'])
    if position['unrealized_pnl']:
        total_pnl += float(position['unrealized_pnl'])

print(f"Total Portfolio Value: ${total_value:,.2f}")
print(f"Total Unrealized P&L: ${total_pnl:,.2f}")
```

### 3. Order Management System

```python
class OrderManager:
    def __init__(self, tws_service):
        self.tws_service = tws_service
    
    def place_stop_loss(self, symbol, quantity, stop_price):
        """Place a stop loss order"""
        return self.tws_service.place_order(
            symbol=symbol,
            action="SELL",
            quantity=quantity,
            order_type="STP",
            stop_price=stop_price
        )
    
    def place_trailing_stop(self, symbol, quantity, trail_percent):
        """Place a trailing stop order"""
        # Get current market price
        market_data = self.tws_service.get_market_data(symbol)
        if market_data['success']:
            current_price = market_data['data']['last']
            stop_price = current_price * (1 - trail_percent / 100)
            
            return self.tws_service.place_order(
                symbol=symbol,
                action="SELL",
                quantity=quantity,
                order_type="TRAIL",
                stop_price=stop_price
            )
        return None

# Usage
order_manager = OrderManager(tws_service)
stop_loss = order_manager.place_stop_loss("AAPL", 10, 140.00)
trailing_stop = order_manager.place_trailing_stop("GOOGL", 5, 5.0)  # 5% trailing stop
```

## Error Handling

### 1. Connection Errors

```python
try:
    tws_service = IBKRTWSService()
    if not tws_service.authenticate():
        print("Failed to connect. Check if TWS/Gateway is running.")
        print("Common issues:")
        print("- TWS/Gateway not started")
        print("- Wrong port number")
        print("- API connections disabled")
        print("- Firewall blocking connection")
except ImportError:
    print("IBKR TWS API not available. Install with: pip install ibapi")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 2. API Errors

```python
# Handle specific TWS API errors
def handle_tws_error(error_code, error_message):
    error_handlers = {
        502: "Couldn't connect to TWS/Gateway",
        504: "Not connected to TWS/Gateway",
        1100: "Connectivity between IB and TWS lost",
        1101: "Connectivity between IB and TWS restored",
        1102: "Connectivity between IB and TWS restored",
        2104: "Market data farm connection is OK",
        2106: "A historical data farm is connected",
        2158: "Sec-def data farm connection is OK"
    }
    
    if error_code in error_handlers:
        print(f"TWS Error {error_code}: {error_handlers[error_code]}")
    else:
        print(f"TWS Error {error_code}: {error_message}")
```

## Best Practices

### 1. Connection Management

```python
class TWSSession:
    def __init__(self, host="127.0.0.1", port=7497):
        self.tws_service = IBKRTWSService(host=host, port=port)
    
    def __enter__(self):
        if not self.tws_service.authenticate():
            raise ConnectionError("Failed to connect to TWS/Gateway")
        return self.tws_service
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tws_service.disconnect()

# Usage with context manager
with TWSSession() as tws:
    account_info = tws.get_account_info()
    balance = tws.get_balance()
    # Connection automatically closed when exiting context
```

### 2. Rate Limiting

```python
import time

def get_multiple_market_data(tws_service, symbols, delay=0.1):
    """Get market data for multiple symbols with rate limiting"""
    results = {}
    for symbol in symbols:
        try:
            market_data = tws_service.get_market_data(symbol)
            results[symbol] = market_data
            time.sleep(delay)  # Rate limiting
        except Exception as e:
            results[symbol] = {'success': False, 'error': str(e)}
    return results
```

### 3. Data Validation

```python
def validate_order_params(symbol, action, quantity, order_type, **kwargs):
    """Validate order parameters before placing"""
    errors = []
    
    if not symbol or not symbol.strip():
        errors.append("Symbol is required")
    
    if action not in ["BUY", "SELL"]:
        errors.append("Action must be BUY or SELL")
    
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        errors.append("Quantity must be a positive number")
    
    if order_type not in ["MKT", "LMT", "STP", "STP LMT", "TRAIL"]:
        errors.append("Invalid order type")
    
    if order_type in ["LMT", "STP LMT"] and "limit_price" not in kwargs:
        errors.append("Limit price required for limit orders")
    
    if order_type in ["STP", "STP LMT"] and "stop_price" not in kwargs:
        errors.append("Stop price required for stop orders")
    
    return errors

# Usage
errors = validate_order_params("AAPL", "BUY", 10, "LMT", limit_price=150.00)
if errors:
    print("Order validation errors:", errors)
else:
    order_result = tws_service.place_order("AAPL", "BUY", 10, "LMT", limit_price=150.00)
```

## Troubleshooting

### Common Issues

1. **Connection Failed (Error 502)**
   - Ensure TWS/Gateway is running
   - Check port number (7497 for TWS, 4001 for Gateway)
   - Verify API connections are enabled in TWS settings

2. **Not Connected (Error 504)**
   - TWS/Gateway may have disconnected
   - Try reconnecting with `tws_service.authenticate()`

3. **Market Data Not Available**
   - Check market hours
   - Verify symbol is valid
   - Ensure market data subscriptions are active

4. **Order Rejected**
   - Check account permissions
   - Verify sufficient buying power
   - Ensure symbol is tradeable

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ibapi')
logger.setLevel(logging.DEBUG)

# Create service with debug info
tws_service = IBKRTWSService()
tws_service.authenticate()
```

## Integration with Django

### 1. Django View Example

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from brokerage_integrations.services.ibkr_tws_service import IBKRTWSService

@csrf_exempt
def get_tws_account_info(request):
    """Django view to get TWS account information"""
    try:
        tws_service = IBKRTWSService()
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            })
        
        account_info = tws_service.get_account_info()
        balance = tws_service.get_balance()
        positions = tws_service.get_portfolio()
        
        tws_service.disconnect()
        
        return JsonResponse({
            'success': True,
            'account_info': account_info,
            'balance': balance,
            'positions': positions
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
```

### 2. Django Management Command

```python
# management/commands/tws_sync.py
from django.core.management.base import BaseCommand
from brokerage_integrations.services.ibkr_tws_service import IBKRTWSService

class Command(BaseCommand):
    help = 'Sync account data from IBKR TWS'

    def handle(self, *args, **options):
        try:
            tws_service = IBKRTWSService()
            
            if not tws_service.authenticate():
                self.stdout.write(
                    self.style.ERROR('Failed to connect to TWS/Gateway')
                )
                return
            
            # Get account data
            account_info = tws_service.get_account_info()
            balance = tws_service.get_balance()
            positions = tws_service.get_portfolio()
            
            # Process and store data
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced data for account: {account_info["data"]["account_id"]}')
            )
            
            tws_service.disconnect()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing TWS data: {e}')
            )
```

## Security Considerations

1. **Local Connection Only**: TWS API only works with local connections
2. **Read-Only Mode**: Use read-only API mode for data access only
3. **Firewall**: Ensure proper firewall configuration
4. **Credentials**: Never store TWS credentials in code
5. **Rate Limiting**: Implement proper rate limiting to avoid API restrictions

## Performance Tips

1. **Connection Pooling**: Reuse connections when possible
2. **Batch Requests**: Group related requests together
3. **Caching**: Cache market data and account info
4. **Async Processing**: Use async/await for non-blocking operations
5. **Error Recovery**: Implement automatic reconnection logic

---

For more information, refer to the official IBKR API documentation:
https://www.interactivebrokers.com/en/trading/ib-api.php

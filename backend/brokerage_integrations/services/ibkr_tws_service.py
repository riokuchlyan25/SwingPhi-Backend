import logging
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService
import os

# Import IBKR TWS API
try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
    from ibapi.common import *
    from ibapi.utils import *
    from ibapi import TickTypeEnum
    TWS_AVAILABLE = True
except ImportError:
    TWS_AVAILABLE = False
    logging.warning("IBKR TWS API (ibapi) not available. Install with: pip install ibapi")

logger = logging.getLogger(__name__)


class IBKRTWSService(BaseBrokerageService):
    """Interactive Brokers TWS API integration using ibapi"""
    
    def __init__(self, account_id: str = None, host: str = "127.0.0.1", port: int = 7497, 
                 client_id: int = 1, timeout: int = 20):
        super().__init__(account_id or "")
        
        if not TWS_AVAILABLE:
            raise ImportError("IBKR TWS API (ibapi) is required. Install with: pip install ibapi")
        
        self.host = host
        self.port = port  # 7497 for TWS, 4001 for Gateway
        self.client_id = client_id
        self.timeout = timeout
        self.client = None
        self.connected = False
        self._lock = threading.Lock()
        
        # Data storage for async responses
        self.account_data = {}
        self.positions = []
        self.transactions = []
        self.contracts = {}
        self._request_id = 0
        self._pending_requests = {}
        
    def _get_next_request_id(self) -> int:
        """Get next unique request ID"""
        with self._lock:
            self._request_id += 1
            return self._request_id
    
    def authenticate(self) -> bool:
        """Connect to TWS/Gateway"""
        try:
            if self.client and self.connected:
                return True
                
            self.client = IBKRClient(self)
            self.client.connect(self.host, self.port, self.client_id)
            
            # Start message processing thread
            self.client_thread = threading.Thread(target=self.client.run, daemon=True)
            self.client_thread.start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info(f"Connected to IBKR TWS/Gateway at {self.host}:{self.port}")
                return True
            else:
                logger.error("Failed to connect to IBKR TWS/Gateway")
                return False
                
        except Exception as e:
            logger.error(f"IBKR TWS authentication failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from TWS/Gateway"""
        if self.client:
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR TWS/Gateway")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get IBKR account information via TWS API"""
        try:
            if not self.authenticate():
                return self._format_error("Failed to connect to TWS/Gateway")
            
            # Request account information
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'account_info', 'data': {}}
            
            self.client.reqAccountUpdates(True, self.account_id or "")
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                return self._format_error("Timeout waiting for account info")
            
            account_data = self._pending_requests.get(request_id, {}).get('data', {})
            
            return self._format_response({
                'account_id': account_data.get('account_id', self.account_id),
                'account_name': account_data.get('account_name', 'IBKR Account'),
                'account_type': account_data.get('account_type', 'Individual'),
                'currency': account_data.get('currency', 'USD'),
                'trading_permissions': account_data.get('trading_permissions', []),
                'connected': self.connected
            })
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get IBKR portfolio positions via TWS API"""
        try:
            if not self.authenticate():
                return []
            
            # Request portfolio positions
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'positions', 'data': []}
            
            self.client.reqPositions()
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                logger.error("Timeout waiting for positions")
                return []
            
            positions = self._pending_requests.get(request_id, {}).get('data', [])
            
            portfolio = []
            for position in positions:
                portfolio.append({
                    'symbol': position.get('symbol'),
                    'exchange': position.get('exchange'),
                    'currency': position.get('currency'),
                    'quantity': self._parse_decimal(position.get('position')),
                    'average_price': self._parse_decimal(position.get('avgCost')),
                    'current_price': self._parse_decimal(position.get('marketPrice')),
                    'market_value': self._parse_decimal(position.get('marketValue')),
                    'unrealized_pnl': self._parse_decimal(position.get('unrealizedPnL')),
                    'contract_id': position.get('contractId'),
                    'account_id': position.get('account')
                })
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get IBKR transaction history via TWS API"""
        try:
            if not self.authenticate():
                return []
            
            # Request account summary
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'transactions', 'data': []}
            
            # Note: TWS API doesn't provide direct transaction history
            # We'll use account summary and recent activity
            self.client.reqAccountSummary(request_id, "All", 
                "NetLiquidation,BuyingPower,TotalCashValue,AvailableFunds")
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            # For transactions, we'll return a placeholder since TWS API doesn't provide
            # direct transaction history like the Client Portal API
            return []
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get IBKR account balance via TWS API"""
        try:
            if not self.authenticate():
                return self._format_error("Failed to connect to TWS/Gateway")
            
            # Request account summary
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'balance', 'data': {}}
            
            self.client.reqAccountSummary(request_id, "All", 
                "NetLiquidation,BuyingPower,TotalCashValue,AvailableFunds,GrossPositionValue")
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                return self._format_error("Timeout waiting for balance")
            
            balance_data = self._pending_requests.get(request_id, {}).get('data', {})
            
            return self._format_response({
                'cash_balance': self._parse_decimal(balance_data.get('TotalCashValue')),
                'total_value': self._parse_decimal(balance_data.get('NetLiquidation')),
                'buying_power': self._parse_decimal(balance_data.get('BuyingPower')),
                'available_funds': self._parse_decimal(balance_data.get('AvailableFunds')),
                'gross_position_value': self._parse_decimal(balance_data.get('GrossPositionValue')),
                'account_id': self.account_id
            })
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS balance: {e}")
            return self._format_error(str(e))
    
    def get_market_data(self, symbol: str, exchange: str = "SMART", currency: str = "USD") -> Dict[str, Any]:
        """Get real-time market data for a symbol"""
        try:
            if not self.authenticate():
                return self._format_error("Failed to connect to TWS/Gateway")
            
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = exchange
            contract.currency = currency
            
            # Request market data
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'market_data', 'data': {}}
            
            self.client.reqMktData(request_id, contract, "", False, False, [])
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                return self._format_error("Timeout waiting for market data")
            
            market_data = self._pending_requests.get(request_id, {}).get('data', {})
            
            return self._format_response({
                'symbol': symbol,
                'bid': self._parse_decimal(market_data.get('bid')),
                'ask': self._parse_decimal(market_data.get('ask')),
                'last': self._parse_decimal(market_data.get('last')),
                'high': self._parse_decimal(market_data.get('high')),
                'low': self._parse_decimal(market_data.get('low')),
                'volume': self._parse_decimal(market_data.get('volume')),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS market data: {e}")
            return self._format_error(str(e))
    
    def place_order(self, symbol: str, action: str, quantity: int, order_type: str = "MKT",
                   limit_price: float = None, stop_price: float = None) -> Dict[str, Any]:
        """Place an order via TWS API"""
        try:
            if not self.authenticate():
                return self._format_error("Failed to connect to TWS/Gateway")
            
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            # Create order
            order = Order()
            order.action = action.upper()  # BUY or SELL
            order.totalQuantity = quantity
            order.orderType = order_type.upper()
            
            if limit_price and order_type.upper() in ["LMT", "STP LMT"]:
                order.lmtPrice = limit_price
            if stop_price and order_type.upper() in ["STP", "STP LMT"]:
                order.auxPrice = stop_price
            
            # Place order
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'order', 'data': {}}
            
            self.client.placeOrder(request_id, contract, order)
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                return self._format_error("Timeout waiting for order confirmation")
            
            order_data = self._pending_requests.get(request_id, {}).get('data', {})
            
            return self._format_response({
                'order_id': order_data.get('orderId'),
                'status': order_data.get('status'),
                'filled': order_data.get('filled'),
                'remaining': order_data.get('remaining'),
                'avg_fill_price': self._parse_decimal(order_data.get('avgFillPrice')),
                'symbol': symbol,
                'action': action,
                'quantity': quantity
            })
            
        except Exception as e:
            logger.error(f"Error placing IBKR TWS order: {e}")
            return self._format_error(str(e))
    
    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            if not self.authenticate():
                return self._format_error("Failed to connect to TWS/Gateway")
            
            self.client.cancelOrder(order_id)
            
            return self._format_response({
                'order_id': order_id,
                'status': 'cancelled',
                'message': 'Order cancellation requested'
            })
            
        except Exception as e:
            logger.error(f"Error cancelling IBKR TWS order: {e}")
            return self._format_error(str(e))
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders"""
        try:
            if not self.authenticate():
                return []
            
            # Request open orders
            request_id = self._get_next_request_id()
            self._pending_requests[request_id] = {'type': 'open_orders', 'data': []}
            
            self.client.reqAllOpenOrders()
            
            # Wait for response
            start_time = time.time()
            while request_id in self._pending_requests and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if request_id in self._pending_requests:
                logger.error("Timeout waiting for open orders")
                return []
            
            orders = self._pending_requests.get(request_id, {}).get('data', [])
            
            open_orders = []
            for order in orders:
                open_orders.append({
                    'order_id': order.get('orderId'),
                    'symbol': order.get('symbol'),
                    'action': order.get('action'),
                    'quantity': self._parse_decimal(order.get('totalQuantity')),
                    'order_type': order.get('orderType'),
                    'limit_price': self._parse_decimal(order.get('lmtPrice')),
                    'stop_price': self._parse_decimal(order.get('auxPrice')),
                    'status': order.get('status'),
                    'account': order.get('account')
                })
            
            return open_orders
            
        except Exception as e:
            logger.error(f"Error getting IBKR TWS open orders: {e}")
            return []
    
    def get_brokerage_link(self) -> str:
        """Get IBKR TWS download link"""
        return "https://www.interactivebrokers.com/en/trading/tws.php"


class IBKRClient(EWrapper, EClient):
    """IBKR TWS API client wrapper"""
    
    def __init__(self, service):
        EClient.__init__(self, self)
        self.service = service
        self.next_order_id = None
    
    def connectAck(self):
        """Called when connection is established"""
        self.service.connected = True
        logger.info("IBKR TWS connection established")
    
    def connectionClosed(self):
        """Called when connection is closed"""
        self.service.connected = False
        logger.info("IBKR TWS connection closed")
    
    def nextValidId(self, orderId: int):
        """Called when next valid order ID is received"""
        self.next_order_id = orderId
        logger.info(f"Next valid order ID: {orderId}")
    
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        """Called when an error occurs"""
        logger.error(f"IBKR TWS Error {errorCode}: {errorString} (reqId: {reqId})")
        
        # Handle specific error codes
        if errorCode == 502:  # Couldn't connect
            self.service.connected = False
        elif errorCode == 504:  # Not connected
            self.service.connected = False
    
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        """Called when account summary data is received"""
        if reqId in self.service._pending_requests:
            request = self.service._pending_requests[reqId]
            if request['type'] == 'balance':
                request['data'][tag] = value
                if tag == 'GrossPositionValue':  # Last tag
                    del self.service._pending_requests[reqId]
    
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        """Called when position data is received"""
        # Find the positions request
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'positions':
                request['data'].append({
                    'account': account,
                    'symbol': contract.symbol,
                    'exchange': contract.exchange,
                    'currency': contract.currency,
                    'position': position,
                    'avgCost': avgCost,
                    'contractId': contract.conId
                })
                break
    
    def positionEnd(self):
        """Called when all position data has been received"""
        # Mark positions request as complete
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'positions':
                del self.service._pending_requests[req_id]
                break
    
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        """Called when account value is updated"""
        # Store account data
        if accountName not in self.service.account_data:
            self.service.account_data[accountName] = {}
        self.service.account_data[accountName][key] = val
    
    def orderStatus(self, orderId: int, status: str, filled: float, remaining: float,
                   avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float,
                   clientId: int, whyHeld: str, mktCapPrice: float):
        """Called when order status is updated"""
        # Find the order request
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'order':
                request['data'] = {
                    'orderId': orderId,
                    'status': status,
                    'filled': filled,
                    'remaining': remaining,
                    'avgFillPrice': avgFillPrice,
                    'permId': permId,
                    'parentId': parentId,
                    'lastFillPrice': lastFillPrice,
                    'clientId': clientId,
                    'whyHeld': whyHeld,
                    'mktCapPrice': mktCapPrice
                }
                del self.service._pending_requests[req_id]
                break
    
    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState):
        """Called when open order data is received"""
        # Find the open orders request
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'open_orders':
                request['data'].append({
                    'orderId': orderId,
                    'symbol': contract.symbol,
                    'action': order.action,
                    'totalQuantity': order.totalQuantity,
                    'orderType': order.orderType,
                    'lmtPrice': order.lmtPrice,
                    'auxPrice': order.auxPrice,
                    'status': orderState.status,
                    'account': order.account
                })
                break
    
    def openOrderEnd(self):
        """Called when all open order data has been received"""
        # Mark open orders request as complete
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'open_orders':
                del self.service._pending_requests[req_id]
                break
    
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        """Called when market data price is received"""
        # Find the market data request
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'market_data':
                if tickType == TickTypeEnum.BID:
                    request['data']['bid'] = price
                elif tickType == TickTypeEnum.ASK:
                    request['data']['ask'] = price
                elif tickType == TickTypeEnum.LAST:
                    request['data']['last'] = price
                elif tickType == TickTypeEnum.HIGH:
                    request['data']['high'] = price
                elif tickType == TickTypeEnum.LOW:
                    request['data']['low'] = price
                break
    
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        """Called when market data size is received"""
        # Find the market data request
        for req_id, request in self.service._pending_requests.items():
            if request['type'] == 'market_data':
                if tickType == TickTypeEnum.VOLUME:
                    request['data']['volume'] = size
                break

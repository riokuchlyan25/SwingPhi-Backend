import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService


class WebullService(BaseBrokerageService):
    """Webull brokerage integration service"""
    
    BASE_URL = "https://api.webull.com/api"
    
    def __init__(self, account_id: str, username: str = None, password: str = None, 
                 access_token: str = None, refresh_token: str = None):
        super().__init__(account_id, access_token=access_token, refresh_token=refresh_token)
        self.username = username
        self.password = password
        self.device_id = self._generate_device_id()
        
    def _generate_device_id(self) -> str:
        """Generate a device ID for Webull API"""
        import uuid
        return str(uuid.uuid4())
    
    def authenticate(self) -> bool:
        """Authenticate with Webull API"""
        try:
            # Webull uses a multi-step authentication process
            # Step 1: Get verification code
            if self.username and self.password:
                login_data = {
                    "username": self.username,
                    "password": self.password,
                    "deviceId": self.device_id,
                    "regionId": 6  # US region
                }
                
                response = self._make_request(
                    "POST", 
                    f"{self.BASE_URL}/passport/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.access_token = data.get('data', {}).get('accessToken')
                        self.refresh_token = data.get('data', {}).get('refreshToken')
                        return True
            
            # If we have existing tokens, try to use them
            elif self.access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                return True
                
        except Exception as e:
            logger.error(f"Webull authentication failed: {e}")
            return False
        
        return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Webull account information"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/account/getSecAccountList")
            data = response.json()
            
            if data.get('success'):
                accounts = data.get('data', [])
                account_info = {
                    'account_id': self.account_id,
                    'brokerage': 'webull',
                    'accounts': accounts
                }
                return self._format_response(account_info)
            else:
                return self._format_error(data.get('message', 'Failed to get account info'))
                
        except Exception as e:
            return self._format_error(f"Error getting account info: {str(e)}")
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get Webull portfolio positions"""
        try:
            if not self.authenticate():
                return []
            
            response = self._make_request("GET", f"{self.BASE_URL}/portfolio/positions")
            data = response.json()
            
            if data.get('success'):
                positions = data.get('data', [])
                portfolio = []
                
                for position in positions:
                    portfolio.append({
                        'symbol': position.get('ticker', {}).get('symbol'),
                        'quantity': self._parse_decimal(position.get('position')),
                        'average_price': self._parse_decimal(position.get('avgPrice')),
                        'current_price': self._parse_decimal(position.get('marketValue')),
                        'market_value': self._parse_decimal(position.get('marketValue')),
                        'unrealized_pnl': self._parse_decimal(position.get('unrealizedPnl')),
                        'unrealized_pnl_percent': self._parse_decimal(position.get('unrealizedPnlPercent'))
                    })
                
                return portfolio
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Webull portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get Webull transaction history"""
        try:
            if not self.authenticate():
                return []
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            params = {
                'startDate': int(start_date.timestamp() * 1000),
                'endDate': int(end_date.timestamp() * 1000),
                'pageSize': 100
            }
            
            response = self._make_request("GET", f"{self.BASE_URL}/account/getStockOrderList", params=params)
            data = response.json()
            
            if data.get('success'):
                orders = data.get('data', [])
                transactions = []
                
                for order in orders:
                    transaction_type = 'buy' if order.get('side') == 'BUY' else 'sell'
                    
                    transactions.append({
                        'transaction_id': order.get('orderId'),
                        'transaction_type': transaction_type,
                        'symbol': order.get('ticker', {}).get('symbol'),
                        'quantity': self._parse_decimal(order.get('quantity')),
                        'price': self._parse_decimal(order.get('filledAvgPrice')),
                        'amount': self._parse_decimal(order.get('totalAmount')),
                        'fees': self._parse_decimal(order.get('commission')),
                        'transaction_date': self._parse_datetime(order.get('createTime'))
                    })
                
                return transactions
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Webull transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Webull account balance"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/account/getAccountBalance")
            data = response.json()
            
            if data.get('success'):
                balance_data = data.get('data', {})
                balance = {
                    'cash_balance': self._parse_decimal(balance_data.get('cash')),
                    'total_value': self._parse_decimal(balance_data.get('totalValue')),
                    'buying_power': self._parse_decimal(balance_data.get('buyingPower')),
                    'account_value': self._parse_decimal(balance_data.get('accountValue'))
                }
                return self._format_response(balance)
            else:
                return self._format_error(data.get('message', 'Failed to get balance'))
                
        except Exception as e:
            return self._format_error(f"Error getting balance: {str(e)}")
    
    def get_brokerage_link(self) -> str:
        """Get Webull brokerage login link"""
        return "https://www.webull.com/login" 
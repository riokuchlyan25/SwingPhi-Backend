import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService

logger = logging.getLogger(__name__)


class MoomooService(BaseBrokerageService):
    """Moomoo API integration"""
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None, username: str = None, password: str = None):
        super().__init__(account_id, api_key, secret_key, access_token, refresh_token)
        self.username = username
        self.password = password
        self.base_url = "https://api.moomoo.com/v1"
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}' if self.access_token else '',
            'X-API-Key': self.api_key if self.api_key else ''
        })
    
    def authenticate(self) -> bool:
        """Authenticate with Moomoo API"""
        try:
            if self.access_token:
                # Test existing token
                response = self._make_request('GET', f"{self.base_url}/user/profile")
                return response.status_code == 200
            elif self.username and self.password:
                # Login with credentials
                login_data = {
                    'username': self.username,
                    'password': self.password
                }
                response = self._make_request('POST', f"{self.base_url}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    return True
            return False
        except Exception as e:
            logger.error(f"Moomoo authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Moomoo account information"""
        try:
            response = self._make_request('GET', f"{self.base_url}/user/profile")
            data = response.json()
            
            return self._format_response({
                'account_id': data.get('account_id'),
                'account_name': data.get('name', 'Moomoo Account'),
                'account_type': data.get('account_type'),
                'currency': data.get('currency', 'USD')
            })
        except Exception as e:
            logger.error(f"Error getting Moomoo account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get Moomoo portfolio positions"""
        try:
            response = self._make_request('GET', f"{self.base_url}/portfolio/positions")
            data = response.json()
            
            portfolio = []
            for position in data.get('positions', []):
                portfolio.append({
                    'symbol': position.get('symbol'),
                    'quantity': self._parse_decimal(position.get('quantity')),
                    'average_price': self._parse_decimal(position.get('avg_price')),
                    'current_price': self._parse_decimal(position.get('current_price')),
                    'market_value': self._parse_decimal(position.get('market_value')),
                    'unrealized_pnl': self._parse_decimal(position.get('unrealized_pnl')),
                    'unrealized_pnl_percent': self._parse_decimal(position.get('unrealized_pnl_percent'))
                })
            
            return portfolio
        except Exception as e:
            logger.error(f"Error getting Moomoo portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get Moomoo transaction history"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            response = self._make_request('GET', f"{self.base_url}/transactions", params=params)
            data = response.json()
            
            transactions = []
            for tx in data.get('transactions', []):
                transactions.append({
                    'transaction_id': tx.get('transaction_id'),
                    'transaction_type': self._map_transaction_type(tx.get('type')),
                    'symbol': tx.get('symbol'),
                    'quantity': self._parse_decimal(tx.get('quantity')),
                    'price': self._parse_decimal(tx.get('price')),
                    'amount': self._parse_decimal(tx.get('amount')),
                    'fees': self._parse_decimal(tx.get('fees', 0)),
                    'transaction_date': self._parse_datetime(tx.get('date'))
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting Moomoo transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Moomoo account balance"""
        try:
            response = self._make_request('GET', f"{self.base_url}/account/balance")
            data = response.json()
            
            return self._format_response({
                'cash_balance': self._parse_decimal(data.get('cash_balance')),
                'total_value': self._parse_decimal(data.get('total_value')),
                'buying_power': self._parse_decimal(data.get('buying_power')),
                'available_funds': self._parse_decimal(data.get('available_funds')),
                'market_value': self._parse_decimal(data.get('market_value'))
            })
        except Exception as e:
            logger.error(f"Error getting Moomoo balance: {e}")
            return self._format_error(str(e))
    
    def _map_transaction_type(self, moomoo_type: str) -> str:
        """Map Moomoo transaction types to standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DIVIDEND': 'dividend',
            'DEPOSIT': 'deposit',
            'WITHDRAWAL': 'withdrawal',
            'TRANSFER': 'transfer'
        }
        return type_mapping.get(moomoo_type, 'other')
    
    def get_brokerage_link(self) -> str:
        """Get Moomoo brokerage login link"""
        return "https://www.moomoo.com/login" 
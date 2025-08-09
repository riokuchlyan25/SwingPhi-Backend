import requests
import json
import logging
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService

logger = logging.getLogger(__name__)


class CoinbaseService(BaseBrokerageService):
    """Coinbase API integration"""
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None, passphrase: str = None):
        super().__init__(account_id, api_key, secret_key, access_token, refresh_token)
        self.passphrase = passphrase
        self.base_url = "https://api.coinbase.com/v2"
        self.session.headers.update({
            'CB-ACCESS-KEY': self.api_key if self.api_key else '',
            'CB-ACCESS-SIGN': '',
            'CB-ACCESS-TIMESTAMP': '',
            'CB-ACCESS-PASSPHRASE': self.passphrase if self.passphrase else ''
        })
    
    def _sign_request(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Sign Coinbase API request"""
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp
        }
    
    def _make_signed_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make signed HTTP request to Coinbase API"""
        body = kwargs.get('json', '') or ''
        if isinstance(body, dict):
            body = json.dumps(body)
        
        headers = self._sign_request(method, path, body)
        self.session.headers.update(headers)
        
        return self._make_request(method, f"{self.base_url}{path}", **kwargs)
    
    def authenticate(self) -> bool:
        """Authenticate with Coinbase API"""
        try:
            if not self.api_key or not self.secret_key:
                return False
            
            # Test authentication by getting accounts
            response = self._make_signed_request('GET', '/accounts')
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Coinbase authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Coinbase account information"""
        try:
            response = self._make_signed_request('GET', '/accounts')
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                account = data['data'][0]  # Get first account
                return self._format_response({
                    'account_id': account.get('id'),
                    'account_name': account.get('name', 'Coinbase Account'),
                    'account_type': account.get('type'),
                    'currency': account.get('currency')
                })
            
            return self._format_error("No account information found")
        except Exception as e:
            logger.error(f"Error getting Coinbase account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get Coinbase portfolio positions"""
        try:
            response = self._make_signed_request('GET', '/accounts')
            data = response.json()
            
            portfolio = []
            for account in data.get('data', []):
                balance = self._parse_decimal(account.get('balance', {}).get('amount'))
                if balance and balance > 0:
                    portfolio.append({
                        'symbol': account.get('currency'),
                        'quantity': balance,
                        'average_price': self._parse_decimal(account.get('avg_price')),
                        'current_price': self._parse_decimal(account.get('current_price')),
                        'market_value': self._parse_decimal(account.get('balance', {}).get('amount')),
                        'unrealized_pnl': None,  # Crypto doesn't have traditional P&L
                        'unrealized_pnl_percent': None
                    })
            
            return portfolio
        except Exception as e:
            logger.error(f"Error getting Coinbase portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get Coinbase transaction history"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            response = self._make_signed_request('GET', '/fills', params=params)
            data = response.json()
            
            transactions = []
            for tx in data.get('data', []):
                transactions.append({
                    'transaction_id': tx.get('trade_id'),
                    'transaction_type': self._map_transaction_type(tx.get('side')),
                    'symbol': f"{tx.get('product_id', '').replace('-', '/')}",
                    'quantity': self._parse_decimal(tx.get('size')),
                    'price': self._parse_decimal(tx.get('price')),
                    'amount': self._parse_decimal(tx.get('fee')),
                    'fees': self._parse_decimal(tx.get('fee', 0)),
                    'transaction_date': self._parse_datetime(tx.get('created_at'))
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting Coinbase transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Coinbase account balance"""
        try:
            response = self._make_signed_request('GET', '/accounts')
            data = response.json()
            
            total_balance = Decimal('0')
            total_value = Decimal('0')
            
            for account in data.get('data', []):
                balance = self._parse_decimal(account.get('balance', {}).get('amount'))
                if balance:
                    total_balance += balance
                    # For crypto, balance is often the value
                    total_value += balance
            
            return self._format_response({
                'cash_balance': total_balance,
                'total_value': total_value,
                'buying_power': total_balance,  # In crypto, available balance is buying power
                'available_funds': total_balance,
                'market_value': total_value
            })
        except Exception as e:
            logger.error(f"Error getting Coinbase balance: {e}")
            return self._format_error(str(e))
    
    def _map_transaction_type(self, coinbase_type: str) -> str:
        """Map Coinbase transaction types to standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DEPOSIT': 'deposit',
            'WITHDRAWAL': 'withdrawal',
            'TRANSFER': 'transfer'
        }
        return type_mapping.get(coinbase_type, 'other')
    
    def get_brokerage_link(self) -> str:
        """Get Coinbase brokerage login link"""
        return "https://www.coinbase.com/login" 
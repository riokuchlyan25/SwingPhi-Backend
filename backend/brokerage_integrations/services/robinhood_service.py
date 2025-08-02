import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService


class RobinhoodService(BaseBrokerageService):
    """Robinhood brokerage integration service"""
    
    BASE_URL = "https://api.robinhood.com"
    
    def __init__(self, account_id: str, username: str = None, password: str = None, 
                 access_token: str = None, refresh_token: str = None):
        super().__init__(account_id, access_token=access_token, refresh_token=refresh_token)
        self.username = username
        self.password = password
        
    def authenticate(self) -> bool:
        """Authenticate with Robinhood API"""
        try:
            if self.username and self.password:
                login_data = {
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password",
                    "client_id": "c82SH0WZOsabOXGP2sxqcj34Fx44fnw5SNuCvb4",
                    "scope": "internal"
                }
                
                response = self._make_request(
                    "POST", 
                    f"{self.BASE_URL}/oauth2/token/",
                    data=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    
                    # Set authorization header
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    return True
            
            # If we have existing tokens, try to use them
            elif self.access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                return True
                
        except Exception as e:
            logger.error(f"Robinhood authentication failed: {e}")
            return False
        
        return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Robinhood account information"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/")
            data = response.json()
            
            if 'results' in data:
                accounts = data.get('results', [])
                account_info = {
                    'account_id': self.account_id,
                    'brokerage': 'robinhood',
                    'accounts': accounts
                }
                return self._format_response(account_info)
            else:
                return self._format_error('Failed to get account info')
                
        except Exception as e:
            return self._format_error(f"Error getting account info: {str(e)}")
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get Robinhood portfolio positions"""
        try:
            if not self.authenticate():
                return []
            
            response = self._make_request("GET", f"{self.BASE_URL}/positions/")
            data = response.json()
            
            if 'results' in data:
                positions = data.get('results', [])
                portfolio = []
                
                for position in positions:
                    if float(position.get('quantity', 0)) > 0:  # Only include positions with shares
                        portfolio.append({
                            'symbol': position.get('instrument', '').split('/')[-1],
                            'quantity': self._parse_decimal(position.get('quantity')),
                            'average_price': self._parse_decimal(position.get('average_buy_price')),
                            'current_price': None,  # Will be updated separately
                            'market_value': self._parse_decimal(position.get('market_value')),
                            'unrealized_pnl': self._parse_decimal(position.get('unrealized_pl')),
                            'unrealized_pnl_percent': self._parse_decimal(position.get('unrealized_plpc'))
                        })
                
                return portfolio
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Robinhood portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get Robinhood transaction history"""
        try:
            if not self.authenticate():
                return []
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            params = {
                'updated_at[gte]': start_date.isoformat(),
                'updated_at[lte]': end_date.isoformat()
            }
            
            response = self._make_request("GET", f"{self.BASE_URL}/orders/", params=params)
            data = response.json()
            
            if 'results' in data:
                orders = data.get('results', [])
                transactions = []
                
                for order in orders:
                    if order.get('state') == 'filled':
                        transaction_type = 'buy' if order.get('side') == 'buy' else 'sell'
                        
                        transactions.append({
                            'transaction_id': order.get('id'),
                            'transaction_type': transaction_type,
                            'symbol': order.get('instrument', '').split('/')[-1],
                            'quantity': self._parse_decimal(order.get('quantity')),
                            'price': self._parse_decimal(order.get('average_price')),
                            'amount': self._parse_decimal(order.get('cumulative_quantity')) * self._parse_decimal(order.get('average_price')),
                            'fees': self._parse_decimal(order.get('fees')),
                            'transaction_date': self._parse_datetime(order.get('last_transaction_at'))
                        })
                
                return transactions
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Robinhood transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Robinhood account balance"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/")
            data = response.json()
            
            if 'results' in data and data['results']:
                account = data['results'][0]  # Get first account
                balance = {
                    'cash_balance': self._parse_decimal(account.get('cash')),
                    'total_value': self._parse_decimal(account.get('portfolio_value')),
                    'buying_power': self._parse_decimal(account.get('buying_power')),
                    'account_value': self._parse_decimal(account.get('equity'))
                }
                return self._format_response(balance)
            else:
                return self._format_error('Failed to get balance')
                
        except Exception as e:
            return self._format_error(f"Error getting balance: {str(e)}") 
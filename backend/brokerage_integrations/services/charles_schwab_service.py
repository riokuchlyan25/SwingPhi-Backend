import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService


class CharlesSchwabService(BaseBrokerageService):
    """Charles Schwab brokerage integration service"""
    
    BASE_URL = "https://api.schwab.com"
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None):
        super().__init__(account_id, api_key=api_key, secret_key=secret_key, 
                        access_token=access_token, refresh_token=refresh_token)
        
    def authenticate(self) -> bool:
        """Authenticate with Charles Schwab API"""
        try:
            if self.api_key and self.secret_key:
                # Charles Schwab uses OAuth 2.0 with client credentials
                auth_data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.secret_key,
                    'scope': 'trading'
                }
                
                response = self._make_request(
                    "POST", 
                    f"{self.BASE_URL}/oauth2/token",
                    data=auth_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    
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
            logger.error(f"Charles Schwab authentication failed: {e}")
            return False
        
        return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Charles Schwab account information"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/{self.account_id}")
            data = response.json()
            
            account_info = {
                'account_id': self.account_id,
                'brokerage': 'charles_schwab',
                'account_type': data.get('accountType'),
                'account_name': data.get('accountName'),
                'status': data.get('status')
            }
            return self._format_response(account_info)
                
        except Exception as e:
            return self._format_error(f"Error getting account info: {str(e)}")
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get Charles Schwab portfolio positions"""
        try:
            if not self.authenticate():
                return []
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/{self.account_id}/positions")
            data = response.json()
            
            if 'positions' in data:
                positions = data.get('positions', [])
                portfolio = []
                
                for position in positions:
                    portfolio.append({
                        'symbol': position.get('symbol'),
                        'quantity': self._parse_decimal(position.get('quantity')),
                        'average_price': self._parse_decimal(position.get('averagePrice')),
                        'current_price': self._parse_decimal(position.get('currentPrice')),
                        'market_value': self._parse_decimal(position.get('marketValue')),
                        'unrealized_pnl': self._parse_decimal(position.get('unrealizedGainLoss')),
                        'unrealized_pnl_percent': self._parse_decimal(position.get('unrealizedGainLossPercent'))
                    })
                
                return portfolio
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Charles Schwab portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get Charles Schwab transaction history"""
        try:
            if not self.authenticate():
                return []
            
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            params = {
                'fromDate': start_date.strftime('%Y-%m-%d'),
                'toDate': end_date.strftime('%Y-%m-%d')
            }
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/{self.account_id}/transactions", params=params)
            data = response.json()
            
            if 'transactions' in data:
                transactions_data = data.get('transactions', [])
                transactions = []
                
                for transaction in transactions_data:
                    transaction_type = self._map_transaction_type(transaction.get('type'))
                    
                    transactions.append({
                        'transaction_id': transaction.get('transactionId'),
                        'transaction_type': transaction_type,
                        'symbol': transaction.get('symbol'),
                        'quantity': self._parse_decimal(transaction.get('quantity')),
                        'price': self._parse_decimal(transaction.get('price')),
                        'amount': self._parse_decimal(transaction.get('amount')),
                        'fees': self._parse_decimal(transaction.get('fees')),
                        'transaction_date': self._parse_datetime(transaction.get('transactionDate'))
                    })
                
                return transactions
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Charles Schwab transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Charles Schwab account balance"""
        try:
            if not self.authenticate():
                return self._format_error("Authentication failed")
            
            response = self._make_request("GET", f"{self.BASE_URL}/accounts/{self.account_id}/balance")
            data = response.json()
            
            balance = {
                'cash_balance': self._parse_decimal(data.get('cashBalance')),
                'total_value': self._parse_decimal(data.get('totalValue')),
                'buying_power': self._parse_decimal(data.get('buyingPower')),
                'account_value': self._parse_decimal(data.get('accountValue'))
            }
            return self._format_response(balance)
                
        except Exception as e:
            return self._format_error(f"Error getting balance: {str(e)}")
    
    def get_brokerage_link(self) -> str:
        """Get Charles Schwab brokerage login link"""
        return "https://www.schwab.com/login"
    
    def _map_transaction_type(self, schwab_type: str) -> str:
        """Map Charles Schwab transaction types to our standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DIVIDEND': 'dividend',
            'DEPOSIT': 'deposit',
            'WITHDRAWAL': 'withdrawal',
            'TRANSFER': 'transfer'
        }
        return type_mapping.get(schwab_type, 'transfer') 
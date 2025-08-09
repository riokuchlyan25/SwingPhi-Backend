import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService

logger = logging.getLogger(__name__)


class TradeStationService(BaseBrokerageService):
    """TradeStation API integration"""
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None):
        super().__init__(account_id, api_key, secret_key, access_token, refresh_token)
        self.base_url = "https://api.tradestation.com/v2"
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}' if self.access_token else '',
            'X-API-Key': self.api_key if self.api_key else ''
        })
    
    def authenticate(self) -> bool:
        """Authenticate with TradeStation API"""
        try:
            if self.access_token:
                # Test existing token
                response = self._make_request('GET', f"{self.base_url}/user/profile")
                return response.status_code == 200
            elif self.api_key and self.secret_key:
                # OAuth flow for TradeStation
                auth_data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.secret_key
                }
                response = self._make_request('POST', f"{self.base_url}/oauth/token", json=auth_data)
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    return True
            return False
        except Exception as e:
            logger.error(f"TradeStation authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get TradeStation account information"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}")
            data = response.json()
            
            return self._format_response({
                'account_id': data.get('AccountID'),
                'account_name': data.get('AccountName', 'TradeStation Account'),
                'account_type': data.get('AccountType'),
                'currency': data.get('Currency', 'USD')
            })
        except Exception as e:
            logger.error(f"Error getting TradeStation account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get TradeStation portfolio positions"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/positions")
            data = response.json()
            
            portfolio = []
            for position in data.get('Positions', []):
                portfolio.append({
                    'symbol': position.get('Symbol'),
                    'quantity': self._parse_decimal(position.get('Quantity')),
                    'average_price': self._parse_decimal(position.get('AveragePrice')),
                    'current_price': self._parse_decimal(position.get('LastPrice')),
                    'market_value': self._parse_decimal(position.get('MarketValue')),
                    'unrealized_pnl': self._parse_decimal(position.get('UnrealizedPnL')),
                    'unrealized_pnl_percent': self._parse_decimal(position.get('UnrealizedPnLPercent'))
                })
            
            return portfolio
        except Exception as e:
            logger.error(f"Error getting TradeStation portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get TradeStation transaction history"""
        try:
            params = {}
            if start_date:
                params['StartDate'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['EndDate'] = end_date.strftime('%Y-%m-%d')
            
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/history", params=params)
            data = response.json()
            
            transactions = []
            for tx in data.get('History', []):
                transactions.append({
                    'transaction_id': tx.get('TransactionID'),
                    'transaction_type': self._map_transaction_type(tx.get('TransactionType')),
                    'symbol': tx.get('Symbol'),
                    'quantity': self._parse_decimal(tx.get('Quantity')),
                    'price': self._parse_decimal(tx.get('Price')),
                    'amount': self._parse_decimal(tx.get('Amount')),
                    'fees': self._parse_decimal(tx.get('Commission', 0)),
                    'transaction_date': self._parse_datetime(tx.get('TransactionDate'))
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting TradeStation transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get TradeStation account balance"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/balances")
            data = response.json()
            
            return self._format_response({
                'cash_balance': self._parse_decimal(data.get('CashBalance')),
                'total_value': self._parse_decimal(data.get('NetLiquidation')),
                'buying_power': self._parse_decimal(data.get('BuyingPower')),
                'available_funds': self._parse_decimal(data.get('AvailableFunds')),
                'market_value': self._parse_decimal(data.get('MarketValue'))
            })
        except Exception as e:
            logger.error(f"Error getting TradeStation balance: {e}")
            return self._format_error(str(e))
    
    def _map_transaction_type(self, tradestation_type: str) -> str:
        """Map TradeStation transaction types to standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DIVIDEND': 'dividend',
            'DEPOSIT': 'deposit',
            'WITHDRAWAL': 'withdrawal',
            'TRANSFER': 'transfer'
        }
        return type_mapping.get(tradestation_type, 'other')
    
    def get_brokerage_link(self) -> str:
        """Get TradeStation brokerage login link"""
        return "https://www.tradestation.com/login" 
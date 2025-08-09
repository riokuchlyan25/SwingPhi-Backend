import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService

logger = logging.getLogger(__name__)


class ETradeService(BaseBrokerageService):
    """E-Trade API integration"""
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None):
        super().__init__(account_id, api_key, secret_key, access_token, refresh_token)
        self.base_url = "https://api.etrade.com/v1"
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}' if self.access_token else '',
            'Consumer-Key': self.api_key if self.api_key else ''
        })
    
    def authenticate(self) -> bool:
        """Authenticate with E-Trade API"""
        try:
            if self.access_token:
                # Test existing token
                response = self._make_request('GET', f"{self.base_url}/accounts")
                return response.status_code == 200
            elif self.api_key and self.secret_key:
                # OAuth flow for E-Trade
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
            logger.error(f"E-Trade authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get E-Trade account information"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}")
            data = response.json()
            
            return self._format_response({
                'account_id': data.get('accountId'),
                'account_name': data.get('accountName', 'E-Trade Account'),
                'account_type': data.get('accountType'),
                'currency': data.get('currency', 'USD')
            })
        except Exception as e:
            logger.error(f"Error getting E-Trade account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get E-Trade portfolio positions"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/portfolio")
            data = response.json()
            
            portfolio = []
            for position in data.get('PortfolioResponse', {}).get('AccountPortfolio', []):
                for holding in position.get('Position', []):
                    portfolio.append({
                        'symbol': holding.get('Product', {}).get('symbol'),
                        'quantity': self._parse_decimal(holding.get('quantity')),
                        'average_price': self._parse_decimal(holding.get('costBasis')),
                        'current_price': self._parse_decimal(holding.get('marketValue')),
                        'market_value': self._parse_decimal(holding.get('marketValue')),
                        'unrealized_pnl': self._parse_decimal(holding.get('unrealizedGainLoss')),
                        'unrealized_pnl_percent': self._parse_decimal(holding.get('unrealizedGainLossPercent'))
                    })
            
            return portfolio
        except Exception as e:
            logger.error(f"Error getting E-Trade portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get E-Trade transaction history"""
        try:
            params = {}
            if start_date:
                params['fromDate'] = start_date.strftime('%m/%d/%Y')
            if end_date:
                params['toDate'] = end_date.strftime('%m/%d/%Y')
            
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/transactions", params=params)
            data = response.json()
            
            transactions = []
            for tx in data.get('TransactionResponse', {}).get('Transaction', []):
                transactions.append({
                    'transaction_id': tx.get('transactionId'),
                    'transaction_type': self._map_transaction_type(tx.get('transactionType')),
                    'symbol': tx.get('Product', {}).get('symbol'),
                    'quantity': self._parse_decimal(tx.get('quantity')),
                    'price': self._parse_decimal(tx.get('price')),
                    'amount': self._parse_decimal(tx.get('amount')),
                    'fees': self._parse_decimal(tx.get('commission', 0)),
                    'transaction_date': self._parse_datetime(tx.get('transactionDate'))
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting E-Trade transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get E-Trade account balance"""
        try:
            response = self._make_request('GET', f"{self.base_url}/accounts/{self.account_id}/balance")
            data = response.json()
            
            balance_data = data.get('BalanceResponse', {}).get('AccountBalance', [])
            if balance_data:
                balance = balance_data[0]
                return self._format_response({
                    'cash_balance': self._parse_decimal(balance.get('cashBalance')),
                    'total_value': self._parse_decimal(balance.get('netAccountValue')),
                    'buying_power': self._parse_decimal(balance.get('buyingPower')),
                    'available_funds': self._parse_decimal(balance.get('availableFunds')),
                    'market_value': self._parse_decimal(balance.get('marketValue'))
                })
            
            return self._format_error("No balance information found")
        except Exception as e:
            logger.error(f"Error getting E-Trade balance: {e}")
            return self._format_error(str(e))
    
    def _map_transaction_type(self, etrade_type: str) -> str:
        """Map E-Trade transaction types to standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DIVIDEND': 'dividend',
            'DEPOSIT': 'deposit',
            'WITHDRAWAL': 'withdrawal',
            'TRANSFER': 'transfer'
        }
        return type_mapping.get(etrade_type, 'other')
    
    def get_brokerage_link(self) -> str:
        """Get E-Trade brokerage login link"""
        return "https://us.etrade.com/login" 
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from .base_service import BaseBrokerageService
import os

logger = logging.getLogger(__name__)


class IBKRService(BaseBrokerageService):
    """Interactive Brokers (IBKR) API integration"""
    
    def __init__(self, account_id: str = None, api_key: str = None, secret_key: str = None,
                 access_token: str = None, refresh_token: str = None,
                 base_url: str = None, verify_ssl: bool = None):
        super().__init__(account_id or "", api_key, secret_key, access_token, refresh_token)
        # IBKR Client Portal Gateway default base URL (local gateway)
        env_base = os.getenv("IBKR_BASE_URL", "https://localhost:5000/v1/api")
        self.base_url = (base_url or env_base).rstrip("/")
        # Local gateway uses self-signed cert; allow disabling verification
        if verify_ssl is None:
            # default: disable verification for localhost gateway
            self.verify_ssl = not self.base_url.startswith("https://localhost")
        else:
            self.verify_ssl = bool(verify_ssl)
        # IBKR Client Portal typically uses cookie-based auth; no token header
        # Keep session headers minimal
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def authenticate(self) -> bool:
        """Authenticate with IBKR API"""
        try:
            # Test authentication by calling client portal status
            response = self._make_request('GET', f"{self.base_url}/iserver/auth/status", verify=self.verify_ssl)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"IBKR authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get IBKR account information"""
        try:
            response = self._make_request('GET', f"{self.base_url}/iserver/accounts", verify=self.verify_ssl)
            data = response.json()
            
            if data and len(data) > 0:
                account = data[0]  # Get first account
                # Set default account_id if not provided
                if not self.account_id:
                    self.account_id = account.get('accountId') or account.get('id') or ""
                return self._format_response({
                    'account_id': self.account_id or account.get('accountId'),
                    'account_name': account.get('accountName', 'IBKR Account'),
                    'account_type': account.get('accountType'),
                    'currency': account.get('currency')
                })
            
            return self._format_error("No account information found")
        except Exception as e:
            logger.error(f"Error getting IBKR account info: {e}")
            return self._format_error(str(e))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get IBKR portfolio positions"""
        try:
            if not self.account_id:
                # Ensure we have an account id
                info = self.get_account_info()
                if not info.get('success'):
                    return []
            response = self._make_request('GET', f"{self.base_url}/portfolio/{self.account_id}/positions", verify=self.verify_ssl)
            data = response.json()
            
            portfolio = []
            for position in data:
                portfolio.append({
                    'symbol': position.get('contract', {}).get('symbol'),
                    'quantity': self._parse_decimal(position.get('position')),
                    'average_price': self._parse_decimal(position.get('avgCost')),
                    'current_price': self._parse_decimal(position.get('marketPrice')),
                    'market_value': self._parse_decimal(position.get('marketValue')),
                    'unrealized_pnl': self._parse_decimal(position.get('unrealizedPnL')),
                    'unrealized_pnl_percent': self._parse_decimal(position.get('unrealizedPnLPercent'))
                })
            
            return portfolio
        except Exception as e:
            logger.error(f"Error getting IBKR portfolio: {e}")
            return []
    
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get IBKR transaction history"""
        try:
            if not self.account_id:
                info = self.get_account_info()
                if not info.get('success'):
                    return []
            # Retrieve recent transactions if available
            response = self._make_request('GET', f"{self.base_url}/iserver/account/{self.account_id}/transactions", verify=self.verify_ssl)
            data = response.json()
            
            transactions = []
            for tx in data:
                tx_date = self._parse_datetime(tx.get('date'))
                
                # Apply date filtering if provided
                if start_date and tx_date and tx_date < start_date:
                    continue
                if end_date and tx_date and tx_date > end_date:
                    continue
                
                transactions.append({
                    'transaction_id': tx.get('transactionId'),
                    'transaction_type': self._map_transaction_type(tx.get('type')),
                    'symbol': tx.get('symbol'),
                    'quantity': self._parse_decimal(tx.get('quantity')),
                    'price': self._parse_decimal(tx.get('price')),
                    'amount': self._parse_decimal(tx.get('amount')),
                    'fees': self._parse_decimal(tx.get('commission')),
                    'transaction_date': tx_date
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting IBKR transactions: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get IBKR account balance"""
        try:
            if not self.account_id:
                info = self.get_account_info()
                if not info.get('success'):
                    return self._format_error('No account')
            response = self._make_request('GET', f"{self.base_url}/portfolio/{self.account_id}/summary", verify=self.verify_ssl)
            data = response.json()
            
            return self._format_response({
                'cash_balance': self._parse_decimal(data.get('cashBalance')),
                'total_value': self._parse_decimal(data.get('netLiquidation')),
                'buying_power': self._parse_decimal(data.get('buyingPower')),
                'available_funds': self._parse_decimal(data.get('availableFunds')),
                'gross_position_value': self._parse_decimal(data.get('grossPositionValue'))
            })
        except Exception as e:
            logger.error(f"Error getting IBKR balance: {e}")
            return self._format_error(str(e))
    
    def _map_transaction_type(self, ibkr_type: str) -> str:
        """Map IBKR transaction types to standard types"""
        type_mapping = {
            'BUY': 'buy',
            'SELL': 'sell',
            'DIV': 'dividend',
            'DEP': 'deposit',
            'WTH': 'withdrawal',
            'TRF': 'transfer'
        }
        return type_mapping.get(ibkr_type, 'other')
    
    def get_brokerage_link(self) -> str:
        """Get IBKR brokerage login link"""
        return "https://www.interactivebrokers.com/portal/main" 
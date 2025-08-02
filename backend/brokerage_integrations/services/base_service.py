import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


class BaseBrokerageService(ABC):
    """Base class for all brokerage integration services"""
    
    def __init__(self, account_id: str, api_key: str = None, secret_key: str = None, 
                 access_token: str = None, refresh_token: str = None):
        self.account_id = account_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SwingPhi-Brokerage-Integration/1.0',
            'Content-Type': 'application/json'
        })
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the brokerage API"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Get basic account information"""
        pass
    
    @abstractmethod
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get current portfolio positions"""
        pass
    
    @abstractmethod
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get transaction history"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance information"""
        pass
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Safely parse decimal values"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """Safely parse datetime values"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # Handle common datetime formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            elif isinstance(value, (int, float)):
                # Handle timestamp
                return datetime.fromtimestamp(value)
        except Exception:
            pass
        return None
    
    def _format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response data consistently"""
        return {
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_error(self, error: str) -> Dict[str, Any]:
        """Format error response consistently"""
        return {
            'success': False,
            'error': error,
            'timestamp': datetime.now().isoformat()
        } 
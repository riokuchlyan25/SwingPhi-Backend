import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import json

class FMPService:
    """Service for interacting with Financial Modeling Prep API"""
    
    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY')
        self.base_url = 'https://financialmodelingprep.com/api/v3'
        
        if not self.api_key:
            raise ValueError("FMP_API_KEY environment variable is required")
    
    def get_historical_price_data(self, ticker: str, period: str = "6mo") -> pd.DataFrame:
        """
        Get historical price data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (6mo, 1y, 2y, 5y, max)
            
        Returns:
            DataFrame with historical price data
        """
        try:
            # Convert period to days for FMP API
            period_days = {
                "6mo": 180,
                "1y": 365,
                "2y": 730,
                "5y": 1825,
                "max": 3650
            }
            
            days = period_days.get(period, 180)
            
            url = f"{self.base_url}/historical-price-full/{ticker}"
            params = {
                'apikey': self.api_key,
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'historical' not in data or not data['historical']:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['historical'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching FMP data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_company_profile(self, ticker: str) -> Dict:
        """
        Get company profile information
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with company profile data
        """
        try:
            url = f"{self.base_url}/profile/{ticker}"
            params = {'apikey': self.api_key}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]
            else:
                return {}
                
        except Exception as e:
            print(f"Error fetching company profile for {ticker}: {str(e)}")
            return {}
    
    def get_stock_quote(self, ticker: str) -> Dict:
        """
        Get current stock quote
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with current quote data
        """
        try:
            url = f"{self.base_url}/quote/{ticker}"
            params = {'apikey': self.api_key}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]
            else:
                return {}
                
        except Exception as e:
            print(f"Error fetching stock quote for {ticker}: {str(e)}")
            return {}

    def get_intraday_price_data(self, ticker: str, interval: str = "1hour", limit: int = 200) -> pd.DataFrame:
        """
        Get intraday OHLCV data for a ticker at a specified interval.

        Args:
            ticker: Stock ticker symbol
            interval: One of ['1min','5min','15min','30min','1hour','4hour']
            limit: Maximum number of data points to return

        Returns:
            DataFrame with datetime index and columns: open, high, low, close, volume
        """
        try:
            supported = {"1min", "5min", "15min", "30min", "1hour", "4hour"}
            if interval not in supported:
                interval = "1hour"

            url = f"{self.base_url}/historical-chart/{interval}/{ticker}"
            params = {
                'apikey': self.api_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json() or []

            if not data:
                return pd.DataFrame()

            # FMP returns most recent first; trim and reverse to chronological
            data = data[:limit]
            df = pd.DataFrame(data)
            # Normalize columns to lower-case
            df.columns = [c.lower() for c in df.columns]

            # Expect keys: date, open, high, low, close, volume
            if 'date' not in df.columns:
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').set_index('date')

            # Keep standard columns if present
            keep_cols = [c for c in ['open', 'high', 'low', 'close', 'volume'] if c in df.columns]
            df = df[keep_cols]
            return df
        except Exception as e:
            print(f"Error fetching intraday {interval} data for {ticker}: {str(e)}")
            return pd.DataFrame()

    def get_most_active_stocks(self, limit: int = 20) -> List[Dict]:
        """
        Get list of most active stocks (by volume) from FMP.

        Args:
            limit: Max number of items to return

        Returns:
            List of dicts with keys: symbol, name, price, change, changesPercentage, volume
        """
        try:
            url = f"{self.base_url}/actives"
            params = {
                'apikey': self.api_key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json() or []
            trimmed = []
            for item in data[:limit]:
                trimmed.append({
                    'symbol': item.get('ticker') or item.get('symbol'),
                    'name': item.get('companyName') or item.get('name'),
                    'price': item.get('price'),
                    'change': item.get('changes') or item.get('change'),
                    'changesPercentage': item.get('changesPercentage'),
                    'volume': item.get('volume')
                })
            return trimmed
        except Exception as e:
            print(f"Error fetching most active stocks: {str(e)}")
            return []

# Global FMP service instance
fmp_service = FMPService() 
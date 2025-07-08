# internal
from financial_data.config import FMP_API_KEY

# external
import requests
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
import yfinance as yf

# built-in

# Sector mappings with representative stocks
SECTOR_STOCKS = {
    'technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMZN', 'TSLA', 'NFLX', 'ADBE', 'CRM'],
    'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN'],
    'financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF'],
    'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL'],
    'consumer_discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'GM', 'F'],
    'consumer_staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'HSY'],
    'industrials': ['BA', 'CAT', 'GE', 'HON', 'MMM', 'LMT', 'RTX', 'UPS', 'FDX', 'UNP'],
    'utilities': ['NEE', 'DUK', 'SO', 'D', 'EXC', 'XEL', 'SRE', 'PEG', 'ES', 'ED'],
    'materials': ['LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'IFF'],
    'real_estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'WELL', 'SPG', 'PSA', 'O', 'CBRE', 'EXR'],
    'communication_services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR', 'TMUS', 'DISH']
}

def get_sector_trends_api(request):
    """Analyze sector trends and determine if positive, negative, or neutral"""
    if request.method == 'GET':
        sector = request.GET.get('sector', '').lower().strip()
        
        if not sector:
            return JsonResponse({
                'error': 'Sector parameter required',
                'available_sectors': list(SECTOR_STOCKS.keys())
            }, status=400)
        
        if sector not in SECTOR_STOCKS:
            return JsonResponse({
                'error': f'Sector "{sector}" not supported',
                'available_sectors': list(SECTOR_STOCKS.keys())
            }, status=400)
        
        try:
            # Get stock symbols for the sector
            sector_symbols = SECTOR_STOCKS[sector]
            
            # Analyze sector performance
            result = analyze_sector_performance(sector, sector_symbols)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'error': 'GET method required'
        }, status=405)

def analyze_sector_performance(sector_name, symbols):
    """Analyze sector performance with simplified response"""
    
    # Initialize tracking variables
    successful_analyses = 0
    price_changes = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    # Analyze each stock in the sector
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="30d", interval="1d")
            
            if df is None or df.empty or len(df) < 2:
                continue
            
            successful_analyses += 1
            
            # Calculate price performance
            latest_price = float(df['Close'].iloc[-1])
            start_price = float(df['Close'].iloc[0])
            price_change_pct = ((latest_price - start_price) / start_price) * 100
            
            price_changes.append(price_change_pct)
            
            # Categorize stock performance
            if price_change_pct > 2:
                positive_count += 1
            elif price_change_pct < -2:
                negative_count += 1
            else:
                neutral_count += 1
            
        except Exception:
            continue
    
    if successful_analyses == 0:
        return {
            'error': 'No data available for sector'
        }
    
    # Calculate sector metrics
    avg_price_change = round(sum(price_changes) / len(price_changes), 2)
    positive_ratio = positive_count / successful_analyses
    negative_ratio = negative_count / successful_analyses
    
    # Determine overall sector sentiment
    if positive_ratio >= 0.6:
        sentiment = 'positive'
    elif negative_ratio >= 0.6:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'sector': sector_name.replace('_', ' ').title(),
        'sentiment': sentiment,
        'avg_30d_change': avg_price_change,
        'stocks_positive': positive_count,
        'stocks_negative': negative_count,
        'stocks_neutral': neutral_count,
        'stocks_analyzed': successful_analyses
    }

def get_available_sectors_api(request):
    """Get simplified list of available sectors"""
    if request.method == 'GET':
        return JsonResponse({
            'sectors': list(SECTOR_STOCKS.keys())
        })
    else:
        return JsonResponse({
            'error': 'GET method required'
        }, status=405) 
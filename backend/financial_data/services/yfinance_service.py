# internal

# external
import requests
import base64
import json
import yfinance as yf
import pandas as pd

# built-in
from django.http import JsonResponse
import json

def get_ticker_from_request(request):
    """Helper function to get ticker from both form data and JSON"""
    ticker = request.POST.get('ticker', '')
    if not ticker and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            ticker = data.get('ticker', '')
        except json.JSONDecodeError:
            ticker = ''
    return ticker.strip().upper() if ticker else ''

def yfinance_price_change_api(request):
    """Get price change analysis for a stock"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_price_change_data(ticker)
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch price change data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_price_change_data(ticker: str) -> dict:
    """Analyze price change for a stock ticker with simplified response"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="10d", interval="1d")
        
        if df is None or df.empty or len(df) < 2:
            return {
                'error': 'No data available'
            }
        
        # Get the two most recent trading days
        latest_price = float(df['Close'].iloc[-1])
        previous_price = float(df['Close'].iloc[-2])
        
        # Validate prices
        if latest_price <= 0 or previous_price <= 0:
            return {
                'error': 'Invalid price data'
            }
        
        # Calculate changes
        price_change = round(latest_price - previous_price, 2)
        percentage_change = round((price_change / previous_price) * 100, 2)
        
        # Determine direction
        direction = "up" if price_change > 0 else "down" if price_change < 0 else "unchanged"
        
        return {
            'ticker': ticker,
            'current_price': round(latest_price, 2),
            'previous_price': round(previous_price, 2),
            'price_change': price_change,
            'percentage_change': percentage_change,
            'direction': direction
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }

def yfinance_daily_api(request):
    """Get simplified daily stock data"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_daily_data(ticker)
            parsed_data = json.loads(data)
            
            if 'error' in parsed_data:
                return JsonResponse(parsed_data, status=500)
                
            return JsonResponse({
                'ticker': ticker,
                'data': parsed_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_daily_data(ticker: str) -> str:
    """Fetch simplified daily stock data"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="5d", interval="1d")
        
        if df is None or df.empty:
            return json.dumps({'error': 'No data available'})
        
        df.reset_index(inplace=True)
        data = []
        
        for _, row in df.iterrows():
            # Only include rows with valid data
            if all(pd.notna([row["Close"], row["Open"], row["High"], row["Low"], row["Volume"]])):
                if all(val > 0 for val in [row["Close"], row["Open"], row["High"], row["Low"], row["Volume"]]):
                    data.append({
                        "date": row["Date"].strftime("%Y-%m-%d"),
                        "close": round(float(row["Close"]), 2),
                        "open": round(float(row["Open"]), 2),
                        "high": round(float(row["High"]), 2),
                        "low": round(float(row["Low"]), 2),
                        "volume": int(row["Volume"])
                    })
        
        if not data:
            return json.dumps({'error': 'No valid data found'})
            
        return json.dumps(data)
    except Exception as e:
        return json.dumps({'error': str(e)})

def yfinance_weekly_api(request):
    """Get simplified weekly stock data"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_weekly_data(ticker)
            parsed_data = json.loads(data)
            
            if 'error' in parsed_data:
                return JsonResponse(parsed_data, status=500)
                
            return JsonResponse({
                'ticker': ticker,
                'data': parsed_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_weekly_data(ticker: str) -> str:
    """Fetch simplified weekly stock data"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1wk")
        
        if df is None or df.empty:
            return json.dumps({'error': 'No data available'})
        
        df.reset_index(inplace=True)
        data = []
        
        for _, row in df.iterrows():
            if all(pd.notna([row["Close"], row["Open"], row["High"], row["Low"], row["Volume"]])):
                if all(val > 0 for val in [row["Close"], row["Open"], row["High"], row["Low"], row["Volume"]]):
                    data.append({
                        "date": row["Date"].strftime("%Y-%m-%d"),
                        "close": round(float(row["Close"]), 2),
                        "open": round(float(row["Open"]), 2),
                        "high": round(float(row["High"]), 2),
                        "low": round(float(row["Low"]), 2),
                        "volume": int(row["Volume"])
                    })
        
        if not data:
            return json.dumps({'error': 'No valid data found'})
            
        return json.dumps(data)
    except Exception as e:
        return json.dumps({'error': str(e)})

def yfinance_yearly_api(request):
    """Get yearly stock data for maximum available period"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_yearly_data(ticker)
            return JsonResponse({'yearly': json.loads(data)})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch yearly data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_yearly_data(ticker: str) -> str:
    """Fetch yearly stock data with monthly intervals"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="max", interval="1mo")
    df.reset_index(inplace=True)
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": round(row["Close"], 2),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "volume": int(row["Volume"])
        })
    return json.dumps(data)

def yfinance_max_api(request):
    """Get maximum available stock data with daily intervals"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_max_data(ticker)
            return JsonResponse({'max': json.loads(data)})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch max data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_max_data(ticker: str) -> str:
    """Fetch maximum available stock data with daily intervals"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="max", interval="1d")
    df.reset_index(inplace=True)
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": round(row["Close"], 2),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "volume": int(row["Volume"])
        })
    return json.dumps(data)

def yfinance_monthly_api(request):
    """Get monthly stock data for the past 5 years"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_monthly_data(ticker)
            return JsonResponse({'monthly': json.loads(data)})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch monthly data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_monthly_data(ticker: str) -> str:
    """Fetch monthly stock data for the past 5 years"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y", interval="1mo")
    df.reset_index(inplace=True)
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": round(row["Close"], 2),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "volume": int(row["Volume"])
        })
    return json.dumps(data)
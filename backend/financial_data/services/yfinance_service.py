# internal

# external
import requests
import base64
import json
import yfinance as yf

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
    return ticker

def yfinance_daily_api(request):
    """Get daily stock data for the past 5 days"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_daily_data(ticker)
            return JsonResponse({'daily': json.loads(data)})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch daily data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_daily_data(ticker: str) -> str:
    """Fetch daily stock data for the past 5 days"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="5d", interval="1d")
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

def yfinance_weekly_api(request):
    """Get weekly stock data for the past year"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = yfinance_weekly_data(ticker)
            return JsonResponse({'weekly': json.loads(data)})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch weekly data: {str(e)}'}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def yfinance_weekly_data(ticker: str) -> str:
    """Fetch weekly stock data for the past year"""
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1wk")
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
# internal
from financial_data.config import FRED_API_KEY, PHI_RESEARCH_CHARLES_SCHWAB_KEY, PHI_RESEARCH_CHARLES_SCHWAB_SECRET 

# external
import requests
import base64
import json
import yfinance as yf

# built-in
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

FRED_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations'

# Helper to fetch FRED data
def fetch_fred_data(series_id, frequency):
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'frequency': frequency,
    }
    response = requests.get(FRED_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('observations', [])
    return []

@csrf_exempt
def fred_yearly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'a')  # annual
        return JsonResponse({'yearly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_monthly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'm')  # monthly
        return JsonResponse({'monthly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_weekly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'w')  # weekly
        return JsonResponse({'weekly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_max_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'd')
        return JsonResponse({'max': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def charles_schwab_view(request):
    """
    Initiate Charles Schwab OAuth 2.0 authentication flow
    """
    if request.method == 'GET':
        # Build the authorization URL
        auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={PHI_RESEARCH_CHARLES_SCHWAB_KEY}&redirect_uri=http://127.0.0.1:8000/charles_schwab_callback"
        
        print(f"auth_url: {auth_url}")
        
        # Return the authorization URL for the client to redirect to
        return JsonResponse({
            'auth_url': auth_url,
            'message': 'Redirect to this URL to authenticate with Charles Schwab'
        })
    
    return JsonResponse({'error': 'GET required'}, status=400)

@csrf_exempt
def charles_schwab_callback(request):
    """
    Handle the OAuth callback from Charles Schwab and exchange authorization code for tokens
    """
    if request.method == 'GET':
        # Get the authorization code from the callback URL
        auth_code = request.GET.get('code')
        
        if not auth_code:
            return JsonResponse({'error': 'Authorization code not found'}, status=400)
        
        # Clean up the authorization code (remove any URL encoding artifacts)
        if '%40' in auth_code:
            auth_code = auth_code.replace('%40', '@')
        
        # Prepare credentials for token exchange
        credentials = f"{PHI_RESEARCH_CHARLES_SCHWAB_KEY}:{PHI_RESEARCH_CHARLES_SCHWAB_SECRET}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        # Prepare headers and payload for token request
        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "http://127.0.0.1:8000/charles_schwab_callback",
        }
        
        try:
            # Exchange authorization code for access and refresh tokens
            token_response = requests.post(
                url="https://api.schwabapi.com/v1/oauth/token",
                headers=headers,
                data=payload,
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                
                # Store tokens securely (in a real application, you'd want to store these in a database or secure storage)
                # For now, we'll just return them in the response
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully authenticated with Charles Schwab',
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type')
                })
            else:
                return JsonResponse({
                    'error': 'Failed to exchange authorization code for tokens',
                    'details': token_response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred during token exchange',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'GET required'}, status=400)

@csrf_exempt
def charles_schwab_refresh_token(request):
    """
    Refresh Charles Schwab access token using refresh token
    """
    if request.method == 'POST':
        refresh_token = request.POST.get('refresh_token')
        
        if not refresh_token:
            return JsonResponse({'error': 'Refresh token required'}, status=400)
        
        # Prepare credentials
        credentials = f"{PHI_RESEARCH_CHARLES_SCHWAB_KEY}:{PHI_RESEARCH_CHARLES_SCHWAB_SECRET}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        try:
            refresh_response = requests.post(
                url="https://api.schwabapi.com/v1/oauth/token",
                headers=headers,
                data=payload,
            )
            
            if refresh_response.status_code == 200:
                token_data = refresh_response.json()
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully refreshed access token',
                    'access_token': token_data.get('access_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type')
                })
            else:
                return JsonResponse({
                    'error': 'Failed to refresh access token',
                    'details': refresh_response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred during token refresh',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def save_close_values_to_json(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        period = request.POST.get('period', '1mo')
        interval = request.POST.get('interval', '1d')
        data = save_close_values_to_json_helper(ticker, period, interval)
        return JsonResponse({'data': data})
    return JsonResponse({'error': 'POST required'}, status=400)

#helper function to save close values to json
def save_close_values_to_json_helper(ticker: str, period: str = "1mo", interval: str = "1d") -> str:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    df.reset_index(inplace=True)
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": round(row["Close"], 2)
        })
    return json.dumps(data)

@csrf_exempt
def yfinance_daily_view(request):
    """Get daily stock data for the past 5 days"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
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

@csrf_exempt
def yfinance_weekly_view(request):
    """Get weekly stock data for the past year"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
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

@csrf_exempt
def yfinance_yearly_view(request):
    """Get yearly stock data for maximum available period"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
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

@csrf_exempt
def yfinance_max_view(request):
    """Get maximum available stock data with daily intervals"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
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

@csrf_exempt
def yfinance_monthly_view(request):
    """Get monthly stock data for the past 5 years"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
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

# Template views for testing interfaces
def yfinance_template(request):
    """Render YFinance testing template"""
    return render(request, 'financial_data/yfinance.html')

def fred_template(request):
    """Render FRED testing template"""
    return render(request, 'financial_data/fred.html')

def charles_schwab_template(request):
    """Render Charles Schwab testing template"""
    return render(request, 'financial_data/charles_schwab.html')
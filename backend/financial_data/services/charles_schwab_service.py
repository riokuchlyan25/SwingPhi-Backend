from financial_data.config import PHI_RESEARCH_CHARLES_SCHWAB_KEY, PHI_RESEARCH_CHARLES_SCHWAB_SECRET 

# external
import requests
import base64
import json

# built-in
from django.http import JsonResponse

def charles_schwab_api(request):
    """
    Initiate Charles Schwab OAuth 2.0 authentication flow
    """
    if request.method == 'GET':
        # Build the authorization URL
        auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={PHI_RESEARCH_CHARLES_SCHWAB_KEY}&redirect_uri=http://127.0.0.1:8000/financial_data/charles_schwab_callback/"
        
        print(f"auth_url: {auth_url}")
        
        # Return the authorization URL for the client to redirect to
        return JsonResponse({
            'auth_url': auth_url,
            'message': 'Redirect to this URL to authenticate with Charles Schwab'
        })
    
    return JsonResponse({'error': 'GET required'}, status=400)

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
            "redirect_uri": "http://127.0.0.1:8000/financial_data/charles_schwab_callback/",
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

def get_symbol_and_token_from_request(request):
    """Helper function to get symbol and access token from both form data and JSON"""
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '')
        access_token = data.get('access_token', '')
    except json.JSONDecodeError:
        symbol = request.POST.get('symbol', '')
        access_token = request.POST.get('access_token', '')
    return symbol, access_token

def charles_schwab_price_data(request):
    """
    Get price data for a stock using Charles Schwab API
    """
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        # Prepare headers for API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            # Get price data from Charles Schwab API
            price_response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=day&period=10&frequencyType=minute&frequency=1",
                headers=headers,
            )
            
            if price_response.status_code == 200:
                price_data = price_response.json()
                return JsonResponse({
                    'success': True,
                    'symbol': symbol,
                    'price_data': price_data
                })
            else:
                return JsonResponse({
                    'error': 'Failed to fetch price data',
                    'details': price_response.text,
                    'status_code': price_response.status_code
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred while fetching price data',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_daily_api(request):
    """Get daily stock data for the past 5 days using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=day&period=5&frequencyType=daily&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'daily': data})
            else:
                return JsonResponse({
                    'error': 'Failed to fetch daily data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch daily data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_weekly_api(request):
    """Get weekly stock data for the past year using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=year&period=1&frequencyType=weekly&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'weekly': data})
            else:
                return JsonResponse({
                    'error': 'Failed to fetch weekly data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch weekly data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_monthly_api(request):
    """Get monthly stock data for the past 5 years using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=year&period=5&frequencyType=monthly&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'monthly': data})
            else:
                return JsonResponse({
                    'error': 'Failed to fetch monthly data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch monthly data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_yearly_api(request):
    """Get yearly stock data for the past 20 years using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=year&period=20&frequencyType=monthly&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'yearly': data})
            else:
                return JsonResponse({
                    'error': 'Failed to fetch yearly data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch yearly data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_max_api(request):
    """Get maximum available stock data using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=year&period=20&frequencyType=daily&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'max': data})
            else:
                return JsonResponse({
                    'error': 'Failed to fetch max data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch max data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def charles_schwab_price_change_api(request):
    """Get price change analysis for a stock using Charles Schwab API"""
    if request.method == 'POST':
        symbol, access_token = get_symbol_and_token_from_request(request)
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            # Get recent daily data to analyze price change
            response = requests.get(
                url=f"https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={symbol}&periodType=day&period=5&frequencyType=daily&frequency=1",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candles' not in data or len(data['candles']) < 2:
                    return JsonResponse({
                        'error': 'Insufficient data available for price change analysis',
                        'symbol': symbol
                    })
                
                # Get the two most recent trading days
                candles = data['candles']
                latest_candle = candles[-1]
                previous_candle = candles[-2]
                
                latest_price = latest_candle['close']
                previous_price = previous_candle['close']
                
                # Calculate changes
                price_change = latest_price - previous_price
                percentage_change = (price_change / previous_price) * 100
                
                # Determine direction
                if price_change > 0:
                    direction = "UP"
                    direction_symbol = "↗"
                elif price_change < 0:
                    direction = "DOWN"
                    direction_symbol = "↘"
                else:
                    direction = "UNCHANGED"
                    direction_symbol = "→"
                
                # Convert timestamps to dates
                import datetime
                latest_date = datetime.datetime.fromtimestamp(latest_candle['datetime'] / 1000).strftime("%Y-%m-%d")
                previous_date = datetime.datetime.fromtimestamp(previous_candle['datetime'] / 1000).strftime("%Y-%m-%d")
                
                return JsonResponse({
                    'symbol': symbol.upper(),
                    'direction': direction,
                    'direction_symbol': direction_symbol,
                    'price_change': round(price_change, 2),
                    'percentage_change': round(percentage_change, 2),
                    'current_price': round(latest_price, 2),
                    'previous_price': round(previous_price, 2),
                    'current_date': latest_date,
                    'previous_date': previous_date,
                    'summary': f"{symbol.upper()} went {direction} by ${abs(round(price_change, 2))} ({abs(round(percentage_change, 2))}%) from {previous_date} to {latest_date}"
                })
            else:
                return JsonResponse({
                    'error': 'Failed to fetch price change data',
                    'details': response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch price change data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def schwab_data_daily(ticker: str) -> str:
    """Get simplified daily data from mock Charles Schwab API"""
    try:
        # Mock Schwab-style data response
        data = [{
            "date": "2024-01-05",
            "close": 185.92,
            "open": 182.15,
            "high": 186.40,
            "low": 181.75,
            "volume": 52847200
        }]
        return json.dumps(data)
    except Exception as e:
        return json.dumps({'error': str(e)})

def schwab_price_data(ticker: str) -> dict:
    """Get simplified price data"""
    try:
        return {
            'ticker': ticker,
            'current_price': 185.92,
            'change': 2.45,
            'change_percent': 1.33,
            'direction': 'up'
        }
    except Exception as e:
        return {'error': str(e)}

def schwab_price_change_data(ticker: str) -> dict:
    """Get simplified price change data"""
    try:
        return {
            'ticker': ticker,
            'current_price': 185.92,
            'previous_price': 183.47,
            'price_change': 2.45,
            'percentage_change': 1.33,
            'direction': 'up'
        }
    except Exception as e:
        return {'error': str(e)}

def schwab_daily_api(request):
    """Get simplified daily data"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = schwab_data_daily(ticker)
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

def schwab_price_api(request):
    """Get simplified current price"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = schwab_price_data(ticker)
            if 'error' in data:
                return JsonResponse(data, status=500)
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def schwab_price_change_api(request):
    """Get simplified price change"""
    if request.method == 'POST':
        ticker = get_ticker_from_request(request)
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            data = schwab_price_change_data(ticker)
            if 'error' in data:
                return JsonResponse(data, status=500)
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

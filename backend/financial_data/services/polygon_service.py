# internal
from financial_data.config import POLYGON_API_KEY

# external
import requests
import json
from datetime import datetime, timedelta

# built-in
from django.http import JsonResponse

def get_symbol_from_request(request):
    """Helper function to get crypto symbol from both form data and JSON"""
    symbol = request.POST.get('symbol', '')
    if not symbol and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            symbol = data.get('symbol', '')
        except json.JSONDecodeError:
            symbol = ''
    return symbol

def polygon_crypto_daily_api(request):
    """Get daily crypto data for the past 30 days using Polygon API"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required (e.g., BTC, ETH, ADA)'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'Polygon API key not configured'}, status=500)
        
        try:
            # Format symbol for Polygon (e.g., BTC -> X:BTCUSD)
            formatted_symbol = f"X:{symbol.upper()}USD"
            
            # Get data for last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'apikey': POLYGON_API_KEY,
                'adjusted': 'true',
                'sort': 'asc'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    formatted_data = []
                    for result in data['results']:
                        formatted_data.append({
                            'date': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d'),
                            'open': round(result['o'], 2),
                            'high': round(result['h'], 2),
                            'low': round(result['l'], 2),
                            'close': round(result['c'], 2),
                            'volume': result['v']
                        })
                    
                    return JsonResponse({
                        'daily': formatted_data,
                        'symbol': symbol.upper(),
                        'count': len(formatted_data)
                    })
                else:
                    return JsonResponse({
                        'error': f'No data found for {symbol}. Please check the symbol.',
                        'symbol': symbol
                    }, status=404)
            else:
                return JsonResponse({
                    'error': 'Failed to fetch data from Polygon API',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch daily crypto data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def polygon_crypto_weekly_api(request):
    """Get weekly crypto data for the past year using Polygon API"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required (e.g., BTC, ETH, ADA)'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'Polygon API key not configured'}, status=500)
        
        try:
            formatted_symbol = f"X:{symbol.upper()}USD"
            
            # Get data for last year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/week/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'apikey': POLYGON_API_KEY,
                'adjusted': 'true',
                'sort': 'asc'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    formatted_data = []
                    for result in data['results']:
                        formatted_data.append({
                            'date': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d'),
                            'open': round(result['o'], 2),
                            'high': round(result['h'], 2),
                            'low': round(result['l'], 2),
                            'close': round(result['c'], 2),
                            'volume': result['v']
                        })
                    
                    return JsonResponse({
                        'weekly': formatted_data,
                        'symbol': symbol.upper(),
                        'count': len(formatted_data)
                    })
                else:
                    return JsonResponse({
                        'error': f'No data found for {symbol}. Please check the symbol.',
                        'symbol': symbol
                    }, status=404)
            else:
                return JsonResponse({
                    'error': 'Failed to fetch data from Polygon API',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch weekly crypto data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def polygon_crypto_monthly_api(request):
    """Get monthly crypto data for the past 2 years using Polygon API"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required (e.g., BTC, ETH, ADA)'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'Polygon API key not configured'}, status=500)
        
        try:
            formatted_symbol = f"X:{symbol.upper()}USD"
            
            # Get data for last 2 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/month/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'apikey': POLYGON_API_KEY,
                'adjusted': 'true',
                'sort': 'asc'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    formatted_data = []
                    for result in data['results']:
                        formatted_data.append({
                            'date': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d'),
                            'open': round(result['o'], 2),
                            'high': round(result['h'], 2),
                            'low': round(result['l'], 2),
                            'close': round(result['c'], 2),
                            'volume': result['v']
                        })
                    
                    return JsonResponse({
                        'monthly': formatted_data,
                        'symbol': symbol.upper(),
                        'count': len(formatted_data)
                    })
                else:
                    return JsonResponse({
                        'error': f'No data found for {symbol}. Please check the symbol.',
                        'symbol': symbol
                    }, status=404)
            else:
                return JsonResponse({
                    'error': 'Failed to fetch data from Polygon API',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch monthly crypto data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def polygon_crypto_price_change_api(request):
    """Get crypto price change analysis using Polygon API"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required (e.g., BTC, ETH, ADA)'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'Polygon API key not configured'}, status=500)
        
        try:
            formatted_symbol = f"X:{symbol.upper()}USD"
            
            # Get last 7 days of data to ensure we have recent trading data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'apikey': POLYGON_API_KEY,
                'adjusted': 'true',
                'sort': 'asc'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results') and len(data['results']) >= 2:
                    results = data['results']
                    latest = results[-1]
                    previous = results[-2]
                    
                    latest_price = latest['c']
                    previous_price = previous['c']
                    latest_date = datetime.fromtimestamp(latest['t'] / 1000).strftime('%Y-%m-%d')
                    previous_date = datetime.fromtimestamp(previous['t'] / 1000).strftime('%Y-%m-%d')
                    
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
                        'error': f'Insufficient data for price change analysis for {symbol}',
                        'symbol': symbol
                    }, status=404)
            else:
                return JsonResponse({
                    'error': 'Failed to fetch data from Polygon API',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to analyze crypto price change: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def polygon_crypto_real_time_api(request):
    """Get real-time crypto price using Polygon API"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required (e.g., BTC, ETH, ADA)'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'Polygon API key not configured'}, status=500)
        
        try:
            formatted_symbol = f"X:{symbol.upper()}USD"
            
            # Get latest aggregated data (previous close)
            url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/prev"
            params = {'apikey': POLYGON_API_KEY}
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    
                    return JsonResponse({
                        'symbol': symbol.upper(),
                        'price': round(result['c'], 2),
                        'open': round(result['o'], 2),
                        'high': round(result['h'], 2),
                        'low': round(result['l'], 2),
                        'volume': result['v'],
                        'date': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d'),
                        'timestamp': result['t']
                    })
                else:
                    return JsonResponse({
                        'error': f'No real-time data found for {symbol}',
                        'symbol': symbol
                    }, status=404)
            else:
                return JsonResponse({
                    'error': 'Failed to fetch real-time data from Polygon API',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch real-time crypto data: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400) 
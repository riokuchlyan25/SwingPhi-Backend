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
    """Get simplified daily crypto data"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            symbol_upper = symbol.upper()
            possible_symbols = [f"X:{symbol_upper}USD", f"{symbol_upper}USD", symbol_upper]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            for formatted_symbol in possible_symbols:
                try:
                    url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    params = {'apikey': POLYGON_API_KEY, 'limit': 30}
                    
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('status') == 'OK' and data.get('results'):
                            # Simplified data - only valid entries
                            simplified_data = []
                            for result in data['results']:
                                if all(key in result for key in ['t', 'o', 'h', 'l', 'c', 'v']):
                                    if all(result[key] > 0 for key in ['o', 'h', 'l', 'c', 'v']):
                                        simplified_data.append({
                                            'date': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d'),
                                            'open': round(result['o'], 2),
                                            'high': round(result['h'], 2),
                                            'low': round(result['l'], 2),
                                            'close': round(result['c'], 2),
                                            'volume': result['v']
                                        })
                            
                            if simplified_data:
                                return JsonResponse({
                                    'symbol': symbol.upper(),
                                    'data': simplified_data
                                })
                
                except requests.RequestException:
                    continue
            
            return JsonResponse({'error': f'No data found for {symbol}'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
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
            symbol_upper = symbol.upper()
            possible_symbols = [
                f"X:{symbol_upper}USD",
                f"{symbol_upper}USD",
                symbol_upper
            ]
            
            # Get data for last year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            for formatted_symbol in possible_symbols:
                try:
                    url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/week/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    params = {
                        'apikey': POLYGON_API_KEY,
                        'adjusted': 'true',
                        'sort': 'asc',
                        'limit': 52  # ~1 year of weeks
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    
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
                                'symbol_format_used': formatted_symbol,
                                'count': len(formatted_data),
                                'status': 'success'
                            })
                
                except requests.RequestException:
                    continue
            
            return JsonResponse({
                'error': f'No data found for {symbol}. Symbol may not be supported.',
                'symbol': symbol,
                'status': 'error'
            }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to fetch weekly crypto data: {str(e)}',
                'symbol': symbol,
                'status': 'error'
            }, status=500)
    
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
            symbol_upper = symbol.upper()
            possible_symbols = [
                f"X:{symbol_upper}USD",
                f"{symbol_upper}USD",
                symbol_upper
            ]
            
            # Get data for last 2 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            
            for formatted_symbol in possible_symbols:
                try:
                    url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/month/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    params = {
                        'apikey': POLYGON_API_KEY,
                        'adjusted': 'true',
                        'sort': 'asc',
                        'limit': 24  # 2 years of months
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    
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
                                'symbol_format_used': formatted_symbol,
                                'count': len(formatted_data),
                                'status': 'success'
                            })
                
                except requests.RequestException:
                    continue
            
            return JsonResponse({
                'error': f'No data found for {symbol}. Symbol may not be supported.',
                'symbol': symbol,
                'status': 'error'
            }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to fetch monthly crypto data: {str(e)}',
                'symbol': symbol,
                'status': 'error'
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

def polygon_crypto_price_change_api(request):
    """Get simplified crypto price change analysis"""
    if request.method == 'POST':
        symbol = get_symbol_from_request(request)
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not POLYGON_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            symbol_upper = symbol.upper()
            possible_symbols = [f"X:{symbol_upper}USD", f"{symbol_upper}USD", symbol_upper]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            for formatted_symbol in possible_symbols:
                try:
                    url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    params = {'apikey': POLYGON_API_KEY, 'sort': 'desc', 'limit': 7}
                    
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('status') == 'OK' and data.get('results') and len(data['results']) >= 2:
                            results = data['results']
                            latest = results[0]
                            previous = results[1]
                            
                            latest_price = latest['c']
                            previous_price = previous['c']
                            
                            if latest_price > 0 and previous_price > 0:
                                price_change = round(latest_price - previous_price, 2)
                                percentage_change = round((price_change / previous_price) * 100, 2)
                                direction = "up" if price_change > 0 else "down" if price_change < 0 else "unchanged"
                                
                                return JsonResponse({
                                    'symbol': symbol.upper(),
                                    'current_price': round(latest_price, 2),
                                    'previous_price': round(previous_price, 2),
                                    'price_change': price_change,
                                    'percentage_change': percentage_change,
                                    'direction': direction
                                })
                
                except requests.RequestException:
                    continue
            
            return JsonResponse({'error': f'No recent data for {symbol}'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
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
            symbol_upper = symbol.upper()
            possible_symbols = [
                f"X:{symbol_upper}USD",
                f"{symbol_upper}USD",
                symbol_upper
            ]
            
            # Try to get the most recent day's data (real-time equivalent)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            for formatted_symbol in possible_symbols:
                try:
                    # First try the ticker details endpoint for more recent data
                    ticker_url = f"https://api.polygon.io/v2/last/trade/{formatted_symbol}"
                    ticker_params = {'apikey': POLYGON_API_KEY}
                    
                    ticker_response = requests.get(ticker_url, params=ticker_params, timeout=15)
                    
                    if ticker_response.status_code == 200:
                        ticker_data = ticker_response.json()
                        
                        if ticker_data.get('status') == 'OK' and ticker_data.get('results'):
                            result = ticker_data['results']
                            
                            return JsonResponse({
                                'symbol': symbol.upper(),
                                'current_price': round(result.get('p', 0), 2),  # price
                                'size': result.get('s', 0),  # size
                                'timestamp': datetime.fromtimestamp(result.get('t', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if result.get('t') else 'N/A',
                                'exchange': result.get('x', 'N/A'),
                                'symbol_format_used': formatted_symbol,
                                'data_type': 'last_trade',
                                'status': 'success'
                            })
                    
                    # Fallback to aggregates if ticker endpoint doesn't work
                    agg_url = f"https://api.polygon.io/v2/aggs/ticker/{formatted_symbol}/range/1/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    agg_params = {
                        'apikey': POLYGON_API_KEY,
                        'adjusted': 'true',
                        'sort': 'desc',
                        'limit': 1
                    }
                    
                    agg_response = requests.get(agg_url, params=agg_params, timeout=15)
                    
                    if agg_response.status_code == 200:
                        agg_data = agg_response.json()
                        
                        if agg_data.get('status') == 'OK' and agg_data.get('results'):
                            result = agg_data['results'][0]
                            
                            return JsonResponse({
                                'symbol': symbol.upper(),
                                'current_price': round(result['c'], 2),  # close price
                                'open': round(result['o'], 2),
                                'high': round(result['h'], 2),
                                'low': round(result['l'], 2),
                                'volume': result['v'],
                                'timestamp': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                                'symbol_format_used': formatted_symbol,
                                'data_type': 'minute_aggregate',
                                'status': 'success'
                            })
                
                except requests.RequestException:
                    continue
            
            return JsonResponse({
                'error': f'No real-time data found for {symbol}. Symbol may not be supported.',
                'symbol': symbol,
                'status': 'error'
            }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to fetch real-time data: {str(e)}',
                'symbol': symbol,
                'status': 'error'
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400) 
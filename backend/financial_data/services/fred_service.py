#internal
from financial_data.config import FRED_API_KEY

# external
import requests

# built-in
from django.http import JsonResponse

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

def fred_yearly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'a')  # annual
        return JsonResponse({'yearly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_monthly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'm')  # monthly
        return JsonResponse({'monthly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_weekly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'w')  # weekly
        return JsonResponse({'weekly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_max_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'd')
        return JsonResponse({'max': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_economic_indicators_api(request):
    """Get key economic indicators (CPI, GDP, Unemployment, etc.)"""
    if request.method == 'POST':
        # Key economic indicators
        indicators = {
            'CPI_All_Urban': 'CPIAUCSL',  # Consumer Price Index for All Urban Consumers
            'CPI_Core': 'CPILFESL',       # Core CPI (less food and energy)
            'Unemployment_Rate': 'UNRATE', # Unemployment Rate
            'GDP': 'GDP',                  # Gross Domestic Product
            'Federal_Funds_Rate': 'FEDFUNDS', # Federal Funds Rate
            'Treasury_10Y': 'DGS10',       # 10-Year Treasury Rate
            'Industrial_Production': 'INDPRO', # Industrial Production Index
            'Consumer_Confidence': 'UMCSENT', # Consumer Sentiment
        }
        
        results = {}
        for name, series_id in indicators.items():
            try:
                data = fetch_fred_data(series_id, 'm')  # Monthly frequency
                # Get latest value if data exists
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'full_data': data[-12:]  # Last 12 months
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'economic_indicators': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_market_events_api(request):
    """Get data related to market events and economic releases"""
    if request.method == 'POST':
        # Market event related indicators
        market_indicators = {
            'VIX': 'VIXCLS',              # VIX Volatility Index
            'SP500': 'SP500',             # S&P 500 Index
            'Dollar_Index': 'DTWEXBGS',   # Trade Weighted US Dollar Index
            'Gold_Price': 'GOLDAMGBD228NLBM', # Gold Price
            'Oil_Price': 'DCOILWTICO',    # WTI Crude Oil Price
            'Treasury_Yield_Spread': 'T10Y2Y', # 10-Year Treasury Constant Maturity Minus 2-Year
            'Credit_Spread': 'BAMLH0A0HYM2', # High Yield Corporate Bond Spread
            'Real_GDP_Growth': 'A191RL1Q225SBEA', # Real GDP Growth Rate
        }
        
        results = {}
        for name, series_id in market_indicators.items():
            try:
                # Use daily frequency for market data, monthly for economic data
                frequency = 'd' if name in ['VIX', 'SP500', 'Dollar_Index', 'Gold_Price', 'Oil_Price'] else 'm'
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    # Get recent data (last 30 for daily, last 12 for monthly)
                    recent_count = 30 if frequency == 'd' else 12
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'market_events': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_cpi_detailed_api(request):
    """Get detailed CPI data and inflation metrics"""
    if request.method == 'POST':
        cpi_indicators = {
            'Headline_CPI': 'CPIAUCSL',        # All items CPI
            'Core_CPI': 'CPILFESL',            # Core CPI (less food and energy)
            'Food_CPI': 'CPIUFDSL',            # Food CPI
            'Energy_CPI': 'CPIENGSL',          # Energy CPI
            'Housing_CPI': 'CPIHOSNS',         # Housing CPI
            'Transportation_CPI': 'CPITRNSL',   # Transportation CPI
            'Medical_CPI': 'CPIMEDSL',         # Medical care CPI
            'Recreation_CPI': 'CPIRECSL',      # Recreation CPI
            'Education_CPI': 'CPIEDUSL',       # Education CPI
            'PCE_Price_Index': 'PCEPI',        # Personal Consumption Expenditures Price Index
            'PPI': 'PPIFIS',                   # Producer Price Index
        }
        
        results = {}
        for name, series_id in cpi_indicators.items():
            try:
                data = fetch_fred_data(series_id, 'm')  # Monthly frequency
                
                if data and len(data) >= 2:
                    latest = data[-1]
                    previous = data[-2]
                    
                    # Calculate month-over-month and year-over-year changes
                    current_value = float(latest.get('value', 0)) if latest.get('value') != '.' else None
                    previous_value = float(previous.get('value', 0)) if previous.get('value') != '.' else None
                    
                    mom_change = None
                    yoy_change = None
                    
                    if current_value and previous_value:
                        mom_change = round(((current_value - previous_value) / previous_value) * 100, 2)
                    
                    # Year-over-year calculation (if we have 12+ months of data)
                    if len(data) >= 13:
                        year_ago = data[-13]
                        year_ago_value = float(year_ago.get('value', 0)) if year_ago.get('value') != '.' else None
                        if current_value and year_ago_value:
                            yoy_change = round(((current_value - year_ago_value) / year_ago_value) * 100, 2)
                    
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'month_over_month_change': f"{mom_change}%" if mom_change else 'N/A',
                        'year_over_year_change': f"{yoy_change}%" if yoy_change else 'N/A',
                        'last_12_months': data[-12:]
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'Insufficient data for calculations'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'cpi_detailed': results})
    return JsonResponse({'error': 'POST required'}, status=400)
# internal
from financial_data.services.charles_schwab_service import charles_schwab_api, charles_schwab_callback, charles_schwab_refresh_token
from financial_data.services.fred_service import fred_yearly_api, fred_monthly_api, fred_weekly_api, fred_max_api
from financial_data.services.yfinance_service import yfinance_daily_api, yfinance_weekly_api, yfinance_yearly_api, yfinance_max_api, yfinance_monthly_api

# external

# built-in
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def fred_yearly_view(request):
    return fred_yearly_api(request)

@csrf_exempt
def fred_monthly_view(request):
    return fred_monthly_api(request)

@csrf_exempt
def fred_weekly_view(request):
    return fred_weekly_api(request)

@csrf_exempt
def fred_max_view(request):
    return fred_max_api(request)

@csrf_exempt
def charles_schwab_view(request):
    return charles_schwab_api(request)

@csrf_exempt
def charles_schwab_callback(request):
    return charles_schwab_callback(request)

@csrf_exempt
def charles_schwab_refresh_token(request):
    return charles_schwab_refresh_token(request)

@csrf_exempt
def yfinance_daily_view(request):
    return yfinance_daily_api(request)

@csrf_exempt
def yfinance_weekly_view(request):
    return yfinance_weekly_api(request)

@csrf_exempt
def yfinance_yearly_view(request):
    return yfinance_yearly_api(request)

@csrf_exempt
def yfinance_max_view(request):
    return yfinance_max_api(request)

@csrf_exempt
def yfinance_monthly_view(request):
    return yfinance_monthly_api(request)

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
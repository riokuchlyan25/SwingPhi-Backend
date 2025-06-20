# internal
from financial_data.services.charles_schwab_service import (
    charles_schwab_api, charles_schwab_callback, charles_schwab_refresh_token, charles_schwab_price_data,
    charles_schwab_daily_api, charles_schwab_weekly_api, charles_schwab_monthly_api,
    charles_schwab_yearly_api, charles_schwab_max_api, charles_schwab_price_change_api
)
from financial_data.services.fred_service import (
    fred_yearly_api, fred_monthly_api, fred_weekly_api, fred_max_api,
    fred_economic_indicators_api, fred_market_events_api, fred_cpi_detailed_api,
    fred_money_banking_api, fred_employment_labor_api, fred_price_commodities_api,
    fred_international_data_api, fred_national_accounts_api, fred_academic_research_api,
    fred_housing_real_estate_api, fred_manufacturing_industrial_api,
    fred_healthcare_indexes_api, fred_education_productivity_api, fred_trade_transportation_api,
    fred_income_demographics_api, fred_cryptocurrency_fintech_api, fred_historical_academic_api,
    fred_sector_specific_api
)
from financial_data.services.yfinance_service import yfinance_daily_api, yfinance_weekly_api, yfinance_yearly_api, yfinance_max_api, yfinance_monthly_api, yfinance_price_change_api
from financial_data.services.polygon_service import (
    polygon_crypto_daily_api, polygon_crypto_weekly_api, polygon_crypto_monthly_api,
    polygon_crypto_price_change_api, polygon_crypto_real_time_api
)

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
def fred_economic_indicators_view(request):
    return fred_economic_indicators_api(request)

@csrf_exempt
def fred_market_events_view(request):
    return fred_market_events_api(request)

@csrf_exempt
def fred_cpi_detailed_view(request):
    return fred_cpi_detailed_api(request)

@csrf_exempt
def fred_money_banking_view(request):
    return fred_money_banking_api(request)

@csrf_exempt
def fred_employment_labor_view(request):
    return fred_employment_labor_api(request)

@csrf_exempt
def fred_price_commodities_view(request):
    return fred_price_commodities_api(request)

@csrf_exempt
def fred_international_data_view(request):
    return fred_international_data_api(request)

@csrf_exempt
def fred_national_accounts_view(request):
    return fred_national_accounts_api(request)

@csrf_exempt
def fred_academic_research_view(request):
    return fred_academic_research_api(request)

@csrf_exempt
def fred_housing_real_estate_view(request):
    return fred_housing_real_estate_api(request)

@csrf_exempt
def fred_manufacturing_industrial_view(request):
    return fred_manufacturing_industrial_api(request)

@csrf_exempt
def fred_healthcare_indexes_view(request):
    return fred_healthcare_indexes_api(request)

@csrf_exempt
def fred_education_productivity_view(request):
    return fred_education_productivity_api(request)

@csrf_exempt
def fred_trade_transportation_view(request):
    return fred_trade_transportation_api(request)

@csrf_exempt
def fred_income_demographics_view(request):
    return fred_income_demographics_api(request)

@csrf_exempt
def fred_cryptocurrency_fintech_view(request):
    return fred_cryptocurrency_fintech_api(request)

@csrf_exempt
def fred_historical_academic_view(request):
    return fred_historical_academic_api(request)

@csrf_exempt
def fred_sector_specific_view(request):
    return fred_sector_specific_api(request)

@csrf_exempt
def charles_schwab_view(request):
    return charles_schwab_api(request)

@csrf_exempt
def charles_schwab_callback_view(request):
    return charles_schwab_callback(request)

@csrf_exempt
def charles_schwab_refresh_token_view(request):
    return charles_schwab_refresh_token(request)

@csrf_exempt
def charles_schwab_price_view(request):
    return charles_schwab_price_data(request)

@csrf_exempt
def charles_schwab_daily_view(request):
    return charles_schwab_daily_api(request)

@csrf_exempt
def charles_schwab_weekly_view(request):
    return charles_schwab_weekly_api(request)

@csrf_exempt
def charles_schwab_monthly_view(request):
    return charles_schwab_monthly_api(request)

@csrf_exempt
def charles_schwab_yearly_view(request):
    return charles_schwab_yearly_api(request)

@csrf_exempt
def charles_schwab_max_view(request):
    return charles_schwab_max_api(request)

@csrf_exempt
def charles_schwab_price_change_view(request):
    return charles_schwab_price_change_api(request)

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

@csrf_exempt
def yfinance_price_change_view(request):
    return yfinance_price_change_api(request)

@csrf_exempt
def polygon_crypto_daily_view(request):
    return polygon_crypto_daily_api(request)

@csrf_exempt
def polygon_crypto_weekly_view(request):
    return polygon_crypto_weekly_api(request)

@csrf_exempt
def polygon_crypto_monthly_view(request):
    return polygon_crypto_monthly_api(request)

@csrf_exempt
def polygon_crypto_price_change_view(request):
    return polygon_crypto_price_change_api(request)

@csrf_exempt
def polygon_crypto_real_time_view(request):
    return polygon_crypto_real_time_api(request)

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

def charles_schwab_price_template(request):
    """Render Charles Schwab price data testing template"""
    return render(request, 'financial_data/charles_schwab_price.html')

def fred_yearly_template(request):
    """Render FRED yearly testing template"""
    return render(request, 'financial_data/fred_yearly.html')

def fred_monthly_template(request):
    """Render FRED monthly testing template"""
    return render(request, 'financial_data/fred_monthly.html')

def fred_weekly_template(request):
    """Render FRED weekly testing template"""
    return render(request, 'financial_data/fred_weekly.html')

def fred_max_template(request):
    """Render FRED max testing template"""
    return render(request, 'financial_data/fred_max.html')

def yfinance_price_change_template(request):
    """Render YFinance price change testing template"""
    return render(request, 'financial_data/yfinance_price_change.html')

def charles_schwab_daily_template(request):
    """Render Charles Schwab daily testing template"""
    return render(request, 'financial_data/charles_schwab_daily.html')

def charles_schwab_weekly_template(request):
    """Render Charles Schwab weekly testing template"""
    return render(request, 'financial_data/charles_schwab_weekly.html')

def charles_schwab_monthly_template(request):
    """Render Charles Schwab monthly testing template"""
    return render(request, 'financial_data/charles_schwab_monthly.html')

def charles_schwab_yearly_template(request):
    """Render Charles Schwab yearly testing template"""
    return render(request, 'financial_data/charles_schwab_yearly.html')

def charles_schwab_max_template(request):
    """Render Charles Schwab max testing template"""
    return render(request, 'financial_data/charles_schwab_max.html')

def charles_schwab_price_change_template(request):
    """Render Charles Schwab price change testing template"""
    return render(request, 'financial_data/charles_schwab_price_change.html')

def fred_economic_indicators_template(request):
    """Render FRED economic indicators testing template"""
    return render(request, 'financial_data/fred_economic_indicators.html')

def fred_market_events_template(request):
    """Render FRED market events testing template"""
    return render(request, 'financial_data/fred_market_events.html')

def fred_cpi_detailed_template(request):
    """Render FRED detailed CPI testing template"""
    return render(request, 'financial_data/fred_cpi_detailed.html')
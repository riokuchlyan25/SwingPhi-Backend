from django.urls import path
from . import views

urlpatterns = [
    # Phi price routes
    path('price/change_percent/', views.price_change_percent_view, name='price_change_percent'),
    path('price/target/', views.price_target_view, name='price_target'),

    path('fred/yearly/', views.fred_yearly_view, name='fred_yearly'),
    path('fred/monthly/', views.fred_monthly_view, name='fred_monthly'),
    path('fred/weekly/', views.fred_weekly_view, name='fred_weekly'),
    path('fred/max/', views.fred_max_view, name='fred_max'),
    # FRED specialized endpoints
    path('fred/economic_indicators/', views.fred_economic_indicators_view, name='fred_economic_indicators'),
    path('fred/market_events/', views.fred_market_events_view, name='fred_market_events'),
    path('fred/cpi_detailed/', views.fred_cpi_detailed_view, name='fred_cpi_detailed'),
    # FRED comprehensive economic data endpoints
    path('fred/money_banking/', views.fred_money_banking_view, name='fred_money_banking'),
    path('fred/employment_labor/', views.fred_employment_labor_view, name='fred_employment_labor'),
    path('fred/price_commodities/', views.fred_price_commodities_view, name='fred_price_commodities'),
    path('fred/international_data/', views.fred_international_data_view, name='fred_international_data'),
    path('fred/national_accounts/', views.fred_national_accounts_view, name='fred_national_accounts'),
    path('fred/academic_research/', views.fred_academic_research_view, name='fred_academic_research'),
    path('fred/housing_real_estate/', views.fred_housing_real_estate_view, name='fred_housing_real_estate'),
    path('fred/manufacturing_industrial/', views.fred_manufacturing_industrial_view, name='fred_manufacturing_industrial'),
    # FRED additional specialized endpoints
    path('fred/healthcare_indexes/', views.fred_healthcare_indexes_view, name='fred_healthcare_indexes'),
    path('fred/education_productivity/', views.fred_education_productivity_view, name='fred_education_productivity'),
    path('fred/trade_transportation/', views.fred_trade_transportation_view, name='fred_trade_transportation'),
    path('fred/income_demographics/', views.fred_income_demographics_view, name='fred_income_demographics'),
    path('fred/cryptocurrency_fintech/', views.fred_cryptocurrency_fintech_view, name='fred_cryptocurrency_fintech'),
    path('fred/historical_academic/', views.fred_historical_academic_view, name='fred_historical_academic'),
    path('fred/sector_specific/', views.fred_sector_specific_view, name='fred_sector_specific'),
    path('charles_schwab/', views.charles_schwab_view, name='charles_schwab'),
    path('charles_schwab_callback/', views.charles_schwab_callback_view, name='charles_schwab_callback'),
    path('charles_schwab_refresh/', views.charles_schwab_refresh_token_view, name='charles_schwab_refresh'),
    path('charles_schwab_price/', views.charles_schwab_price_view, name='charles_schwab_price'),
    # Charles Schwab stock data endpoints
    path('charles_schwab/daily/', views.charles_schwab_daily_view, name='charles_schwab_daily'),
    path('charles_schwab/weekly/', views.charles_schwab_weekly_view, name='charles_schwab_weekly'),
    path('charles_schwab/monthly/', views.charles_schwab_monthly_view, name='charles_schwab_monthly'),
    path('charles_schwab/yearly/', views.charles_schwab_yearly_view, name='charles_schwab_yearly'),
    path('charles_schwab/max/', views.charles_schwab_max_view, name='charles_schwab_max'),
    path('charles_schwab/price_change/', views.charles_schwab_price_change_view, name='charles_schwab_price_change'),
    # YFinance endpoints for stock data
    path('yfinance/daily/', views.yfinance_daily_view, name='yfinance_daily'),
    path('yfinance/weekly/', views.yfinance_weekly_view, name='yfinance_weekly'),
    path('yfinance/monthly/', views.yfinance_monthly_view, name='yfinance_monthly'),
    path('yfinance/yearly/', views.yfinance_yearly_view, name='yfinance_yearly'),
    path('yfinance/max/', views.yfinance_max_view, name='yfinance_max'),
    path('yfinance/price_change/', views.yfinance_price_change_view, name='yfinance_price_change'),
    # SEC endpoints for filings data
    path('sec/filings/', views.sec_filings_view, name='sec_filings'),
    path('sec/company_facts/', views.sec_company_facts_view, name='sec_company_facts'),
    path('sec/filings_summary/', views.sec_filings_summary_view, name='sec_filings_summary'),
    # Earnings Calendar endpoints using Financial Modeling Prep API
    path('earnings/calendar/', views.earnings_calendar_view, name='earnings_calendar'),
    path('earnings/symbol/', views.earnings_for_symbol_view, name='earnings_for_symbol'),
    path('earnings/upcoming/', views.upcoming_earnings_view, name='upcoming_earnings'),
    # Earnings Insights endpoints for comprehensive analysis
    path('earnings/insights/', views.earnings_insights_view, name='earnings_insights'),
    path('earnings/insights/date/', views.earnings_insights_by_date_view, name='earnings_insights_by_date'),
    path('earnings/insights/comprehensive/', views.comprehensive_earnings_insights_view, name='comprehensive_earnings_insights'),
    path('earnings/correlation/', views.earnings_correlation_view, name='earnings_correlation'),
    path('earnings/correlation/impact/', views.earnings_correlation_impact_view, name='earnings_correlation_impact'),
    # Sector Analysis endpoints
    path('sector/trends/', views.sector_trends_view, name='sector_trends'),
    path('sector/available/', views.available_sectors_view, name='available_sectors'),
    path('sector/correlation/', views.all_sectors_correlation_view, name='all_sectors_correlation'),
    # Stock Correlation Overview endpoint
    path('stock/correlation_overview/', views.stock_correlation_overview_view, name='stock_correlation_overview'),
    # NYSE Stocks endpoints
    path('nyse/stocks/', views.nyse_stocks_view, name='nyse_stocks'),
    path('nyse/correlation/', views.stock_correlation_view, name='stock_correlation'),
] 
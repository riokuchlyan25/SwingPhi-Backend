from django.urls import path

from . import views

urlpatterns = [
    path('fred/yearly/', views.fred_yearly_view, name='fred_yearly'),
    path('fred/monthly/', views.fred_monthly_view, name='fred_monthly'),
    path('fred/weekly/', views.fred_weekly_view, name='fred_weekly'),
    path('fred/max/', views.fred_max_view, name='fred_max'),
    path('charles_schwab/', views.charles_schwab_view, name='charles_schwab'),
    path('charles_schwab_callback/', views.charles_schwab_callback, name='charles_schwab_callback'),
    path('charles_schwab_refresh/', views.charles_schwab_refresh_token, name='charles_schwab_refresh'),
    # YFinance endpoints for stock data
    path('yfinance/daily/', views.yfinance_daily_view, name='yfinance_daily'),
    path('yfinance/weekly/', views.yfinance_weekly_view, name='yfinance_weekly'),
    path('yfinance/monthly/', views.yfinance_monthly_view, name='yfinance_monthly'),
    path('yfinance/yearly/', views.yfinance_yearly_view, name='yfinance_yearly'),
    path('yfinance/max/', views.yfinance_max_view, name='yfinance_max'),
    # Testing template interfaces
    path('test/yfinance/', views.yfinance_template, name='yfinance_template'),
    path('test/fred/', views.fred_template, name='fred_template'),
    path('test/charles_schwab/', views.charles_schwab_template, name='charles_schwab_template'),
] 
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
] 
from django.urls import path

from . import views

urlpatterns = [
    path('fred/yearly/', views.fred_yearly_view, name='fred_yearly'),
    path('fred/monthly/', views.fred_monthly_view, name='fred_monthly'),
    path('fred/weekly/', views.fred_weekly_view, name='fred_weekly'),
    path('fred/max/', views.fred_max_view, name='fred_max'),
] 
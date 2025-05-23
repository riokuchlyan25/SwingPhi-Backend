from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import requests

FRED_API_KEY = 'YOUR_FRED_API_KEY'  # Placeholder key
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

@csrf_exempt
def fred_yearly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'a')  # annual
        return JsonResponse({'yearly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_monthly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'm')  # monthly
        return JsonResponse({'monthly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_weekly_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'w')  # weekly
        return JsonResponse({'weekly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def fred_max_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        # For max, fetch all data (let's use 'd' for daily, which is the most granular)
        data = fetch_fred_data(ticker, 'd')
        return JsonResponse({'max': data})
    return JsonResponse({'error': 'POST required'}, status=400)
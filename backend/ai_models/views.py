# internal
from .config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
from openai import AzureOpenAI
import anthropic
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
import requests
from django.http import JsonResponse

# built-in

# Create your views here.

@csrf_exempt
def openai_view(request):
    if request.method == 'POST':
        user_input = request.body.decode('utf-8')
        try:
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_KEY,
                api_version="2023-05-15",
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": "Give me a short stock analysis of the following stock (ensure the analysis is concise and to the point with no special characters just punctuation and the alphabet. do not list out its metrics but rather give me a 5 sentence paragraph analysis. mention unique and insightful details not just its basic facts such as location, industry, etc. do not use special characters or markdown formatting such as * or _. THE RESPONSE MUST BE IN PLAIN TEXT AND LESS THAN 80 WORDS. do not use an astricks or number sign either): " + user_input}
                ]
            )
            ai_response = response.choices[0].message.content
            return HttpResponse(ai_response, content_type='text/plain')
        except Exception as e:
            return HttpResponse(str(e), content_type='text/plain', status=500)

    return render(request, 'ai_models/openai.html')

def claude_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        claude_api_key = 'YOUR_ANTHROPIC_API_KEY'
        try:
            client = anthropic.Client(api_key=claude_api_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": "Give me a short stock analysis of the following stock (ensure the analysis is concise and to the point with no special characters just punctuation and the alphabet. do not list out its metrics but rather give me a 5 sentence paragraph analysis. mention unique and insightful details not just its basic facts such as location, industry, etc. do not use special characters or markdown formatting such as * or _. THE RESPONSE MUST BE IN PLAIN TEXT AND LESS THAN 130 WORDS. do not use an astricks or number sign either): " + user_input}
                ]
            )
            ai_response = response.content[0].text
            return render(request, 'ai_models/claude.html', {'response': ai_response, 'input': user_input})
        except Exception as e:
            return render(request, 'ai_models/claude.html', {'error': str(e)})
    return render(request, 'ai_models/claude.html')

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

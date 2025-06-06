# internal
from news_data.services.news_service import get_top_headlines

# external

# built-in
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def news_api_view(request):
    if request.method == 'POST':
        # Try to get query from JSON body first
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
        except json.JSONDecodeError:
            # Fall back to form data
            query = request.POST.get('query', '')
        
        if not query:
            return JsonResponse({'error': 'query parameter is required'}, status=400)
            
        return get_top_headlines(query)
    return JsonResponse({'error': 'POST required'}, status=400)

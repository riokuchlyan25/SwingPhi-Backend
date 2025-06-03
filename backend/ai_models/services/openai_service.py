# internal
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
from openai import AzureOpenAI

# built-in
from django.http import JsonResponse
from django.shortcuts import HttpResponse
import json

def openai_api(request):
    """OpenAI API endpoint - POST requests only"""
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                user_input = data.get('user_input', '')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            user_input = request.POST.get('user_input', '') or request.body.decode('utf-8')
        
        if not user_input:
            return JsonResponse({'error': 'No input provided'}, status=400)
        
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
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'response': ai_response,
                    'input': user_input
                })
            else:
                return HttpResponse(ai_response, content_type='text/plain')
                
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'error': str(e)}, status=500)
            else:
                return HttpResponse(str(e), content_type='text/plain', status=500)

    return JsonResponse({'error': 'POST required'}, status=400)

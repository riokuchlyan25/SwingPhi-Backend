from django.shortcuts import render, HttpResponse
from openai import AzureOpenAI
import anthropic
from .config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def home(request):
    return HttpResponse("Hello World")

@csrf_exempt
def openai_view(request):
    if request.method == 'POST':
        # Accept raw string as POST body
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
                    {"role": "user", "content": "Give me a short stock analysis of the following stock (ensure the analysis is concise and to the point with no special characters just punctuation and the alphabet. do not list out its metrics but rather give me a 5 sentence paragraph analysis. mention unique and insightful details not just its basic facts such as location, industry, etc. do not use special characters or markdown formatting such as * or _. THE RESPONSE MUST BE IN PLAIN TEXT AND LESS THAN 130 WORDS. do not use an astricks or number sign either): " + user_input}
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

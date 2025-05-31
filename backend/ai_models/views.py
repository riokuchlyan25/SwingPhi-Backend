# internal
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
from openai import AzureOpenAI
import anthropic
import requests
import uuid

# built-in
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Import the agent functionality
try:
    from .agent import AGENT
    from mlflow.types.agent import ChatAgentMessage
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    AGENT_IMPORT_ERROR = str(e)

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

@csrf_exempt
def claude_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                user_input = data.get('user_input', '')
                use_agent = data.get('use_agent', False)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            user_input = request.POST.get('user_input', '')
            use_agent = request.POST.get('use_agent', 'false').lower() == 'true'
        
        if not user_input:
            return JsonResponse({'error': 'No input provided'}, status=400)
        
        if use_agent and AGENT_AVAILABLE:
            try:
                messages = [
                    ChatAgentMessage(
                        id=str(uuid.uuid4()),
                        role="user", 
                        content=f"Give me a short stock analysis of the following stock (ensure the analysis is concise and to the point with no special characters just punctuation and the alphabet. do not list out its metrics but rather give me a 5 sentence paragraph analysis. mention unique and insightful details not just its basic facts such as location, industry, etc. do not use special characters or markdown formatting such as * or _. THE RESPONSE MUST BE IN PLAIN TEXT AND LESS THAN 130 WORDS. do not use an astricks or number sign either): {user_input}"
                    )
                ]
                
                response = AGENT.predict(messages)
                
                if response.messages and len(response.messages) > 0:
                    ai_response = response.messages[-1].content
                else:
                    ai_response = "No response generated from agent"
                
                return JsonResponse({
                    'response': ai_response,
                    'input': user_input,
                    'agent_used': True
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Agent error: {str(e)}',
                    'agent_used': True
                }, status=500)
        
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
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'response': ai_response,
                    'input': user_input,
                    'agent_used': False
                })
            else:
                return render(request, 'ai_models/claude.html', {
                    'response': ai_response, 
                    'input': user_input,
                    'agent_available': AGENT_AVAILABLE
                })
                
        except Exception as e:
            error_msg = str(e)
            if request.content_type == 'application/json':
                return JsonResponse({
                    'error': error_msg,
                    'agent_used': False
                }, status=500)
            else:
                return render(request, 'ai_models/claude.html', {
                    'error': error_msg,
                    'agent_available': AGENT_AVAILABLE
                })
    
    return render(request, 'ai_models/claude.html', {
        'agent_available': AGENT_AVAILABLE,
        'agent_error': AGENT_IMPORT_ERROR if not AGENT_AVAILABLE else None
    })
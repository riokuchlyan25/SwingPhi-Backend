# internal
from ai_models.config import ANTHROPIC_API_KEY, ANTHROPIC_ENDPOINT

# external
import anthropic
import uuid

# built-in
from django.http import JsonResponse
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

@csrf_exempt
def claude_api(request):
    """Get simplified Claude response"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()
            
            if not prompt:
                return JsonResponse({'error': 'Prompt required'}, status=400)
            
            if not ANTHROPIC_API_KEY:
                return JsonResponse({'error': 'Claude not configured'}, status=500)
            
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return JsonResponse({
                'response': response.content[0].text
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)
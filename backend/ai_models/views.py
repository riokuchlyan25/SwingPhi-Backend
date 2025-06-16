# internal
from ai_models.services.openai_service import openai_api, phi_confidence_api
from ai_models.services.claude_service import claude_api

# external
# built-in
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Import the agent functionality
try:
    from ai_models.services.agent import AGENT
    from mlflow.types.agent import ChatAgentMessage
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    AGENT_IMPORT_ERROR = "Agent functionality not available"

# API Endpoints (POST only)
@csrf_exempt
def openai_view(request):
    return openai_api(request)

@csrf_exempt
def claude_view(request):
    return claude_api(request)

@csrf_exempt
def phi_confidence_view(request):
    return phi_confidence_api(request)

# Template Views (GET requests)
def openai_template(request):
    """Render OpenAI testing template"""
    return render(request, 'ai_models/openai.html')

def claude_template(request):
    """Render Claude testing template"""
    return render(request, 'ai_models/claude.html', {
        'agent_available': AGENT_AVAILABLE,
        'agent_error': AGENT_IMPORT_ERROR if not AGENT_AVAILABLE else None
    })
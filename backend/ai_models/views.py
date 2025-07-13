# internal
from ai_models.services.openai_service import chatgpt_api, phi_confidence_api
from ai_models.services.claude_service import claude_api

# external
# built-in
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
    """OpenAI API view - redirect to simplified endpoint"""
    return chatgpt_api(request)

@csrf_exempt
def claude_view(request):
    """Claude API view - redirect to simplified endpoint"""
    return claude_api(request)

@csrf_exempt
def phi_confidence_view(request):
    """Phi confidence API view - redirect to simplified endpoint"""
    return phi_confidence_api(request)


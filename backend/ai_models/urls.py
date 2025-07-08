from django.urls import path
from .views import openai_view, claude_view, phi_confidence_view
from .services.openai_service import chatgpt_api, phi_confidence_api
from .services.claude_service import claude_api

urlpatterns = [
    # Template views
    path('openai/', openai_view, name='openai'),
    path('claude/', claude_view, name='claude'),
    path('phi_confidence/', phi_confidence_view, name='phi_confidence'),
    
    # API endpoints - simplified
    path('api/chatgpt/', chatgpt_api, name='chatgpt_api'),
    path('api/claude/', claude_api, name='claude_api'),
    path('api/phi_confidence/', phi_confidence_api, name='phi_confidence_api'),
]
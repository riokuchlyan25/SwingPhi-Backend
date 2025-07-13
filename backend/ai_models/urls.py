from django.urls import path
from .views import openai_view, claude_view, phi_confidence_view
from .services.openai_service import (
    chatgpt_api, 
    phi_confidence_api,
    phi_price_targets_api,
    phi_news_impact_api,
    phi_volume_signals_api,
    phi_options_activity_api,
    phi_full_market_analysis_api
)
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
    
    # New Phi Market Analysis API endpoints
    path('api/phi_price_targets/', phi_price_targets_api, name='phi_price_targets_api'),
    path('api/phi_news_impact/', phi_news_impact_api, name='phi_news_impact_api'),
    path('api/phi_volume_signals/', phi_volume_signals_api, name='phi_volume_signals_api'),
    path('api/phi_options_activity/', phi_options_activity_api, name='phi_options_activity_api'),
    path('api/phi_full_market_analysis/', phi_full_market_analysis_api, name='phi_full_market_analysis_api'),
]
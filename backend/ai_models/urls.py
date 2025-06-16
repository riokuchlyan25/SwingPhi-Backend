from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints (POST only)
    path('openai/', views.openai_view, name='openai_view'),
    path('claude/', views.claude_view, name='claude_view'),
    path('phi_confidence/', views.phi_confidence_view, name='phi_confidence_view'),
    
    # Testing template interfaces
    path('test/openai/', views.openai_template, name='openai_template'),
    path('test/claude/', views.claude_template, name='claude_template'),
]
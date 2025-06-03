from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints (POST only)
    path('openai/', views.openai_api, name='openai_api'),
    path('claude/', views.claude_api, name='claude_api'),
    
    # Testing template interfaces
    path('test/openai/', views.openai_template, name='openai_template'),
    path('test/claude/', views.claude_template, name='claude_template'),
]
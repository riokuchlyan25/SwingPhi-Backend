from django.urls import path
from . import views

urlpatterns = [
    path('', views.openai_view, name='openai_view'),
    path('openai/', views.openai_view, name='openai'),
    path('claude/', views.claude_view, name='claude'),
]
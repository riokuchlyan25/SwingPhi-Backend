from django.urls import path

from . import views

urlpatterns = [
    path('headlines/', views.news_api_view, name='news_headlines'),
]
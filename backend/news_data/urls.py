from django.urls import path

from . import views

urlpatterns = [
    path('', views.news_test_index, name='news_test_index'),
    path('headlines/', views.news_api_view, name='news_headlines'),
    path('headlines/template/', views.news_headlines_template, name='news_headlines_template'),
    path('test-dashboard/', views.news_test_dashboard, name='news_test_dashboard'),
]
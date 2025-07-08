from django.urls import path
from .views import news_headlines_view, news_test_dashboard_view, news_test_index_view
from .services.news_service import get_news_headlines_api, get_news_sentiment_api, get_best_articles_for_stock_api, get_financial_news

urlpatterns = [
    # Template views
    path('headlines/', news_headlines_view, name='news_headlines'),
    path('test/dashboard/', news_test_dashboard_view, name='news_test_dashboard'),
    path('test/index/', news_test_index_view, name='news_test_index'),
    
    # API endpoints - simplified
    path('api/headlines/', get_news_headlines_api, name='news_headlines_api'),
    path('api/sentiment/', get_news_sentiment_api, name='news_sentiment_api'),
    path('api/best_articles/', get_best_articles_for_stock_api, name='best_articles_api'),
    path('financial/', get_financial_news, name='financial_news_api'),
]
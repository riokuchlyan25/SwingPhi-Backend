# internal
from news_data.services.news_service import (
    get_news_headlines,
    get_financial_news,
    get_news_headlines_api,
    get_news_sentiment_api
)

# external

# built-in
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def news_api_view(request):
    """
    Handler for news headlines API endpoint
    Delegates all business logic to the service layer
    """
    return get_news_headlines(request)

@csrf_exempt
def financial_news_view(request):
    """
    Handler for financial news API endpoint
    Delegates all business logic to the service layer
    """
    return get_financial_news(request)



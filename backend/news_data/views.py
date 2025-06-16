# internal
from news_data.services.news_service import (
    get_news_headlines,
    get_financial_news,
    get_news_headlines_template_context,
    get_news_test_dashboard_context,
    get_news_test_index_context
)

# external

# built-in
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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

def news_headlines_template(request):
    """
    Handler for news headlines template view
    Delegates context generation to the service layer
    """
    context = get_news_headlines_template_context()
    return render(request, 'news_data/news_headlines.html', context)

def news_test_dashboard(request):
    """
    Handler for news test dashboard view
    Delegates context generation to the service layer
    """
    context = get_news_test_dashboard_context()
    return render(request, 'news_data/news_test_dashboard.html', context)

def news_test_index(request):
    """
    Handler for news test index view
    Delegates context generation to the service layer
    """
    context = get_news_test_index_context()
    return render(request, 'news_data/news_test_index.html', context)

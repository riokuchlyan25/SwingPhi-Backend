# internal
from news_data.config import NEWS_API_KEY

# external
from newsapi import NewsApiClient

# built-in
from django.http import JsonResponse
import json

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def get_news_headlines(request):
    """
    Service function to handle news headlines requests
    Handles request parsing, validation, and API calls
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    # Parse request data
    query = _extract_query_from_request(request)
    
    if not query:
        return JsonResponse({'error': 'query parameter is required'}, status=400)
    
    # Make API call
    try:
        articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=10  # Limit to 10 most relevant articles
        )
        return JsonResponse(articles)
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch news: {str(e)}'}, status=500)

def get_news_headlines_template_context():
    """
    Service function to generate context for news headlines template
    """
    return {
        'title': 'News API Headlines Test',
        'endpoint_url': '/news_data/headlines/',
        'description': 'Test the News API by entering a search query to get top headlines'
    }

def get_news_test_dashboard_context():
    """
    Service function to generate context for news test dashboard
    """
    return {
        'title': 'News API Test Dashboard',
        'headlines_endpoint': '/news_data/headlines/',
        'description': 'Comprehensive testing dashboard for News API functionality'
    }

def get_news_test_index_context():
    """
    Service function to generate context for news test index
    """
    return {
        'title': 'News API Testing Suite',
        'test_pages': [
            {
                'name': 'Basic Headlines Test',
                'url': '/news_data/headlines/template/',
                'description': 'Simple interface for testing news headlines with search queries'
            },
            {
                'name': 'Comprehensive Test Dashboard',
                'url': '/news_data/test-dashboard/',
                'description': 'Advanced testing dashboard with batch testing, analytics, and targeted searches'
            }
        ]
    }

def _extract_query_from_request(request):
    """
    Private helper function to extract query parameter from request
    Handles both JSON and form data
    """
    query = ''
    
    # Try to get query from JSON body first
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
    except json.JSONDecodeError:
        # Fall back to form data
        query = request.POST.get('query', '')
    
    return query.strip()

# Legacy function for backward compatibility
def get_top_headlines(query: str):
    """
    Legacy function for backward compatibility
    Directly calls NewsAPI with query string
    """
    try:
        articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=10
        )
        return JsonResponse(articles)
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch news: {str(e)}'}, status=500)

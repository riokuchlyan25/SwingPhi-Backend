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

def get_financial_news(request):
    """
    Service function to fetch comprehensive financial and market news
    Optimized for Swing Phi platform with financial focus
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        # Parse request data for optional parameters
        data = {}
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}
        
        # Extract parameters with defaults
        ticker = data.get('ticker', '')
        category = data.get('category', 'general')
        page_size = min(data.get('page_size', 20), 100)  # Max 100 articles
        
        # Financial news categories and queries
        financial_queries = {
            'general': 'stock market OR financial news OR economy OR trading OR investment',
            'earnings': 'earnings report OR quarterly earnings OR company earnings',
            'federal_reserve': 'Federal Reserve OR Fed OR interest rates OR monetary policy',
            'markets': 'stock market OR nasdaq OR dow jones OR s&p 500 OR market analysis',
            'crypto': 'cryptocurrency OR bitcoin OR ethereum OR crypto market',
            'commodities': 'oil prices OR gold price OR commodities OR energy market',
            'economic_data': 'GDP OR unemployment OR inflation OR economic indicators',
            'mergers': 'merger OR acquisition OR corporate deal OR buyout'
        }
        
        # Build query based on category and ticker
        if ticker:
            query = f'"{ticker}" AND (stock OR shares OR trading OR earnings OR financial)'
        else:
            query = financial_queries.get(category, financial_queries['general'])
        
        # Fetch news articles
        articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=page_size,
            domains='bloomberg.com,reuters.com,cnbc.com,marketwatch.com,finance.yahoo.com,wsj.com,fool.com'
        )
        
        # Enhanced response with metadata
        response_data = {
            'status': articles.get('status', 'ok'),
            'totalResults': articles.get('totalResults', 0),
            'query_used': query,
            'category': category,
            'ticker': ticker if ticker else None,
            'articles': articles.get('articles', []),
            'metadata': {
                'financial_focus': True,
                'source_domains': 'bloomberg,reuters,cnbc,marketwatch,yahoo_finance,wsj,motley_fool',
                'relevance_sorted': True
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch financial news: {str(e)}'}, status=500)

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

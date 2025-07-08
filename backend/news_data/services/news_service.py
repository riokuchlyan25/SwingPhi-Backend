# internal
from news_data.config import NEWS_API_KEY

# external
from newsapi import NewsApiClient

# built-in
from django.http import JsonResponse
import json
import requests

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
            'category': category,
            'ticker': ticker if ticker else None,
            'total': len(articles.get('articles', [])),
            'articles': articles.get('articles', [])
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

def get_news_headlines_api(request):
    """Get simplified news headlines"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        limit = min(int(request.GET.get('limit', 10)), 50)
        
        if not NEWS_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            # Search query - use symbol if provided, otherwise general market news
            query = f"{symbol} stock market" if symbol else "stock market finance"
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Simplified articles - only valid ones
                simplified_articles = []
                for article in articles:
                    if all([article.get('title'), article.get('publishedAt'), article.get('url')]):
                        simplified_articles.append({
                            'title': article['title'],
                            'published_at': article['publishedAt'][:10],  # Just date
                            'url': article['url']
                        })
                
                return JsonResponse({
                    'symbol': symbol if symbol else 'MARKET',
                    'total': len(simplified_articles),
                    'articles': simplified_articles
                })
            else:
                return JsonResponse({'error': f'News API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_news_sentiment_api(request):
    """Get simplified news sentiment analysis"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not NEWS_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            query = f"{symbol} stock earnings financial"
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Simple sentiment analysis
                positive_words = ['gain', 'rise', 'bull', 'up', 'profit', 'strong', 'beat', 'growth']
                negative_words = ['fall', 'drop', 'bear', 'down', 'loss', 'weak', 'miss', 'decline']
                
                positive_count = 0
                negative_count = 0
                
                for article in articles[:10]:  # Analyze first 10 articles
                    title = article.get('title', '').lower()
                    if any(word in title for word in positive_words):
                        positive_count += 1
                    elif any(word in title for word in negative_words):
                        negative_count += 1
                
                # Determine sentiment
                if positive_count > negative_count:
                    sentiment = 'positive'
                elif negative_count > positive_count:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                return JsonResponse({
                    'symbol': symbol,
                    'sentiment': sentiment,
                    'positive_count': positive_count,
                    'negative_count': negative_count
                })
            else:
                return JsonResponse({'error': f'News API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_best_articles_for_stock_api(request):
    """Get the best two articles for a stock using News API and OpenAI API based on highest interaction"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not NEWS_API_KEY:
            return JsonResponse({'error': 'News API key not configured'}, status=500)
        
        try:
            # Get comprehensive news data for the stock
            query = f'"{symbol}" AND (stock OR earnings OR financial OR investment OR revenue OR profit)'
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'popularity',  # Sort by engagement/popularity
                'pageSize': 20,  # Get more articles to analyze
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    return JsonResponse({
                        'symbol': symbol,
                        'message': 'No articles found for this stock',
                        'best_articles': []
                    })
                
                # Score articles based on interaction indicators
                scored_articles = []
                
                for article in articles:
                    if not all([article.get('title'), article.get('url'), article.get('publishedAt')]):
                        continue
                    
                    # Calculate interaction score based on various factors
                    interaction_score = 0
                    
                    # Source credibility score
                    source_name = article.get('source', {}).get('name', '').lower()
                    if any(source in source_name for source in ['bloomberg', 'reuters', 'cnbc', 'wsj']):
                        interaction_score += 30
                    elif any(source in source_name for source in ['yahoo', 'marketwatch', 'fool']):
                        interaction_score += 20
                    else:
                        interaction_score += 10
                    
                    # Title engagement indicators
                    title = article.get('title', '').lower()
                    engagement_keywords = ['breaking', 'exclusive', 'analysis', 'earnings', 'beats', 'misses', 'surge', 'plunge', 'report']
                    interaction_score += sum(5 for keyword in engagement_keywords if keyword in title)
                    
                    # Description relevance
                    description = article.get('description', '').lower()
                    if symbol.lower() in description:
                        interaction_score += 15
                    
                    # Time recency bonus (more recent = higher interaction potential)
                    from datetime import datetime
                    try:
                        pub_date = datetime.strptime(article['publishedAt'][:10], '%Y-%m-%d')
                        days_ago = (datetime.now() - pub_date).days
                        if days_ago <= 1:
                            interaction_score += 20
                        elif days_ago <= 3:
                            interaction_score += 15
                        elif days_ago <= 7:
                            interaction_score += 10
                    except:
                        pass
                    
                    scored_articles.append({
                        'article': article,
                        'interaction_score': interaction_score
                    })
                
                # Sort by interaction score and get top 2
                scored_articles.sort(key=lambda x: x['interaction_score'], reverse=True)
                best_articles = scored_articles[:2]
                
                # Use OpenAI to analyze and rank the best articles
                try:
                    from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
                    from openai import AzureOpenAI
                    
                    if all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                        client = AzureOpenAI(
                            api_key=AZURE_OPENAI_KEY,
                            api_version="2023-05-15",
                            azure_endpoint=AZURE_OPENAI_ENDPOINT
                        )
                        
                        # Analyze each article for relevance and quality
                        enhanced_articles = []
                        
                        for idx, scored_article in enumerate(best_articles):
                            article = scored_article['article']
                            
                            # Create AI analysis prompt
                            prompt = f"""Analyze this article about {symbol} and provide a brief 1-sentence summary of why it's valuable for investors. Focus on key financial insights, earnings impact, or market significance.

Article Title: {article.get('title', '')}
Article Description: {article.get('description', '')}

Provide only the summary, no additional text."""
                            
                            try:
                                ai_response = client.chat.completions.create(
                                    model=MODEL_NAME,
                                    messages=[{"role": "user", "content": prompt}]
                                )
                                
                                ai_summary = ai_response.choices[0].message.content.strip()
                            except:
                                ai_summary = "AI analysis unavailable"
                            
                            enhanced_articles.append({
                                'rank': idx + 1,
                                'title': article.get('title'),
                                'description': article.get('description'),
                                'url': article.get('url'),
                                'source': article.get('source', {}).get('name'),
                                'published_at': article.get('publishedAt')[:10],
                                'interaction_score': scored_article['interaction_score'],
                                'ai_summary': ai_summary
                            })
                        
                        # Create simplified articles list
                        simple_articles = []
                        for idx, scored_article in enumerate(best_articles):
                            article = scored_article['article']
                            ai_summary = enhanced_articles[idx]['ai_summary'] if idx < len(enhanced_articles) else 'Analysis unavailable'
                            
                            simple_articles.append({
                                'title': article.get('title'),
                                'url': article.get('url'),
                                'source': article.get('source', {}).get('name'),
                                'date': article.get('publishedAt')[:10],
                                'summary': ai_summary
                            })
                        
                        return JsonResponse({
                            'symbol': symbol,
                            'articles': simple_articles
                        })
                    
                    else:
                        # Fallback without AI analysis
                        simple_articles = []
                        for scored_article in best_articles:
                            article = scored_article['article']
                            simple_articles.append({
                                'title': article.get('title'),
                                'url': article.get('url'),
                                'source': article.get('source', {}).get('name'),
                                'date': article.get('publishedAt')[:10]
                            })
                        
                        return JsonResponse({
                            'symbol': symbol,
                            'articles': simple_articles
                        })
                        
                except Exception as ai_error:
                    return JsonResponse({
                        'error': f'AI analysis failed: {str(ai_error)}',
                        'symbol': symbol
                    }, status=500)
                    
            else:
                return JsonResponse({'error': f'News API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

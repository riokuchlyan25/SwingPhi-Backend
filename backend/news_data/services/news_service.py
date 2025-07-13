# internal
from news_data.config import NEWS_API_KEY

# external
from newsapi import NewsApiClient

# built-in
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from datetime import datetime

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

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
def get_best_articles_for_stock_api(request):
    """Get the best two articles for a stock using FMP API and OpenAI API for enhanced financial analysis"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        # Import FMP API key
        from financial_data.config import FMP_API_KEY
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'FMP API key not configured'}, status=500)
        
        try:
            # Get financial news data from FMP API
            articles = []
            
            # 1. Get general stock news from FMP
            stock_news_url = f"https://financialmodelingprep.com/api/v3/stock_news"
            stock_news_params = {
                'tickers': symbol,
                'limit': 15,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(stock_news_url, params=stock_news_params, timeout=30)
            
            if response.status_code == 200:
                stock_news_data = response.json()
                if isinstance(stock_news_data, list):
                    articles.extend(stock_news_data)
            
            # 2. Get more general news for broader coverage
            general_news_url = f"https://financialmodelingprep.com/api/v4/general_news"
            general_params = {
                'page': 0,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(general_news_url, params=general_params, timeout=30)
            
            if response.status_code == 200:
                general_data = response.json()
                if isinstance(general_data, list):
                    # Filter for articles mentioning the symbol
                    for article in general_data[:20]:  # Check first 20 articles
                        if (article.get('title') and 
                            article.get('publishedDate') and 
                            (symbol.lower() in article.get('title', '').lower() or 
                             symbol.lower() in article.get('text', '').lower())):
                            articles.append(article)
            
            # 3. Get company-specific press releases for high-quality content
            press_releases_url = f"https://financialmodelingprep.com/api/v4/press-releases"
            press_params = {
                'symbol': symbol,
                'page': 0,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(press_releases_url, params=press_params, timeout=30)
            
            if response.status_code == 200:
                press_data = response.json()
                if isinstance(press_data, list):
                    # Add press releases with proper format
                    for press in press_data[:5]:  # Limit to 5 press releases
                        if press.get('title') and press.get('date'):
                            # Convert press release format to match article format
                            press_article = {
                                'symbol': symbol,
                                'publishedDate': press.get('date'),
                                'title': press.get('title'),
                                'url': press.get('url', ''),
                                'text': press.get('text', ''),
                                'site': 'Official Press Release'
                            }
                            articles.append(press_article)
            
            if not articles:
                return JsonResponse({
                    'symbol': symbol,
                    'message': 'No financial articles found for this stock',
                    'articles': []
                })
            
            # Score articles based on financial relevance and quality
            scored_articles = []
            
            for article in articles:
                if not article.get('title'):
                    continue
                
                # Calculate relevance score for financial content
                relevance_score = 0
                
                # Source credibility - FMP data is generally high quality
                source = article.get('site', '').lower()
                if 'earnings call' in source or 'press release' in source:
                    relevance_score += 50  # Official company communications
                elif any(source_name in source for source_name in ['reuters', 'bloomberg', 'cnbc', 'wsj', 'marketwatch']):
                    relevance_score += 40
                elif 'yahoo' in source or 'fool' in source:
                    relevance_score += 30
                else:
                    relevance_score += 20
                
                # Title financial relevance
                title = article.get('title', '').lower()
                financial_keywords = [
                    'earnings', 'revenue', 'profit', 'financial', 'quarterly', 'annual',
                    'beats', 'misses', 'guidance', 'outlook', 'results', 'performance',
                    'acquisition', 'merger', 'ipo', 'dividend', 'split', 'buyback'
                ]
                relevance_score += sum(8 for keyword in financial_keywords if keyword in title)
                
                # Symbol mention bonus
                if symbol.lower() in title:
                    relevance_score += 25
                
                # Content relevance (if available)
                content = article.get('text', '').lower()
                if content and symbol.lower() in content:
                    relevance_score += 15
                
                # Time recency bonus
                try:
                    pub_date_str = article.get('publishedDate', '')
                    if pub_date_str:
                        # Handle different date formats from FMP
                        pub_date = None
                        for date_format in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                pub_date = datetime.strptime(pub_date_str[:19], date_format)
                                break
                            except:
                                continue
                        
                        if pub_date:
                            days_ago = (datetime.now() - pub_date).days
                            if days_ago <= 1:
                                relevance_score += 30
                            elif days_ago <= 3:
                                relevance_score += 25
                            elif days_ago <= 7:
                                relevance_score += 20
                            elif days_ago <= 30:
                                relevance_score += 10
                except:
                    pass
                
                scored_articles.append({
                    'article': article,
                    'relevance_score': relevance_score
                })
            
            # Sort by relevance score and get top 2
            scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            best_articles = scored_articles[:2]
            
            # Use OpenAI to analyze and enhance the articles
            try:
                from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
                from openai import AzureOpenAI
                
                if all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                    client = AzureOpenAI(
                        api_key=AZURE_OPENAI_KEY,
                        api_version="2023-05-15",
                        azure_endpoint=AZURE_OPENAI_ENDPOINT
                    )
                    
                    # Analyze each article for investment insights
                    enhanced_articles = []
                    
                    for idx, scored_article in enumerate(best_articles):
                        article = scored_article['article']
                        
                        # Create AI analysis prompt focused on financial insights
                        article_text = article.get('text', article.get('title', ''))[:500]  # Limit text length
                        prompt = f"""Analyze this financial article about {symbol} and provide a concise investment insight in 1-2 sentences. Focus on:
- Key financial metrics or performance indicators
- Market impact or investor implications
- Earnings, revenue, or business developments

Article Title: {article.get('title', '')}
Content: {article_text}

Provide only the investment insight, be specific and actionable."""
                        
                        try:
                            ai_response = client.chat.completions.create(
                                model=MODEL_NAME,
                                messages=[{
                                    "role": "system", 
                                    "content": "You are a financial analyst providing concise investment insights."
                                }, {
                                    "role": "user", 
                                    "content": prompt
                                }],
                                temperature=0.3
                            )
                            
                            ai_insight = ai_response.choices[0].message.content.strip()
                        except:
                            ai_insight = "Investment analysis unavailable"
                        
                        # Format the enhanced article
                        enhanced_articles.append({
                            'title': article.get('title'),
                            'url': article.get('url', ''),
                            'source': article.get('site', 'FMP Financial Data'),
                            'date': article.get('publishedDate', '')[:10] if article.get('publishedDate') else '',
                            'investment_insight': ai_insight,
                            'relevance_score': scored_article['relevance_score']
                        })
                    
                    return JsonResponse({
                        'symbol': symbol,
                        'articles': enhanced_articles,
                        'data_source': 'Financial Modeling Prep API',
                        'total_articles_analyzed': len(articles)
                    })
                
                else:
                    # Fallback without AI analysis
                    simple_articles = []
                    for scored_article in best_articles:
                        article = scored_article['article']
                        simple_articles.append({
                            'title': article.get('title'),
                            'url': article.get('url', ''),
                            'source': article.get('site', 'FMP Financial Data'),
                            'date': article.get('publishedDate', '')[:10] if article.get('publishedDate') else '',
                            'relevance_score': scored_article['relevance_score']
                        })
                    
                    return JsonResponse({
                        'symbol': symbol,
                        'articles': simple_articles,
                        'data_source': 'Financial Modeling Prep API',
                        'note': 'AI analysis unavailable'
                    })
                    
            except Exception as ai_error:
                return JsonResponse({
                    'error': f'AI analysis failed: {str(ai_error)}',
                    'symbol': symbol,
                    'data_source': 'Financial Modeling Prep API'
                }, status=500)
                
        except requests.exceptions.Timeout:
            return JsonResponse({'error': 'Request timeout - FMP API response too slow'}, status=408)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'FMP API request failed: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)

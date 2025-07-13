# internal
from financial_data.config import FMP_API_KEY
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
import requests
from django.http import JsonResponse
import json
from openai import AzureOpenAI

# Comprehensive sector mappings with representative stocks
SECTOR_STOCKS = {
    # Original sectors
    'technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA'],
    'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'MRK'],
    'financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
    'consumer_discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
    'consumer_staples': ['PG', 'KO', 'PEP', 'WMT', 'COST'],
    'industrials': ['BA', 'CAT', 'GE', 'HON', 'MMM'],
    'utilities': ['NEE', 'DUK', 'SO', 'D', 'EXC'],
    'materials': ['LIN', 'APD', 'ECL', 'SHW', 'FCX'],
    'real_estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'WELL'],
    'communication_services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA'],
    'aerospace_defense': ['BA', 'LMT', 'RTX', 'NOC', 'GD'],
    'automotive': ['TSLA', 'GM', 'F', 'RIVN', 'LCID'],
    'biotech': ['GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX'],
    'semiconductors': ['NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO'],
    'software': ['MSFT', 'CRM', 'ADBE', 'ORCL', 'NOW'],
    'cybersecurity': ['CRWD', 'ZS', 'PANW', 'OKTA', 'FTNT'],
    'cloud_computing': ['AMZN', 'MSFT', 'GOOGL', 'CRM', 'SNOW'],
    'renewable_energy': ['ENPH', 'SEDG', 'FSLR', 'NEE', 'ICLN'],
    'banking': ['JPM', 'BAC', 'WFC', 'C', 'USB'],
    'insurance': ['BRK-B', 'PGR', 'TRV', 'AIG', 'MET'],
    'retail': ['WMT', 'AMZN', 'COST', 'TGT', 'HD'],
    'hospitality': ['MAR', 'HLT', 'IHG', 'H', 'DIS'],
    'transportation': ['UPS', 'FDX', 'UNP', 'CSX', 'DAL'],
    'telecommunications': ['VZ', 'T', 'TMUS', 'CHTR', 'CMCSA'],
    'entertainment': ['DIS', 'NFLX', 'WBD', 'PARA', 'SONY'],
    
    # New granular sector classifications
    'technology_services': ['CRM', 'SNOW', 'PLTR', 'DDOG', 'MDB'],
    'electronic_technology': ['AAPL', 'HPQ', 'DELL', 'IBM', 'CSCO'],
    'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'health_technology': ['MDT', 'ABT', 'TMO', 'DHR', 'BSX'],
    'retail_trade': ['WMT', 'AMZN', 'TGT', 'COST', 'LOW'],
    'consumer_non_durables': ['PG', 'KO', 'PEP', 'UL', 'CL'],
    'energy_minerals': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
    'consumer_services': ['DIS', 'SBUX', 'MCD', 'CMG', 'YUM'],
    'producer_manufacturing': ['CAT', 'GE', 'MMM', 'HON', 'EMR'],
    'consumer_durables': ['GM', 'F', 'WHR', 'NVR', 'PHM'],
    'utilities_granular': ['NEE', 'DUK', 'SO', 'D', 'EXC'],
    'industrial_services': ['UPS', 'FDX', 'WM', 'RSG', 'URI'],
    'non_energy_minerals': ['NEM', 'FCX', 'AA', 'X', 'CLF'],
    'transportation_granular': ['DAL', 'UNP', 'CSX', 'AAL', 'UAL'],
    'process_industries': ['DOW', 'LYB', 'DD', 'LIN', 'APD'],
    'communications': ['VZ', 'T', 'CMCSA', 'CHTR', 'DISH'],
    'commercial_services': ['ADP', 'PAYX', 'FIS', 'V', 'MA'],
    'health_services': ['UNH', 'CVS', 'CI', 'ANTM', 'HUM'],
    'distribution_services': ['UPS', 'FDX', 'XPO', 'CHRW', 'EXPD'],
    'miscellaneous': ['BRK-B', 'BRK-A', 'MNST', 'COST', 'WMT']
}

def get_sector_trends_api(request):
    """Analyze sector trends using FMP news and OpenAI - returns sentiment and trend sentence"""
    if request.method == 'GET':
        sector = request.GET.get('sector', '').lower().strip()
        
        if not sector:
            return JsonResponse({
                'error': 'Sector parameter required',
                'available_sectors': list(SECTOR_STOCKS.keys())
            }, status=400)
        
        if sector not in SECTOR_STOCKS:
            return JsonResponse({
                'error': f'Sector "{sector}" not supported',
                'available_sectors': list(SECTOR_STOCKS.keys())
            }, status=400)
        
        try:
            # Get news articles for sector stocks using FMP API
            news_articles = get_sector_news(sector)
            
            if not news_articles:
                return JsonResponse({
                    'sector': sector,
                    'sentiment': 'neutral',
                    'trend': 'No recent news available for sentiment analysis',
                    'error': 'No news articles found for this sector'
                })
            
            # Analyze sentiment using OpenAI
            sentiment_analysis = analyze_sector_sentiment_with_openai(sector, news_articles)
            
            return JsonResponse({
                'sector': sector,
                'sentiment': sentiment_analysis['sentiment'],
                'trend': sentiment_analysis['trend']
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'sector': sector,
                'sentiment': 'neutral',
                'trend': 'Unable to analyze sector trend due to technical error'
            }, status=500)
    
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)

def get_sector_news(sector):
    """Fetch news articles for sector stocks from FMP API"""
    if not FMP_API_KEY:
        return []
    
    sector_symbols = SECTOR_STOCKS[sector]
    all_articles = []
    
    try:
        # Get stock news for top 3 symbols in the sector to avoid rate limits
        for symbol in sector_symbols[:3]:
            # Get stock-specific news
            stock_news_url = f"https://financialmodelingprep.com/api/v3/stock_news"
            params = {
                'tickers': symbol,
                'limit': 5,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(stock_news_url, params=params, timeout=10)
            
            if response.status_code == 200:
                news_data = response.json()
                if isinstance(news_data, list):
                    all_articles.extend(news_data[:3])  # Limit to 3 articles per stock
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles[:10]  # Return max 10 articles
        
    except Exception:
        return []

def analyze_sector_sentiment_with_openai(sector, news_articles):
    """Use OpenAI to analyze sector sentiment and generate trend sentence"""
    try:
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return {
                'sentiment': 'neutral',
                'trend': 'Unable to analyze sentiment due to configuration issues'
            }
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        # Prepare news summary for analysis
        news_summary = ""
        for i, article in enumerate(news_articles[:5], 1):  # Use top 5 articles
            title = article.get('title', '')
            text = article.get('text', '')[:200]  # First 200 chars of text
            news_summary += f"{i}. {title} - {text}...\n"
        
        sector_name = sector.replace('_', ' ').title()
        
        prompt = f"""
        Analyze the following recent news articles about the {sector_name} sector and provide:
        1. Overall sentiment (positive, negative, or neutral)
        2. A brief 1-sentence trend description
        
        News articles:
        {news_summary}
        
        Please respond in the following JSON format:
        {{
            "sentiment": "positive/negative/neutral",
            "trend": "A single sentence describing the current sector trend"
        }}
        
        Keep the trend sentence under 100 characters and focus on market movements, earnings, or significant developments.
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse OpenAI response
        ai_response = response.choices[0].message.content.strip()
        
        try:
            # Try to parse as JSON
            parsed_response = json.loads(ai_response)
            sentiment = parsed_response.get('sentiment', 'neutral').lower()
            trend = parsed_response.get('trend', f'{sector_name} sector shows mixed signals')
            
            # Validate sentiment
            if sentiment not in ['positive', 'negative', 'neutral']:
                sentiment = 'neutral'
                
            return {
                'sentiment': sentiment,
                'trend': trend
            }
            
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            if 'positive' in ai_response.lower():
                sentiment = 'positive'
            elif 'negative' in ai_response.lower():
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            return {
                'sentiment': sentiment,
                'trend': f'{sector_name} sector shows mixed market signals based on recent news'
            }
            
    except Exception:
        return {
            'sentiment': 'neutral',
            'trend': f'{sector.replace("_", " ").title()} sector analysis unavailable due to technical issues'
        }

def get_available_sectors_api(request):
    """Get list of available sector names only"""
    if request.method == 'GET':
        # Convert sector keys to readable names
        sector_names = [sector.replace('_', ' ').title() for sector in SECTOR_STOCKS.keys()]
        
        return JsonResponse({
            'total_sectors': len(SECTOR_STOCKS),
            'sectors': sector_names,
            'sector_keys': list(SECTOR_STOCKS.keys())  # Include keys for API usage
        })
    else:
        return JsonResponse({'error': 'GET method required'}, status=405) 
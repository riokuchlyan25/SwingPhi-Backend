# internal
from financial_data.config import FMP_API_KEY
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
import requests
from django.http import JsonResponse
import json
from openai import AzureOpenAI
import yfinance as yf
import pandas as pd
import numpy as np

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

def calculate_sector_correlation_matrix():
    """
    Calculate actual mathematical correlations between sector representative stocks
    
    Returns a correlation matrix showing how different sectors correlate with each other
    based on actual price movements over the past 6 months
    """
    try:
        # Select representative stocks for each major sector
        sector_representatives = {
            'technology': 'AAPL',
            'healthcare': 'JNJ', 
            'financial': 'JPM',
            'energy': 'XOM',
            'consumer_discretionary': 'AMZN',
            'consumer_staples': 'PG',
            'industrials': 'BA',
            'utilities': 'NEE',
            'materials': 'LIN',
            'real_estate': 'AMT',
            'communication_services': 'GOOGL',
            'semiconductors': 'NVDA',
            'biotech': 'GILD',
            'automotive': 'TSLA',
            'banking': 'JPM'
        }
        
        # Get price data for all representative stocks
        price_data = {}
        period = "6mo"  # 6 months of data
        
        for sector, ticker in sector_representatives.items():
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period=period, interval="1d")
                
                if not data.empty:
                    # Calculate daily returns (percentage change)
                    returns = data['Close'].pct_change().dropna()
                    price_data[sector] = returns
                    
            except Exception:
                continue  # Skip if data fetch fails
        
        if len(price_data) < 5:  # Need at least 5 sectors for meaningful analysis
            return None
        
        # Create DataFrame from price data
        df = pd.DataFrame(price_data)
        
        # Calculate correlation matrix
        correlation_matrix = df.corr()
        
        # Calculate overall sector correlation score
        # Take the mean of all correlations (excluding diagonal)
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        upper_triangle_correlations = correlation_matrix.where(mask).stack()
        
        # Filter out NaN values and extreme outliers
        valid_correlations = upper_triangle_correlations.dropna()
        valid_correlations = valid_correlations[(valid_correlations >= -1.0) & (valid_correlations <= 1.0)]
        
        if len(valid_correlations) > 0:
            overall_correlation = float(valid_correlations.mean())
            return {
                'overall_correlation': round(max(0.0, min(1.0, overall_correlation)), 3),
                'correlation_matrix': correlation_matrix.round(3).to_dict(),
                'sectors_analyzed': list(price_data.keys()),
                'data_points': len(df),
                'calculation_method': 'pearson_correlation_6mo_returns'
            }
        
        return None
        
    except Exception as e:
        return None

def get_all_sectors_correlation_api(request):
    """Analyze correlation across all sectors using both mathematical calculation and OpenAI analysis"""
    if request.method == 'GET':
        try:
            # Get mathematical correlation calculation
            math_correlation = calculate_sector_correlation_matrix()
            
            # Get all sector information for OpenAI analysis
            all_sectors = list(SECTOR_STOCKS.keys())
            sector_count = len(all_sectors)
            
            # Use OpenAI to analyze correlation patterns across all sectors
            ai_correlation_score = 0.65  # Default fallback
            ai_description = 'Sector correlation analysis completed with mixed signals'
            
            if all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                try:
                    client = AzureOpenAI(
                        api_key=AZURE_OPENAI_KEY,
                        api_version="2023-05-15",
                        azure_endpoint=AZURE_OPENAI_ENDPOINT
                    )
                    
                    # Prepare sector information for analysis
                    sector_names = [sector.replace('_', ' ').title() for sector in all_sectors]
                    sector_summary = f"Analyzing {sector_count} sectors: {', '.join(sector_names)}"
                    
                    # Include mathematical correlation data in prompt if available
                    math_context = ""
                    if math_correlation:
                        math_context = f"\nMathematical correlation analysis shows an overall correlation of {math_correlation['overall_correlation']} based on {math_correlation['data_points']} days of price data across {len(math_correlation['sectors_analyzed'])} major sectors."
                    
                    prompt = f"""
                    Analyze the overall correlation patterns across all {sector_count} market sectors:
                    
                    {sector_summary}
                    {math_context}
                    
                    Consider these factors for sector correlation analysis:
                    1. Economic cycle sensitivity - how sectors move together during economic cycles
                    2. Interest rate sensitivity - sectors that respond similarly to rate changes
                    3. Market sentiment correlation - how sectors react to market-wide events
                    4. Supply chain interdependencies - sectors that depend on each other
                    5. Consumer behavior patterns - sectors affected by similar consumer trends
                    6. Regulatory environments - sectors under similar regulatory pressures
                    7. Technology disruption patterns - sectors being transformed by similar tech trends
                    8. Global economic exposure - sectors with similar international dependencies
                    
                    Based on current market conditions, historical patterns, and the mathematical correlation data provided, provide:
                    1. A numerical correlation score (0.0 to 1.0) representing overall sector correlation
                    2. A concise description (one sentence) explaining the correlation level
                    
                    Correlation ranges:
                    - 0.0-0.3: Low correlation (sectors moving independently)
                    - 0.3-0.6: Moderate correlation (some sectoral alignment)
                    - 0.6-0.8: High correlation (strong sectoral alignment)
                    - 0.8-1.0: Very high correlation (sectors highly synchronized)
                    
                    Respond ONLY with a JSON object in this exact format:
                    {{
                        "sector_correlation": [0.0-1.0 decimal to 2 places],
                        "description": "[one sentence description]"
                    }}
                    """
                    
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "You are a financial market analyst specializing in sector correlation analysis. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    # Try to find JSON in the response (in case there's extra text)
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        ai_response = json_match.group()
                    
                    result = json.loads(ai_response)
                    
                    # Extract and validate results
                    ai_correlation_score = float(result.get('sector_correlation', 0.65))
                    ai_description = result.get('description', 'Sector correlation analysis completed')
                    
                    # Ensure correlation is within 0.0-1.0 range
                    ai_correlation_score = max(0.0, min(1.0, ai_correlation_score))
                    ai_correlation_score = round(ai_correlation_score, 2)
                    
                except Exception:
                    pass  # Use fallback values
            
            # Combine mathematical and AI analysis
            if math_correlation:
                # Weight the mathematical correlation more heavily if available
                combined_correlation = round((math_correlation['overall_correlation'] * 0.7 + ai_correlation_score * 0.3), 2)
                
                response_data = {
                    'sector_correlation': combined_correlation,
                    'description': ai_description,
                    'analysis_details': {
                        'mathematical_correlation': math_correlation['overall_correlation'],
                        'ai_correlation': ai_correlation_score,
                        'combined_method': 'weighted_70_30',
                        'mathematical_analysis': math_correlation,
                        'sectors_count': sector_count
                    }
                }
            else:
                # Use AI analysis only if mathematical calculation failed
                response_data = {
                    'sector_correlation': ai_correlation_score,
                    'description': ai_description,
                    'analysis_details': {
                        'mathematical_correlation': None,
                        'ai_correlation': ai_correlation_score,
                        'combined_method': 'ai_only',
                        'note': 'Mathematical correlation calculation failed, using AI analysis only',
                        'sectors_count': sector_count
                    }
                }
            
            return JsonResponse(response_data)
                
        except Exception as e:
            return JsonResponse({
                'sector_correlation': 0.65,
                'description': 'Moderate correlation observed across market sectors with mixed alignment patterns',
                'analysis_details': {
                    'error': str(e),
                    'method': 'fallback'
                }
            }, status=500)
    
    else:
        return JsonResponse({'error': 'GET method required'}, status=405) 
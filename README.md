# Swing Phi Backend Routes

## Phi Analysis

### Phi market trends using OpenAI/Claude
```bash
curl -X POST "http://localhost:8000/ai_models/openai/" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "AAPL"}'
```

### Phi Confidence Score (0-100) using OpenAI Sentiment Analysis
```bash
curl -X POST "http://localhost:8000/ai_models/phi_confidence/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple stock is performing exceptionally well this quarter with strong earnings growth and positive market sentiment."}'
```

### Full Phi Market Analysis - Comprehensive OpenAI Analysis
```bash
# Get comprehensive analysis combining price targets, news impact, volume signals, and options activity (1-2 sentences each)
curl -X POST "http://localhost:8000/ai_models/api/phi_full_market_analysis/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

## Stock and Crypto Price Data Collection

### Price data for graphs from YFinance (Daily)
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/daily/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### Phi daily snapshot alerts (Price Change)
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/price_change/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### YFinance Weekly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/weekly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### YFinance Monthly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/monthly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### YFinance Yearly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/yearly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### YFinance Maximum Historical Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/yfinance/max/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

## Charles Schwab Routes - not finished access token needed

### Charles Schwab Login Link
```bash
curl -X GET "http://localhost:8000/financial_data/charles_schwab/"
```

### Charles Schwab Daily Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/daily/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

### Charles Schwab Weekly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/weekly/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

### Charles Schwab Monthly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/monthly/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

### Charles Schwab Yearly Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/yearly/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

### Charles Schwab Maximum Historical Stock Data
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/max/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

### Charles Schwab Price Change Analysis
```bash
curl -X POST "http://localhost:8000/financial_data/charles_schwab/price_change/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "access_token": "YOUR_ACCESS_TOKEN"}'
```

## News Data Collection

### Financial News from News API
```bash
curl -X POST "http://localhost:8000/news_data/financial/" \
  -H "Content-Type: application/json" \
  -d '{"category": "markets", "ticker": "AAPL", "page_size": 10}'
```

### Get News Headlines for Stock Symbol
```bash
# Get simplified news headlines for a specific stock or general market news
curl -X GET "http://localhost:8000/news_data/api/headlines/?symbol=AAPL&limit=10"
```

### Get News Sentiment Analysis for Stock
```bash
# Get sentiment analysis (positive/negative/neutral) for a specific stock
curl -X GET "http://localhost:8000/news_data/api/sentiment/?symbol=AAPL"
```

### Get Best Articles for Stock (AI-Powered Analysis)
```bash
# Get the best 2 articles for a stock based on highest interaction and AI analysis
curl -X GET "http://localhost:8000/news_data/api/best_articles/?symbol=AAPL"
```

## SEC Filings Data Collection using SEC Edgar API

### Get SEC Filing Links for a Stock Ticker
```bash
curl -X GET "http://localhost:8000/financial_data/sec/filings/?ticker=AAPL"
```

### Get SEC Company Facts (XBRL Data) for a Stock Ticker
```bash
curl -X GET "http://localhost:8000/financial_data/sec/company_facts/?ticker=AAPL"
```

### Get AI-Generated 2-Sentence Summary of SEC Filings for a Stock Ticker
```bash
curl -X GET "http://localhost:8000/financial_data/sec/filings_summary/?ticker=AAPL"
```

## Earnings Calendar Data Collection using Financial Modeling Prep API

### Get Earnings Calendar for Date Range (All Companies)
```bash
# Get all companies reporting earnings in a specific date range
curl -X GET "http://localhost:8000/financial_data/earnings/calendar/?from_date=2024-01-01&to_date=2024-01-07"
```

### Get Earnings History for Specific Stock (EPS Reported, EPS Expected, Surprise %, Quarter Cycle)
```bash
# Get historical earnings data for a specific stock symbol
curl -X GET "http://localhost:8000/financial_data/earnings/symbol/?symbol=AAPL"
```

### Get Upcoming Earnings in Next 30 Days
```bash
# Get all companies with earnings scheduled in the next 30 days
curl -X GET "http://localhost:8000/financial_data/earnings/upcoming/"
```

### Get Upcoming Earnings for Maximum Available Days
```bash
# Get all companies with earnings scheduled for maximum available period (up to 365 days)
curl -X GET "http://localhost:8000/financial_data/earnings/upcoming/?days=max"

# Get earnings for custom number of days (e.g., 90 days)
curl -X GET "http://localhost:8000/financial_data/earnings/upcoming/?days=90"
```

## Earnings Insights - Comprehensive Analysis for Stock Arrays

### Get Comprehensive Earnings Insights for Array of Stocks (Beat Rate, Miss Rate, KPIs)
```bash
# Analyze earnings performance for multiple stocks with AI-generated market sentiment
curl -X POST "http://localhost:8000/financial_data/earnings/insights/" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "JNJ", "V"]}'
```

### Get Earnings Insights for Companies Reporting on Specific Date
```bash
# Get comprehensive analysis for all companies reporting earnings on a specific date
curl -X GET "http://localhost:8000/financial_data/earnings/insights/date/?date=2024-01-25"
```

### Get Comprehensive Earnings Insights with Guidance Implementation
```bash
# Get comprehensive earnings insights with guidance analysis, KPIs, and performance metrics
curl -X POST "http://localhost:8000/financial_data/earnings/insights/comprehensive/" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "JNJ", "V"]}'
```

### Get Earnings Correlation Analysis (AI-Powered)
```bash
# Get earnings correlation analysis with cloud revenue, AI/ML growth, chip demand, enterprise spending
curl -X GET "http://localhost:8000/financial_data/earnings/correlation/?symbol=AAPL"
```

### Get Earnings Correlation with Impact Level Analysis
```bash
# Get earnings correlation (0-100) and impact level (high/medium/low) using FMP API and OpenAI analysis
curl -X GET "http://localhost:8000/financial_data/earnings/correlation/impact/?symbol=AAPL"
```

## Sector Trends Analysis - Positive/Negative/Neutral Classification

### Get Sector Trends Analysis (Sentiment Classification)
```bash
# Analyze a specific sector and get positive/negative/neutral sentiment
curl -X GET "http://localhost:8000/financial_data/sector/trends/?sector=technology"
```

### Get Available Sectors for Analysis
```bash
# Get list of all supported sectors
curl -X GET "http://localhost:8000/financial_data/sector/available/"
```

### Get All Sectors Correlation Analysis
```bash
# Get numerical correlation (0.0-1.0) and description for all 26 sectors using OpenAI analysis
curl -X GET "http://localhost:8000/financial_data/sector/correlation/"
```

### Stock Correlation Overview - AI-Powered Multi-Sector Analysis
```bash
# Get comprehensive stock correlation analysis with related stocks grouped by sector
# Returns correlation data for same sector (3 stocks) and related sectors (3 stocks each)
# Includes AI-generated explanatory sentences for each correlation group
curl -X POST "http://localhost:8000/financial_data/stock/correlation_overview/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA"}'
```

## List of all stocks and correlation between two stocks

### List of all stocks
```bash
curl -X GET "http://localhost:8000/financial_data/nyse/stocks/"
```

### Correlation between two stocks
```bash
curl -X POST "http://localhost:8000/financial_data/nyse/correlation/" \
  -H "Content-Type: application/json" \
  -d '{"ticker1": "AAPL", "ticker2": "MSFT"}'
```

## Comprehensive Economic Data Collection from FRED API

### Raw market events from FRED
```bash
curl -X POST "http://localhost:8000/financial_data/fred/market_events/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### CPI from FRED
```bash
curl -X POST "http://localhost:8000/financial_data/fred/cpi_detailed/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Money, Banking & Finance Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/money_banking/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Employment & Labor Market Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/employment_labor/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Price & Commodities Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/price_commodities/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### International Economic Data
```bash
curl -X POST "http://localhost:8000/financial_data/fred/international_data/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### National Accounts Data
```bash
curl -X POST "http://localhost:8000/financial_data/fred/national_accounts/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Academic Research & Policy Uncertainty
```bash
curl -X POST "http://localhost:8000/financial_data/fred/academic_research/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Housing & Real Estate Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/housing_real_estate/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Manufacturing & Industrial Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/manufacturing_industrial/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Healthcare Cost & Utilization Indexes
```bash
curl -X POST "http://localhost:8000/financial_data/fred/healthcare_indexes/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Education & Productivity Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/education_productivity/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Trade Indexes & Transportation Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/trade_transportation/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Income Distribution & Demographics
```bash
curl -X POST "http://localhost:8000/financial_data/fred/income_demographics/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Cryptocurrency & Fintech Sentiment Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/cryptocurrency_fintech/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Historical & Academic Research Data
```bash
curl -X POST "http://localhost:8000/financial_data/fred/historical_academic/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Sector-Specific Economic Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/sector_specific/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### General Economic Indicators
```bash
curl -X POST "http://localhost:8000/financial_data/fred/economic_indicators/" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Brokerage Integration - Multi-Platform Account Management

### Get Supported Brokerage Platforms
```bash
# Get list of all supported brokerage platforms with configuration requirements
curl -X GET "http://localhost:8000/brokerage_integrations/brokerages/supported/"
```

### Connect Brokerage Account
```bash
# Connect a new brokerage account (Webull example)
curl -X POST "http://localhost:8000/brokerage_integrations/brokerages/connect/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "brokerage_name": "webull",
    "credentials": {
      "username": "user@example.com",
      "password": "password123"
    }
  }'

# Connect Charles Schwab account (API key method)
curl -X POST "http://localhost:8000/brokerage_integrations/brokerages/connect/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "brokerage_name": "charles_schwab",
    "credentials": {
      "api_key": "your_api_key",
      "secret_key": "your_secret_key"
    }
  }'
```

### Get User's Connected Accounts
```bash
# Get all connected brokerage accounts for a specific user
curl -X GET "http://localhost:8000/brokerage_integrations/brokerages/user/123/accounts/"
```

### Sync Account Data
```bash
# Manually sync account data (portfolio positions and transactions)
curl -X POST "http://localhost:8000/brokerage_integrations/brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/sync/" \
  -H "Content-Type: application/json" \
  -d '{"force_sync": false}'
```

### Get Portfolio Positions
```bash
# Get current portfolio positions for a specific account
curl -X GET "http://localhost:8000/brokerage_integrations/brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/portfolio/"
```

### Get Transaction History
```bash
# Get transaction history with optional filtering
curl -X GET "http://localhost:8000/brokerage_integrations/brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/transactions/"

# Get transactions with date range and type filters
curl -X GET "http://localhost:8000/brokerage_integrations/brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/transactions/?start_date=2024-01-01&end_date=2024-01-31&transaction_type=buy"
```

### Disconnect Brokerage Account
```bash
# Disconnect a brokerage account and remove all associated data
curl -X DELETE "http://localhost:8000/brokerage_integrations/brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/disconnect/"
```
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

# Comprehensive Indicator Coverage Summary

## Total Economic Data Collection: 200+ Indicators

### AI & Sentiment Analysis (2 endpoints)
- **OpenAI/Claude Market Analysis**: Advanced AI analysis of market trends and stock insights
- **Phi Confidence Score**: 0-100 sentiment analysis using OpenAI for text evaluation

### Stock Price Data (12 endpoints)
- **YFinance Data**: 6 endpoints covering daily, weekly, monthly, yearly, max historical, and price change analysis
- **Charles Schwab Data**: 6 endpoints with same time intervals plus authentication and callback handling

### SEC Filings Data (3 endpoints)
- **SEC Edgar API**: 3 endpoints providing SEC filing links, company facts (XBRL data), and AI-generated 2-sentence summaries for any stock ticker using CIK lookup

### Earnings Calendar Data (3 endpoints)
- **Financial Modeling Prep API**: 3 endpoints providing earnings calendar data, historical earnings for specific symbols, and upcoming earnings with EPS estimated/actual, surprise %, and quarter cycle dates

### Earnings Insights Data (2 endpoints)
- **Comprehensive Analysis**: 2 endpoints providing detailed earnings insights for stock arrays including beat rates, miss rates, average surprise percentages, revenue growth, positive earnings rates, and AI-generated market sentiment analysis

### News Data Collection (3 endpoints)
- **Financial News API**: Category-based news filtering (general, earnings, federal_reserve, markets, crypto, commodities, economic_data, mergers) with ticker-specific filtering
- **News Headlines API**: 1 endpoint providing simplified news headlines for a specific stock or general market news
- **News Sentiment Analysis API**: 1 endpoint providing sentiment analysis (positive/negative/neutral) for a specific stock
- **Best Articles API**: 1 endpoint providing the best 2 articles for a stock based on highest interaction and AI analysis

### Economic Data from FRED API (15 comprehensive endpoints)

#### 1. **Money, Banking & Finance** (16 indicators)
- M1/M2 Money Supply, Bank Credit, Treasury Rates, Corporate Bond Yields, Foreign Exchange Rates, Yield Spreads

#### 2. **Employment & Labor Markets** (18 indicators) 
- Unemployment Rates, Job Openings (JOLTS), Initial Claims, Payroll Data, Productivity Metrics, Labor Force Participation

#### 3. **Price & Commodities** (17 indicators)
- Oil Prices, Gold, Agricultural Commodities, Energy PPI, CPI Components, Import/Export Prices

#### 4. **International Economic Data** (15 indicators)
- GDP for Major Economies (China, EU, Japan, UK), Foreign Exchange Rates, Trade Balance, Global Indicators

#### 5. **National Accounts** (15 indicators)
- Real/Nominal GDP, Personal Income, Government Debt, Flow of Funds, Trade & International Transactions

#### 6. **Academic Research & Policy** (12 indicators)
- Economic Policy Uncertainty, VIX, Recession Probability, NBER Indicators, Financial Stress Indexes

#### 7. **Housing & Real Estate** (14 indicators)
- Housing Starts, Home Prices, Mortgage Rates, Construction Spending, Real Estate Investment

#### 8. **Manufacturing & Industrial** (14 indicators)
- Industrial Production, ISM PMI, Capacity Utilization, Durable Goods Orders, Factory Orders

#### 9. **Healthcare Cost & Utilization** (10 indicators)
- Medical Care CPI, Prescription Drug Prices, Hospital Services, Health Insurance Costs, Medicare Data

#### 10. **Education & Productivity** (10 indicators)
- Educational Services CPI, College Tuition, Labor Productivity, R&D Spending, Patent Data

#### 11. **Trade & Transportation** (13 indicators)
- Import/Export Price Indexes, Baltic Dry Index, Container Traffic, Transportation CPI, Vehicle Sales

#### 12. **Income Distribution & Demographics** (12 indicators)
- Median Household Income, Gini Coefficient, Poverty Rate, Population Data, Minimum Wage

#### 13. **Cryptocurrency & Fintech** (10 indicators)
- Digital Payment Volume, Credit Card Debt, Electronic Benefits, Fintech Investment Indicators

#### 14. **Historical & Academic Research** (12 indicators)
- Economic Policy Uncertainty, NBER Recession Indicators, Historical Fed Funds, Yield Curves

#### 15. **Sector-Specific Indicators** (12 indicators)
- Energy Production, Technology Production, Small Business Optimism, Consumer Sentiment, Innovation Indexes

### Complete Market Intelligence System
This comprehensive system provides:
- **Real-time market analysis** via AI models
- **Historical and current stock data** from multiple sources  
- **SEC filings and regulatory data** via Edgar API with direct filing links
- **Economic macro indicators** covering all major categories
- **Sentiment analysis** for text-based market intelligence
- **Financial news integration** with advanced filtering
- **200+ economic data points** for complete market coverage

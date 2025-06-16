# Backend Routes for Each Swing Phi Feature

## Phi Analysis

### Phi market trends using OpenAI/Claude
curl -X POST "http://localhost:8000/ai_models/openai/" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "AAPL"}'

### Phi Confidence Score (0-100) using OpenAI Sentiment Analysis
curl -X POST "http://localhost:8000/ai_models/phi_confidence/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple stock is performing exceptionally well this quarter with strong earnings growth and positive market sentiment."}'

## Stock Price Data Collection

### Price data for graphs from YFinance (Daily)
curl -X POST "http://localhost:8000/financial_data/yfinance/daily/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Phi daily snapshot alerts (Price Change)
curl -X POST "http://localhost:8000/financial_data/yfinance/price_change/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### YFinance Weekly Stock Data
curl -X POST "http://localhost:8000/financial_data/yfinance/weekly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### YFinance Monthly Stock Data
curl -X POST "http://localhost:8000/financial_data/yfinance/monthly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### YFinance Yearly Stock Data
curl -X POST "http://localhost:8000/financial_data/yfinance/yearly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### YFinance Maximum Historical Stock Data
curl -X POST "http://localhost:8000/financial_data/yfinance/max/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Login Link
curl -X GET "http://localhost:8000/financial_data/charles_schwab/"

### Charles Schwab Daily Stock Data
curl -X POST "http://localhost:8000/financial_data/charles_schwab/daily/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Weekly Stock Data
curl -X POST "http://localhost:8000/financial_data/charles_schwab/weekly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Monthly Stock Data
curl -X POST "http://localhost:8000/financial_data/charles_schwab/monthly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Yearly Stock Data
curl -X POST "http://localhost:8000/financial_data/charles_schwab/yearly/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Maximum Historical Stock Data
curl -X POST "http://localhost:8000/financial_data/charles_schwab/max/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

### Charles Schwab Price Change Analysis
curl -X POST "http://localhost:8000/financial_data/charles_schwab/price_change/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

## News Data Collection

### Financial News from News API
curl -X POST "http://localhost:8000/news_data/financial/" \
  -H "Content-Type: application/json" \
  -d '{"category": "markets", "ticker": "AAPL", "page_size": 10}'

## Comprehensive Economic Data Collection from FRED API

### Raw market events from FRED
curl -X POST "http://localhost:8000/financial_data/fred/market_events/" \
  -H "Content-Type: application/json" \
  -d '{}'

### CPI from FRED
curl -X POST "http://localhost:8000/financial_data/fred/cpi_detailed/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Money, Banking & Finance Indicators
curl -X POST "http://localhost:8000/financial_data/fred/money_banking/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Employment & Labor Market Indicators
curl -X POST "http://localhost:8000/financial_data/fred/employment_labor/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Price & Commodities Indicators
curl -X POST "http://localhost:8000/financial_data/fred/price_commodities/" \
  -H "Content-Type: application/json" \
  -d '{}'

### International Economic Data
curl -X POST "http://localhost:8000/financial_data/fred/international_data/" \
  -H "Content-Type: application/json" \
  -d '{}'

### National Accounts Data
curl -X POST "http://localhost:8000/financial_data/fred/national_accounts/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Academic Research & Policy Uncertainty
curl -X POST "http://localhost:8000/financial_data/fred/academic_research/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Housing & Real Estate Indicators
curl -X POST "http://localhost:8000/financial_data/fred/housing_real_estate/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Manufacturing & Industrial Indicators
curl -X POST "http://localhost:8000/financial_data/fred/manufacturing_industrial/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Healthcare Cost & Utilization Indexes
curl -X POST "http://localhost:8000/financial_data/fred/healthcare_indexes/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Education & Productivity Indicators
curl -X POST "http://localhost:8000/financial_data/fred/education_productivity/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Trade Indexes & Transportation Indicators
curl -X POST "http://localhost:8000/financial_data/fred/trade_transportation/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Income Distribution & Demographics
curl -X POST "http://localhost:8000/financial_data/fred/income_demographics/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Cryptocurrency & Fintech Sentiment Indicators
curl -X POST "http://localhost:8000/financial_data/fred/cryptocurrency_fintech/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Historical & Academic Research Data
curl -X POST "http://localhost:8000/financial_data/fred/historical_academic/" \
  -H "Content-Type: application/json" \
  -d '{}'

### Sector-Specific Economic Indicators
curl -X POST "http://localhost:8000/financial_data/fred/sector_specific/" \
  -H "Content-Type: application/json" \
  -d '{}'

### General Economic Indicators
curl -X POST "http://localhost:8000/financial_data/fred/economic_indicators/" \
  -H "Content-Type: application/json" \
  -d '{}'

# Comprehensive Indicator Coverage Summary

## Total Economic Data Collection: 200+ Indicators

### AI & Sentiment Analysis (2 endpoints)
- **OpenAI/Claude Market Analysis**: Advanced AI analysis of market trends and stock insights
- **Phi Confidence Score**: 0-100 sentiment analysis using OpenAI for text evaluation

### Stock Price Data (12 endpoints)
- **YFinance Data**: 6 endpoints covering daily, weekly, monthly, yearly, max historical, and price change analysis
- **Charles Schwab Data**: 6 endpoints with same time intervals plus authentication and callback handling

### News Data Collection (1 endpoint)
- **Financial News API**: Category-based news filtering (general, earnings, federal_reserve, markets, crypto, commodities, economic_data, mergers) with ticker-specific filtering

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
- **Economic macro indicators** covering all major categories
- **Sentiment analysis** for text-based market intelligence
- **Financial news integration** with advanced filtering
- **200+ economic data points** for complete market coverage

### API Authentication & Keys Configured
- ✅ **FRED API**: 881d0a5ff12349c8a165bd7a44aa069f (Active)
- ✅ **News API**: NEWS_API_KEY (Configured)
- ✅ **OpenAI API**: Azure ChatGPT Integration (Active)
- ✅ **Charles Schwab API**: OAuth2 Authentication (Setup)
- ✅ **YFinance**: No authentication required (Active)


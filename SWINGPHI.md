# Backend Routes for Each Swing Phi Feature

## Phi market trends using OpenAI/Claude
curl -X POST "http://localhost:8000/ai_models/openai/" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "AAPL"}'

## Price data for graphs from Charles Schwab
curl -X POST "http://localhost:8000/financial_data/yfinance/daily/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

## Phi daily snapshot alerts
curl -X POST "http://localhost:8000/financial_data/yfinance/price_change/" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

## Charles Schwab Login Link
curl -X GET "http://localhost:8000/financial_data/charles_schwab/"

## Raw market events from FRED
curl -X POST "http://localhost:8000/financial_data/fred/market_events/" \
  -H "Content-Type: application/json" \
  -d '{}'

## CPI from FRED
curl -X POST "http://localhost:8000/financial_data/fred/cpi_detailed/" \
  -H "Content-Type: application/json" \
  -d '{}'
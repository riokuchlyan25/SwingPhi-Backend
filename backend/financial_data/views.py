from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
import json
import pandas as pd
from .services.yfinance_service import get_ticker_from_request
from .services.fmp_service import fmp_service
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
from openai import AzureOpenAI


@csrf_exempt
def price_change_percent_view(request):
    """Return only percentage change for the current day for a ticker."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)
    ticker = request.GET.get('ticker', '').strip().upper()
    if not ticker:
        return JsonResponse({'error': 'ticker is required'}, status=400)

    try:
        quote = fmp_service.get_stock_quote(ticker)
        # FMP quote has changePercent as a percentage value (e.g., 1.23 for +1.23%)
        if not quote or 'changesPercentage' not in quote:
            # fallback compute from today's open/price if available
            price = quote.get('price') if quote else None
            open_price = quote.get('open') if quote else None
            if price and open_price and open_price != 0:
                pct = round((price - open_price) / open_price * 100, 2)
            else:
                return JsonResponse({'error': 'quote unavailable'}, status=503)
        else:
            # changesPercentage may include percent sign; normalize
            raw = quote['changesPercentage']
            if isinstance(raw, str):
                raw = raw.replace('%', '').replace('+', '').strip()
                pct = round(float(raw), 2)
            else:
                pct = round(float(raw), 2)

        return JsonResponse({'percent_change': pct})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def price_target_view(request):
    """Return an AI-generated price target using FMP fundamentals and quote."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json'}, status=400)

    ticker = (data.get('ticker') or '').strip().upper()
    if not ticker:
        return JsonResponse({'error': 'ticker is required'}, status=400)

    try:
        # Gather FMP data
        quote = fmp_service.get_stock_quote(ticker)
        profile = fmp_service.get_company_profile(ticker)
        hist = fmp_service.get_historical_price_data(ticker, period='1y')

        # Basic features
        current_price = quote.get('price') if quote else None
        pe = profile.get('pe') if profile else None
        sector = profile.get('sector') if profile else None
        beta = profile.get('beta') if profile else None

        last_close = float(hist['close'].iloc[-1]) if not hist.empty else None
        avg_30d = float(hist['close'].tail(30).mean()) if not hist.empty else None

        # Ensure OpenAI configured
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return JsonResponse({'error': 'OpenAI not configured'}, status=503)

        client = AzureOpenAI(api_key=AZURE_OPENAI_KEY, api_version="2023-05-15", azure_endpoint=AZURE_OPENAI_ENDPOINT)
        prompt = f"""
You are an equity research analyst. Propose a 6-12 month price target for {ticker}.
Use the data below and output ONLY valid JSON with keys price_target (float) and rationale (string).

Data:
- current_price: {current_price}
- last_close: {last_close}
- 30d_avg_close: {avg_30d}
- pe: {pe}
- beta: {beta}
- sector: {sector}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a concise equity research model. Output only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        # Extract JSON
        import re, json as pyjson
        if '```' in content:
            m = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content)
            content = m.group(1) if m else content
        try:
            result = pyjson.loads(content)
        except Exception:
            # Fallback minimal
            result = {"price_target": current_price, "rationale": "Model parsing fallback."}

        # Normalize output
        pt = float(result.get('price_target', current_price or 0))
        rationale = result.get('rationale', 'N/A')
        return JsonResponse({"ticker": ticker, "price_target": round(pt, 2), "rationale": rationale})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# internal
from financial_data.services.charles_schwab_service import (
    charles_schwab_api, charles_schwab_callback, charles_schwab_refresh_token, charles_schwab_price_data,
    charles_schwab_daily_api, charles_schwab_weekly_api, charles_schwab_monthly_api,
    charles_schwab_yearly_api, charles_schwab_max_api, charles_schwab_price_change_api
)
from financial_data.services.fred_service import (
    fred_yearly_api, fred_monthly_api, fred_weekly_api, fred_max_api,
    fred_economic_indicators_api, fred_market_events_api, fred_cpi_detailed_api,
    fred_money_banking_api, fred_employment_labor_api, fred_price_commodities_api,
    fred_international_data_api, fred_national_accounts_api, fred_academic_research_api,
    fred_housing_real_estate_api, fred_manufacturing_industrial_api,
    fred_healthcare_indexes_api, fred_education_productivity_api, fred_trade_transportation_api,
    fred_income_demographics_api, fred_cryptocurrency_fintech_api, fred_historical_academic_api,
    fred_sector_specific_api
)
from financial_data.services.yfinance_service import yfinance_daily_api, yfinance_weekly_api, yfinance_yearly_api, yfinance_max_api, yfinance_monthly_api, yfinance_price_change_api, stock_correlation_overview_api
from financial_data.services.sec_service import (
    get_sec_filings_api, get_sec_company_facts_api, get_sec_filings_summary_api
)
from financial_data.services.earnings_service import get_earnings_calendar_api, get_earnings_for_symbol_api, get_upcoming_earnings_api, get_earnings_insights_api, get_earnings_insights_by_date_api, get_comprehensive_earnings_insights_api, get_earnings_correlation_api, get_earnings_correlation_impact_api
from financial_data.services.sector_analysis_service import get_sector_trends_api, get_available_sectors_api, get_all_sectors_correlation_api
from financial_data.services.nyse_stocks_service import get_nyse_stocks_api, get_stock_correlation_api

# external

# built-in
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def fred_yearly_view(request):
    return fred_yearly_api(request)

@csrf_exempt
def fred_monthly_view(request):
    return fred_monthly_api(request)

@csrf_exempt
def fred_weekly_view(request):
    return fred_weekly_api(request)

@csrf_exempt
def fred_max_view(request):
    return fred_max_api(request)

@csrf_exempt
def fred_economic_indicators_view(request):
    return fred_economic_indicators_api(request)

@csrf_exempt
def fred_market_events_view(request):
    return fred_market_events_api(request)

@csrf_exempt
def fred_cpi_detailed_view(request):
    return fred_cpi_detailed_api(request)

@csrf_exempt
def fred_money_banking_view(request):
    return fred_money_banking_api(request)

@csrf_exempt
def fred_employment_labor_view(request):
    return fred_employment_labor_api(request)

@csrf_exempt
def fred_price_commodities_view(request):
    return fred_price_commodities_api(request)

@csrf_exempt
def fred_international_data_view(request):
    return fred_international_data_api(request)

@csrf_exempt
def fred_national_accounts_view(request):
    return fred_national_accounts_api(request)

@csrf_exempt
def fred_academic_research_view(request):
    return fred_academic_research_api(request)

@csrf_exempt
def fred_housing_real_estate_view(request):
    return fred_housing_real_estate_api(request)

@csrf_exempt
def fred_manufacturing_industrial_view(request):
    return fred_manufacturing_industrial_api(request)

@csrf_exempt
def fred_healthcare_indexes_view(request):
    return fred_healthcare_indexes_api(request)

@csrf_exempt
def fred_education_productivity_view(request):
    return fred_education_productivity_api(request)

@csrf_exempt
def fred_trade_transportation_view(request):
    return fred_trade_transportation_api(request)

@csrf_exempt
def fred_income_demographics_view(request):
    return fred_income_demographics_api(request)

@csrf_exempt
def fred_cryptocurrency_fintech_view(request):
    return fred_cryptocurrency_fintech_api(request)

@csrf_exempt
def fred_historical_academic_view(request):
    return fred_historical_academic_api(request)

@csrf_exempt
def fred_sector_specific_view(request):
    return fred_sector_specific_api(request)

@csrf_exempt
def charles_schwab_view(request):
    return charles_schwab_api(request)

@csrf_exempt
def charles_schwab_callback_view(request):
    return charles_schwab_callback(request)

@csrf_exempt
def charles_schwab_refresh_token_view(request):
    return charles_schwab_refresh_token(request)

@csrf_exempt
def charles_schwab_price_view(request):
    return charles_schwab_price_data(request)

@csrf_exempt
def charles_schwab_daily_view(request):
    return charles_schwab_daily_api(request)

@csrf_exempt
def charles_schwab_weekly_view(request):
    return charles_schwab_weekly_api(request)

@csrf_exempt
def charles_schwab_monthly_view(request):
    return charles_schwab_monthly_api(request)

@csrf_exempt
def charles_schwab_yearly_view(request):
    return charles_schwab_yearly_api(request)

@csrf_exempt
def charles_schwab_max_view(request):
    return charles_schwab_max_api(request)

@csrf_exempt
def charles_schwab_price_change_view(request):
    return charles_schwab_price_change_api(request)

@csrf_exempt
def yfinance_daily_view(request):
    return yfinance_daily_api(request)

@csrf_exempt
def yfinance_weekly_view(request):
    return yfinance_weekly_api(request)

@csrf_exempt
def yfinance_yearly_view(request):
    return yfinance_yearly_api(request)

@csrf_exempt
def yfinance_max_view(request):
    return yfinance_max_api(request)

@csrf_exempt
def yfinance_monthly_view(request):
    return yfinance_monthly_api(request)

@csrf_exempt
def yfinance_price_change_view(request):
    return yfinance_price_change_api(request)

@csrf_exempt
def sec_filings_view(request):
    return get_sec_filings_api(request)

@csrf_exempt
def sec_company_facts_view(request):
    return get_sec_company_facts_api(request)

@csrf_exempt
def sec_filings_summary_view(request):
    return get_sec_filings_summary_api(request)

@csrf_exempt
def earnings_calendar_view(request):
    return get_earnings_calendar_api(request)

@csrf_exempt
def earnings_for_symbol_view(request):
    return get_earnings_for_symbol_api(request)

@csrf_exempt
def upcoming_earnings_view(request):
    return get_upcoming_earnings_api(request)

@csrf_exempt
def earnings_insights_view(request):
    return get_earnings_insights_api(request)

@csrf_exempt
def earnings_insights_by_date_view(request):
    """Get earnings insights for companies reporting on specific date"""
    return get_earnings_insights_by_date_api(request)

@csrf_exempt
def comprehensive_earnings_insights_view(request):
    """Get comprehensive earnings insights with guidance implementation"""
    return get_comprehensive_earnings_insights_api(request)

@csrf_exempt
def earnings_correlation_view(request):
    """Get earnings correlation analysis for a stock"""
    return get_earnings_correlation_api(request)

@csrf_exempt
def earnings_correlation_impact_view(request):
    """Get earnings correlation with impact level analysis"""
    return get_earnings_correlation_impact_api(request)

# Sector Analysis Views
def sector_trends_view(request):
    """Get sector trends analysis with sentiment (positive/negative/neutral)"""
    return get_sector_trends_api(request)

def available_sectors_view(request):
    """Get list of available sectors for analysis"""
    return get_available_sectors_api(request)

def all_sectors_correlation_view(request):
    """Get correlation analysis across all 26 sectors"""
    return get_all_sectors_correlation_api(request)

@csrf_exempt
def stock_correlation_overview_view(request):
    """Get stock correlation overview with related stocks grouped by sector"""
    return stock_correlation_overview_api(request)

@csrf_exempt
def nyse_stocks_view(request):
    """Get list of NYSE stocks with their industries and sectors"""
    return get_nyse_stocks_api(request)

@csrf_exempt
def stock_correlation_view(request):
    """Get correlation between two stocks from the NYSE list"""
    return get_stock_correlation_api(request)


@csrf_exempt
def fmp_daily_view(request):
    """Get last 5 daily candles from FMP for a ticker."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    ticker = get_ticker_from_request(request)
    if not ticker:
        return JsonResponse({'error': 'Ticker required'}, status=400)
    try:
        df = fmp_service.get_historical_price_data(ticker, period='6mo')
        if df is None or df.empty:
            return JsonResponse({'error': 'No data available'}, status=503)
        recent = df.tail(5).copy()
        recent = recent[['open', 'high', 'low', 'close', 'volume']]
        recent.index = pd.to_datetime(recent.index)
        recent = recent.reset_index().rename(columns={'index': 'date'})
        data = [
            {
                'date': row['date'].strftime('%Y-%m-%d'),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
            }
            for _, row in recent.iterrows()
            if pd.notna(row['open']) and pd.notna(row['high']) and pd.notna(row['low']) and pd.notna(row['close'])
        ]
        if not data:
            return JsonResponse({'error': 'No valid data found'}, status=503)
        return JsonResponse({'ticker': ticker, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fmp_weekly_view(request):
    """Get weekly OHLCV aggregated candles from FMP (last ~12 weeks)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    ticker = get_ticker_from_request(request)
    if not ticker:
        return JsonResponse({'error': 'Ticker required'}, status=400)
    try:
        df = fmp_service.get_historical_price_data(ticker, period='6mo')
        if df is None or df.empty:
            return JsonResponse({'error': 'No data available'}, status=503)
        daily = df[['open', 'high', 'low', 'close', 'volume']].copy()
        daily.index = pd.to_datetime(daily.index)
        weekly = pd.DataFrame({
            'open': daily['open'].resample('W-FRI').first(),
            'high': daily['high'].resample('W-FRI').max(),
            'low': daily['low'].resample('W-FRI').min(),
            'close': daily['close'].resample('W-FRI').last(),
            'volume': daily['volume'].resample('W-FRI').sum(),
        }).dropna()
        weekly = weekly.tail(12).reset_index().rename(columns={'date': 'Date'})
        data = [
            {
                'date': row['index'].strftime('%Y-%m-%d'),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
            }
            for _, row in weekly.iterrows()
        ]
        if not data:
            return JsonResponse({'error': 'No valid data found'}, status=503)
        return JsonResponse({'ticker': ticker, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fmp_monthly_view(request):
    """Get monthly OHLCV aggregated candles from FMP (last ~24 months)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    ticker = get_ticker_from_request(request)
    if not ticker:
        return JsonResponse({'error': 'Ticker required'}, status=400)
    try:
        df = fmp_service.get_historical_price_data(ticker, period='5y')
        if df is None or df.empty:
            return JsonResponse({'error': 'No data available'}, status=503)
        daily = df[['open', 'high', 'low', 'close', 'volume']].copy()
        daily.index = pd.to_datetime(daily.index)
        monthly = pd.DataFrame({
            'open': daily['open'].resample('M').first(),
            'high': daily['high'].resample('M').max(),
            'low': daily['low'].resample('M').min(),
            'close': daily['close'].resample('M').last(),
            'volume': daily['volume'].resample('M').sum(),
        }).dropna()
        monthly = monthly.tail(24).reset_index()
        data = [
            {
                'date': row['date'].strftime('%Y-%m-%d') if 'date' in monthly.columns else row['index'].strftime('%Y-%m-%d'),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
            }
            for _, row in monthly.iterrows()
        ]
        if not data:
            return JsonResponse({'error': 'No valid data found'}, status=503)
        return JsonResponse({'ticker': ticker, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fmp_yearly_view(request):
    """Get yearly OHLCV aggregated candles from FMP (last ~10 years)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    ticker = get_ticker_from_request(request)
    if not ticker:
        return JsonResponse({'error': 'Ticker required'}, status=400)
    try:
        df = fmp_service.get_historical_price_data(ticker, period='max')
        if df is None or df.empty:
            return JsonResponse({'error': 'No data available'}, status=503)
        daily = df[['open', 'high', 'low', 'close', 'volume']].copy()
        daily.index = pd.to_datetime(daily.index)
        yearly = pd.DataFrame({
            'open': daily['open'].resample('Y').first(),
            'high': daily['high'].resample('Y').max(),
            'low': daily['low'].resample('Y').min(),
            'close': daily['close'].resample('Y').last(),
            'volume': daily['volume'].resample('Y').sum(),
        }).dropna()
        yearly = yearly.tail(10).reset_index()
        data = [
            {
                'date': row['date'].strftime('%Y-%m-%d') if 'date' in yearly.columns else row['index'].strftime('%Y-%m-%d'),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
            }
            for _, row in yearly.iterrows()
        ]
        if not data:
            return JsonResponse({'error': 'No valid data found'}, status=503)
        return JsonResponse({'ticker': ticker, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fmp_hourly_view(request):
    """Get intraday OHLCV data at 1-hour interval from FMP (up to ~200 bars)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    ticker = get_ticker_from_request(request)
    if not ticker:
        return JsonResponse({'error': 'Ticker required'}, status=400)
    try:
        df = fmp_service.get_intraday_price_data(ticker, interval='1hour', limit=200)
        if df is None or df.empty:
            return JsonResponse({'error': 'No data available'}, status=503)

        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df.index = pd.to_datetime(df.index)
        df = df.reset_index().rename(columns={'index': 'date'})

        data = [
            {
                'date': row['date'].strftime('%Y-%m-%d %H:%M:%S'),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume']) if pd.notna(row['volume']) else 0,
            }
            for _, row in df.iterrows()
            if pd.notna(row['open']) and pd.notna(row['high']) and pd.notna(row['low']) and pd.notna(row['close'])
        ]
        if not data:
            return JsonResponse({'error': 'No valid data found'}, status=503)
        return JsonResponse({'ticker': ticker, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def trending_assets_view(request):
    """Get trending stocks (FMP most actives) and trending crypto (CoinGecko)."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)
    try:
        # Trending stocks from FMP (most actives)
        stocks = fmp_service.get_most_active_stocks(limit=20)

        # Trending crypto from CoinGecko simple/markets endpoint
        import requests
        crypto = []
        try:
            cg_url = 'https://api.coingecko.com/api/v3/coins/markets'
            params = {
                'vs_currency': 'usd',
                'order': 'gecko_desc',
                'per_page': 20,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            resp = requests.get(cg_url, params=params, timeout=10)
            if resp.ok:
                data = resp.json() or []
                for item in data:
                    crypto.append({
                        'symbol': item.get('symbol', '').upper(),
                        'name': item.get('name'),
                        'price': item.get('current_price'),
                        'change24h': item.get('price_change_percentage_24h'),
                        'market_cap': item.get('market_cap'),
                        'volume': item.get('total_volume')
                    })
        except Exception:
            crypto = []

        return JsonResponse({'stocks': stocks, 'crypto': crypto})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

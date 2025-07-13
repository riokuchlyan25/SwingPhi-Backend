# internal
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
from openai import AzureOpenAI

# built-in
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

@csrf_exempt
def chatgpt_api(request):
    """Get simplified ChatGPT response"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Support both old and new parameter names for backward compatibility
            prompt = data.get('prompt') or data.get('user_input', '').strip()
            
            if not prompt:
                return JsonResponse({'error': 'Prompt or user_input required'}, status=400)
            
            if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                return JsonResponse({'error': 'OpenAI not configured'}, status=500)
            
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_KEY,
                api_version="2023-05-15",
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            
            # For backward compatibility, if user_input is provided, use the original prompt format
            if data.get('user_input'):
                analysis_prompt = f"Give me a short stock analysis of the following stock (ensure the analysis is concise and to the point with no special characters just punctuation and the alphabet. do not list out its metrics but rather give me a 5 sentence paragraph analysis. mention unique and insightful details not just its basic facts such as location, industry, etc. do not use special characters or markdown formatting such as * or _. THE RESPONSE MUST BE IN PLAIN TEXT AND LESS THAN 80 WORDS. do not use an astricks or number sign either): {prompt}"
            else:
                analysis_prompt = prompt
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            return JsonResponse({
                'response': response.choices[0].message.content
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def phi_confidence_api(request):
    """
    Phi Confidence API endpoint - Returns only a confidence score from 0-100
    Uses OpenAI ChatGPT for confidence analysis
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    # Parse request data
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            text_input = data.get('text', '')
        else:
            text_input = request.POST.get('text', '') or request.body.decode('utf-8')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not text_input:
        return JsonResponse({'error': 'No text input provided'}, status=400)
    
    if len(text_input) > 5000:
        return JsonResponse({'error': 'Text input too long (max 5000 characters)'}, status=400)
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        # Construct prompt for confidence scoring
        prompt = f"""
        Analyze the confidence level of the following text for financial/investment decision making.
        
        Text to analyze: "{text_input}"
        
        Based on the sentiment, tone, certainty, and overall confidence expressed in this text, provide a confidence score from 0 to 100 where:
        - 0 = extremely negative/uncertain
        - 50 = neutral
        - 100 = extremely positive/confident
        
        Consider factors like positive vs negative language, certainty vs uncertainty indicators, factual statements vs opinions, emotional tone and conviction, and market optimism vs pessimism.
        
        Respond ONLY in this exact JSON format:
        {{
            "confidence_score": [0-100 integer]
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a financial confidence scoring expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent results
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response (in case there's extra text)
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group()
            
            parsed_response = json.loads(ai_response)
            
            # Validate and clean the response
            confidence_score = int(parsed_response.get('confidence_score', 50))
            confidence_score = max(0, min(100, confidence_score))  # Ensure 0-100 range
            
            return JsonResponse({'confidence_score': confidence_score})
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: return neutral confidence score
            return JsonResponse({'confidence_score': 50})
            
    except Exception as e:
        return JsonResponse({'confidence_score': 50}, status=500)

@csrf_exempt
def phi_price_targets_api(request):
    """
    Phi Price Targets API endpoint - AI-powered price target analysis
    Analyzes technical and fundamental data to provide price targets
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return JsonResponse({'error': 'OpenAI not configured'}, status=500)
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        prompt = f"""
        Provide a comprehensive price target analysis for {symbol} stock.
        
        Please analyze and provide:
        1. Current price range assessment
        2. Short-term price target (1-3 months)
        3. Medium-term price target (3-6 months)
        4. Long-term price target (6-12 months)
        5. Key support and resistance levels
        6. Risk factors and catalysts
        7. Technical indicators summary
        8. Fundamental analysis summary
        
        Respond ONLY in this exact JSON format:
        {{
            "symbol": "{symbol}",
            "price_targets": {{
                "short_term": {{"target": 0.0, "timeframe": "1-3 months", "probability": "0%"}},
                "medium_term": {{"target": 0.0, "timeframe": "3-6 months", "probability": "0%"}},
                "long_term": {{"target": 0.0, "timeframe": "6-12 months", "probability": "0%"}}
            }},
            "support_resistance": {{
                "support_levels": [0.0, 0.0, 0.0],
                "resistance_levels": [0.0, 0.0, 0.0]
            }},
            "analysis_summary": "Brief analysis summary",
            "risk_factors": ["factor1", "factor2", "factor3"],
            "catalysts": ["catalyst1", "catalyst2", "catalyst3"],
            "technical_indicators": {{
                "trend": "bullish/bearish/neutral",
                "momentum": "strong/weak/neutral",
                "volume": "high/low/normal"
            }},
            "confidence_level": "high/medium/low",
            "analyst_rating": "buy/hold/sell"
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert financial analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group()
            
            parsed_response = json.loads(ai_response)
            
            # Add metadata
            parsed_response['phi_analysis_metadata'] = {
                'model_used': MODEL_NAME,
                'analysis_type': 'price_targets',
                'timestamp': str(json.dumps(None))
            }
            
            return JsonResponse(parsed_response)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({
                'error': f'Response parsing error: {str(e)}',
                'symbol': symbol,
                'raw_response': ai_response
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def phi_news_impact_api(request):
    """
    Phi News Impact API endpoint - News impact analysis with volatility and sentiment scoring
    Analyzes how news events might impact stock price volatility
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return JsonResponse({'error': 'OpenAI not configured'}, status=500)
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        prompt = f"""
        Analyze the potential news impact on {symbol} stock.
        
        Please provide:
        1. Recent news sentiment analysis
        2. Volatility impact assessment
        3. Market reaction prediction
        4. News-based risk factors
        5. Sentiment score (0-100)
        6. Volatility forecast
        7. Key news themes affecting the stock
        
        Respond ONLY in this exact JSON format:
        {{
            "symbol": "{symbol}",
            "news_impact": {{
                "sentiment_score": 0,
                "volatility_impact": "high/medium/low",
                "market_reaction": "positive/negative/neutral",
                "impact_duration": "short/medium/long"
            }},
            "key_themes": ["theme1", "theme2", "theme3"],
            "risk_factors": ["risk1", "risk2", "risk3"],
            "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
            "volatility_forecast": {{
                "next_week": "high/medium/low",
                "next_month": "high/medium/low",
                "trend": "increasing/decreasing/stable"
            }},
            "sentiment_breakdown": {{
                "positive_factors": ["factor1", "factor2"],
                "negative_factors": ["factor1", "factor2"],
                "neutral_factors": ["factor1", "factor2"]
            }},
            "overall_assessment": "Brief overall assessment",
            "confidence_level": "high/medium/low"
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert financial news analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group()
            
            parsed_response = json.loads(ai_response)
            
            # Add metadata
            parsed_response['phi_analysis_metadata'] = {
                'model_used': MODEL_NAME,
                'analysis_type': 'news_impact',
                'timestamp': str(json.dumps(None))
            }
            
            return JsonResponse(parsed_response)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({
                'error': f'Response parsing error: {str(e)}',
                'symbol': symbol,
                'raw_response': ai_response
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def phi_volume_signals_api(request):
    """
    Phi Volume Signals API endpoint - Volume trading signals with correlation analysis
    Analyzes trading volume patterns and correlations
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return JsonResponse({'error': 'OpenAI not configured'}, status=500)
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        prompt = f"""
        Analyze volume trading signals for {symbol} stock.
        
        Please provide:
        1. Volume trend analysis
        2. Volume-price correlation
        3. Trading signal strength
        4. Volume anomaly detection
        5. Institutional vs retail volume indicators
        6. Volume-based entry/exit signals
        7. Market maker activity assessment
        
        Respond ONLY in this exact JSON format:
        {{
            "symbol": "{symbol}",
            "volume_analysis": {{
                "trend": "increasing/decreasing/stable",
                "average_volume": 0,
                "volume_spike": true/false,
                "volume_strength": "high/medium/low"
            }},
            "trading_signals": {{
                "buy_signal": true/false,
                "sell_signal": true/false,
                "signal_strength": "strong/weak/neutral",
                "entry_point": "current/wait/avoid"
            }},
            "volume_patterns": {{
                "accumulation": true/false,
                "distribution": true/false,
                "breakout_volume": true/false,
                "profit_taking": true/false
            }},
            "institutional_activity": {{
                "institutional_buying": true/false,
                "institutional_selling": true/false,
                "retail_activity": "high/medium/low",
                "smart_money_flow": "inflow/outflow/neutral"
            }},
            "volume_indicators": {{
                "volume_price_trend": "positive/negative/neutral",
                "on_balance_volume": "rising/falling/sideways",
                "volume_oscillator": "overbought/oversold/neutral"
            }},
            "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
            "risk_assessment": "high/medium/low",
            "confidence_level": "high/medium/low"
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert volume analysis specialist. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group()
            
            parsed_response = json.loads(ai_response)
            
            # Add metadata
            parsed_response['phi_analysis_metadata'] = {
                'model_used': MODEL_NAME,
                'analysis_type': 'volume_signals',
                'timestamp': str(json.dumps(None))
            }
            
            return JsonResponse(parsed_response)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({
                'error': f'Response parsing error: {str(e)}',
                'symbol': symbol,
                'raw_response': ai_response
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def phi_options_activity_api(request):
    """
    Phi Options Activity API endpoint - Options activity analysis with market maker positioning
    Analyzes options flow and market maker activity
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
            return JsonResponse({'error': 'OpenAI not configured'}, status=500)
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        prompt = f"""
        Analyze options activity for {symbol} stock.
        
        Please provide:
        1. Options flow analysis
        2. Put/Call ratio assessment
        3. Market maker positioning
        4. Unusual options activity
        5. Implied volatility analysis
        6. Options-based sentiment indicators
        7. Gamma and delta positioning
        
        Respond ONLY in this exact JSON format:
        {{
            "symbol": "{symbol}",
            "options_flow": {{
                "call_volume": 0,
                "put_volume": 0,
                "put_call_ratio": 0.0,
                "flow_direction": "bullish/bearish/neutral"
            }},
            "market_maker_activity": {{
                "positioning": "long/short/neutral",
                "gamma_exposure": "high/medium/low",
                "delta_hedging": "active/passive/neutral",
                "market_maker_bias": "bullish/bearish/neutral"
            }},
            "unusual_activity": {{
                "large_trades": true/false,
                "unusual_volume": true/false,
                "sweep_activity": true/false,
                "block_trades": true/false
            }},
            "implied_volatility": {{
                "iv_rank": 0,
                "iv_percentile": 0,
                "iv_trend": "rising/falling/stable",
                "iv_skew": "call/put/neutral"
            }},
            "sentiment_indicators": {{
                "options_sentiment": "bullish/bearish/neutral",
                "smart_money_flow": "calls/puts/neutral",
                "retail_activity": "high/medium/low",
                "institutional_flow": "calls/puts/neutral"
            }},
            "key_strikes": {{
                "max_pain": 0.0,
                "high_gamma_strikes": [0.0, 0.0, 0.0],
                "high_open_interest": [0.0, 0.0, 0.0]
            }},
            "trading_implications": ["implication1", "implication2", "implication3"],
            "risk_assessment": "high/medium/low",
            "confidence_level": "high/medium/low"
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert options flow analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group()
            
            parsed_response = json.loads(ai_response)
            
            # Add metadata
            parsed_response['phi_analysis_metadata'] = {
                'model_used': MODEL_NAME,
                'analysis_type': 'options_activity',
                'timestamp': str(json.dumps(None))
            }
            
            return JsonResponse(parsed_response)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({
                'error': f'Response parsing error: {str(e)}',
                'symbol': symbol,
                'raw_response': ai_response
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# internal
from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT

# external
from openai import AzureOpenAI

# built-in
from django.http import JsonResponse
from django.shortcuts import HttpResponse
import json
import re

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

def phi_confidence_api(request):
    """
    Phi Confidence API endpoint - Analyzes text sentiment and returns confidence score 0-100
    Uses OpenAI ChatGPT for advanced sentiment analysis
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
        
        # Construct prompt for sentiment analysis and confidence scoring
        prompt = f"""
        Analyze the sentiment and confidence level of the following text for financial/investment decision making.
        
        Text to analyze: "{text_input}"
        
        Based on the sentiment, tone, certainty, and overall confidence expressed in this text, provide:
        1. A confidence score from 0 to 100 (where 0 = extremely negative/uncertain, 50 = neutral, 100 = extremely positive/confident)
        2. A brief sentiment analysis (1-2 sentences)
        3. Key sentiment indicators found in the text
        
        Consider factors like:
        - Positive vs negative language
        - Certainty vs uncertainty indicators
        - Factual statements vs opinions
        - Emotional tone and conviction
        - Market optimism vs pessimism
        
        Respond ONLY in this exact JSON format:
        {{
            "confidence_score": [0-100 integer],
            "sentiment_analysis": "[brief analysis]",
            "sentiment_indicators": ["indicator1", "indicator2", "indicator3"],
            "overall_sentiment": "[positive/negative/neutral]"
        }}
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a financial sentiment analysis expert. Always respond with valid JSON only."},
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
            
            result = {
                'confidence_score': confidence_score,
                'sentiment_analysis': parsed_response.get('sentiment_analysis', 'Unable to analyze sentiment'),
                'sentiment_indicators': parsed_response.get('sentiment_indicators', []),
                'overall_sentiment': parsed_response.get('overall_sentiment', 'neutral'),
                'input_text': text_input[:200] + ('...' if len(text_input) > 200 else ''),  # Truncated input for response
                'text_length': len(text_input),
                'phi_confidence_metadata': {
                    'model_used': MODEL_NAME,
                    'analysis_type': 'financial_sentiment',
                    'confidence_range': '0-100'
                }
            }
            
            return JsonResponse(result)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: provide basic sentiment analysis if JSON parsing fails
            return JsonResponse({
                'confidence_score': 50,
                'sentiment_analysis': 'Unable to parse detailed analysis',
                'sentiment_indicators': ['parsing_error'],
                'overall_sentiment': 'neutral',
                'input_text': text_input[:200] + ('...' if len(text_input) > 200 else ''),
                'text_length': len(text_input),
                'error': f'Response parsing error: {str(e)}',
                'raw_response': ai_response
            })
            
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to analyze sentiment: {str(e)}',
            'confidence_score': 50,
            'overall_sentiment': 'error'
        }, status=500)

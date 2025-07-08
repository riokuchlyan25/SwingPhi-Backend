# internal

# external
import pandas as pd
import requests
from django.http import JsonResponse
import json

# built-in
import os

def get_CIK(ticker: str) -> str:
    """Get CIK (Central Index Key) for a given stock ticker"""
    try:
        # Use absolute path to ensure we can find the file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cik_file_path = os.path.join(base_dir, "data", "cik.csv")
        
        cik_data = pd.read_csv(cik_file_path, delimiter='\t', header=None)
        data = cik_data.set_index(0)
        
        ticker_cik = str(int(data.loc[ticker.lower(), 1]))
        # Pad with zeros to make it 10 digits
        cik = ticker_cik.zfill(10)
        return cik
    except Exception as e:
        return str(e)

def get_sec_filings_api(request):
    """Get simplified SEC filing links"""
    if request.method == 'GET':
        ticker = request.GET.get('ticker', '').upper()
        
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            cik = get_CIK(ticker)
            
            if not cik.isdigit():
                return JsonResponse({'error': f'Invalid ticker: {ticker}'}, status=404)
            
            sec_api_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            headers = {'User-Agent': 'Financial Data API (contact@example.com)'}
            
            response = requests.get(sec_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                recent_filings = data.get('filings', {}).get('recent', {})
                
                # Get only the latest 5 filings with valid data
                filing_links = []
                accession_numbers = recent_filings.get('accessionNumber', [])
                filing_dates = recent_filings.get('filingDate', [])
                forms = recent_filings.get('form', [])
                primary_documents = recent_filings.get('primaryDocument', [])
                
                for i in range(min(5, len(accession_numbers))):
                    if all([accession_numbers[i], filing_dates[i], forms[i], primary_documents[i]]):
                        accession_formatted = accession_numbers[i].replace('-', '')
                        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_formatted}/{primary_documents[i]}"
                        
                        filing_links.append({
                            'form': forms[i],
                            'date': filing_dates[i],
                            'url': filing_url
                        })
                
                return JsonResponse({
                    'ticker': ticker,
                    'filings': filing_links
                })
            else:
                return JsonResponse({'error': f'SEC API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_sec_company_facts_api(request):
    """Get SEC company facts for a given stock ticker"""
    if request.method == 'GET':
        ticker = request.GET.get('ticker', '').upper()
        
        if not ticker:
            return JsonResponse({
                'error': 'Ticker parameter is required',
                'status': 'error'
            }, status=400)
        
        try:
            # Get CIK for the ticker
            cik = get_CIK(ticker)
            
            # Check if CIK retrieval failed
            if not cik.isdigit():
                return JsonResponse({
                    'error': f'Could not find CIK for ticker {ticker}: {cik}',
                    'status': 'error'
                }, status=404)
            
            # SEC Edgar API endpoint for company facts
            sec_api_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            
            # SEC requires a User-Agent header
            headers = {
                'User-Agent': 'Financial Data API (contact@example.com)'
            }
            
            # Make request to SEC API
            response = requests.get(sec_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                return JsonResponse({
                    'ticker': ticker,
                    'cik': cik,
                    'company_name': data.get('entityName', 'N/A'),
                    'facts': data.get('facts', {}),
                    'status': 'success'
                })
            else:
                return JsonResponse({
                    'error': f'Failed to fetch company facts from SEC API. Status code: {response.status_code}',
                    'status': 'error'
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({
                'error': f'An error occurred: {str(e)}',
                'status': 'error'
            }, status=500)
    
    else:
        return JsonResponse({
            'error': 'Only GET method is allowed',
            'status': 'error'
        }, status=405)

def get_sec_filings_summary_api(request):
    """Get simplified SEC filings with AI summary focused on earnings from 10Q filings with fallback to 10K and other forms"""
    if request.method == 'GET':
        ticker = request.GET.get('ticker', '').upper()
        
        if not ticker:
            return JsonResponse({'error': 'Ticker required'}, status=400)
        
        try:
            cik = get_CIK(ticker)
            
            if not cik.isdigit():
                return JsonResponse({'error': f'Invalid ticker: {ticker}'}, status=404)
            
            sec_api_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            headers = {'User-Agent': 'Financial Data API (contact@example.com)'}
            
            response = requests.get(sec_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                recent_filings = data.get('filings', {}).get('recent', {})
                
                forms = recent_filings.get('form', [])
                dates = recent_filings.get('filingDate', [])
                
                # Priority order: 10-Q (quarterly) → 10-K (annual) → any available form
                target_forms = ['10-Q', '10-K', '8-K', '10-Q/A', '10-K/A']
                found_forms = []
                found_dates = []
                form_type_used = None
                
                # Try to find forms in priority order
                for target_form in target_forms:
                    for i, form in enumerate(forms):
                        if form == target_form and len(found_forms) < 3:
                            found_forms.append(form)
                            found_dates.append(dates[i])
                            if form_type_used is None:
                                form_type_used = target_form
                    
                    if found_forms:  # If we found any forms of this type, use them
                        break
                
                # If no priority forms found, use any available forms
                if not found_forms:
                    for i, form in enumerate(forms[:3]):
                        found_forms.append(form)
                        found_dates.append(dates[i])
                        if form_type_used is None:
                            form_type_used = form
                
                # Generate earnings-focused AI summary with form-specific prompt
                ai_summary = "Recent earnings information from SEC filings unavailable"
                form_context = "10-Q quarterly filing"
                
                # Adjust context based on actual form found
                if form_type_used == '10-K':
                    form_context = "10-K annual filing"
                elif form_type_used == '8-K':
                    form_context = "8-K current report"
                elif form_type_used in ['10-Q/A', '10-K/A']:
                    form_context = f"{form_type_used} amended filing"
                elif form_type_used and form_type_used != '10-Q':
                    form_context = f"{form_type_used} filing"
                
                try:
                    from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
                    from openai import AzureOpenAI
                    
                    if all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                        client = AzureOpenAI(
                            api_key=AZURE_OPENAI_KEY,
                            api_version="2023-05-15",
                            azure_endpoint=AZURE_OPENAI_ENDPOINT
                        )
                        
                        # Create a more flexible prompt that works regardless of form type
                        prompt = f"""Provide a 2-sentence summary of {ticker}'s earnings and financial performance based on their most recent {form_context} from {found_dates[0] if found_dates else 'recent period'}. 
                        
Focus on key financial metrics such as revenue, net income, earnings per share, and overall financial performance. 
If specific earnings data is not available in the filing, provide a general assessment of the company's financial health and performance trends. 
Do not include citations or references to specific data sources."""
                        
                        ai_response = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        ai_summary = ai_response.choices[0].message.content
                except Exception:
                    pass
                
                return JsonResponse({
                    'ticker': ticker,
                    'form_type': form_type_used,
                    'date': found_dates[0] if found_dates else None,
                    'summary': ai_summary
                })
            else:
                return JsonResponse({'error': f'SEC API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405) 
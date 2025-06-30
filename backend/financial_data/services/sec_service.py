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
    """Get SEC filing links for a given stock ticker"""
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
            
            # SEC Edgar API endpoint for submissions
            sec_api_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            
            # SEC requires a User-Agent header
            headers = {
                'User-Agent': 'Financial Data API (contact@example.com)'
            }
            
            # Make request to SEC API
            response = requests.get(sec_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract recent filings
                recent_filings = data.get('filings', {}).get('recent', {})
                
                # Create filing links
                filing_links = []
                accession_numbers = recent_filings.get('accessionNumber', [])
                filing_dates = recent_filings.get('filingDate', [])
                forms = recent_filings.get('form', [])
                primary_documents = recent_filings.get('primaryDocument', [])
                
                for i in range(min(10, len(accession_numbers))):  # Get latest 10 filings
                    accession_no = accession_numbers[i]
                    # Format accession number for URL (remove dashes)
                    accession_formatted = accession_no.replace('-', '')
                    
                    filing_link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_formatted}/{primary_documents[i]}"
                    
                    filing_links.append({
                        'form': forms[i],
                        'filing_date': filing_dates[i],
                        'accession_number': accession_no,
                        'filing_url': filing_link,
                        'edgar_url': f"https://www.sec.gov/edgar/browse/?CIK={cik}&owner=exclude&action=getcompany"
                    })
                
                return JsonResponse({
                    'ticker': ticker,
                    'cik': cik,
                    'company_name': data.get('name', 'N/A'),
                    'recent_filings': filing_links,
                    'total_filings_available': len(accession_numbers),
                    'edgar_search_url': f"https://www.sec.gov/edgar/browse/?CIK={cik}&owner=exclude&action=getcompany",
                    'status': 'success'
                })
            else:
                return JsonResponse({
                    'error': f'Failed to fetch data from SEC API. Status code: {response.status_code}',
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
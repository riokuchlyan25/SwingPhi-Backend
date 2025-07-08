# internal
from financial_data.config import FMP_API_KEY

# external
import requests
from django.http import JsonResponse
import json
from datetime import datetime, timedelta

# built-in

def get_earnings_calendar_api(request):
    """Get simplified earnings calendar data with earnings/guidance tagging"""
    if request.method == 'GET':
        from_date = request.GET.get('from_date', datetime.now().strftime('%Y-%m-%d'))
        to_date = request.GET.get('to_date', (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            fmp_url = f"https://financialmodelingprep.com/api/v3/earning_calendar"
            params = {
                'from': from_date,
                'to': to_date,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(fmp_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and data.get('Error Message'):
                    return JsonResponse({'error': data.get('Error Message')}, status=400)
                
                # Simplified earnings data - only entries with meaningful data
                simplified_earnings = []
                if isinstance(data, list):
                    for earning in data:
                        if (earning and 
                            earning.get('symbol') and 
                            earning.get('date') and
                            (earning.get('epsEstimated') is not None or earning.get('eps') is not None)):
                            
                            eps_est = earning.get('epsEstimated')
                            eps_act = earning.get('eps')
                            
                            # Only include if we have at least one meaningful EPS value
                            if eps_est is not None or eps_act is not None:
                                # Calculate surprise only if both values exist and are valid
                                surprise = None
                                if eps_est is not None and eps_act is not None and eps_est != 0:
                                    try:
                                        surprise = round(((float(eps_act) - float(eps_est)) / abs(float(eps_est))) * 100, 2)
                                    except (ValueError, TypeError, ZeroDivisionError):
                                        surprise = None
                                
                                # Tag as earnings or guidance based on whether actual results are available
                                tag = "earnings" if eps_act is not None else "guidance"
                                
                                simplified_earnings.append({
                                    'symbol': earning['symbol'],
                                    'date': earning['date'],
                                    'eps_estimated': eps_est,
                                    'eps_actual': eps_act,
                                    'surprise_percent': surprise,
                                    'tag': tag,
                                    'type': 'historical' if eps_act is not None else 'upcoming'
                                })
                
                return JsonResponse({
                    'from_date': from_date,
                    'to_date': to_date,
                    'count': len(simplified_earnings),
                    'earnings': simplified_earnings
                })
            else:
                return JsonResponse({'error': f'API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_earnings_for_symbol_api(request):
    """Get simplified earnings data for specific symbol with earnings/guidance tagging"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
            params = {'apikey': FMP_API_KEY}
            
            response = requests.get(fmp_url, params=params, timeout=30)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                if isinstance(earnings_data, dict) and earnings_data.get('Error Message'):
                    return JsonResponse({'error': earnings_data.get('Error Message')}, status=400)
                
                # Get latest 10 valid earnings reports
                simplified_earnings = []
                if isinstance(earnings_data, list):
                    for earning in earnings_data[:10]:
                        if earning and earning.get('date'):
                            eps_est = earning.get('epsEstimated')
                            eps_act = earning.get('eps')
                            
                            surprise = None
                            if eps_est is not None and eps_act is not None and eps_est != 0:
                                try:
                                    surprise = round(((float(eps_act) - float(eps_est)) / abs(float(eps_est))) * 100, 2)
                                except (ValueError, TypeError, ZeroDivisionError):
                                    surprise = None
                            
                            # Tag as earnings or guidance based on whether actual results are available
                            tag = "earnings" if eps_act is not None else "guidance"
                            
                            simplified_earnings.append({
                                'date': earning['date'],
                                'quarter': earning.get('fiscalDateEnding', '')[:7] if earning.get('fiscalDateEnding') else '',
                                'eps_estimated': eps_est,
                                'eps_actual': eps_act,
                                'surprise_percent': surprise,
                                'tag': tag,
                                'type': 'historical' if eps_act is not None else 'upcoming'
                            })
                
                return JsonResponse({
                    'symbol': symbol,
                    'earnings': simplified_earnings
                })
            else:
                return JsonResponse({'error': f'API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_upcoming_earnings_api(request):
    """Get upcoming earnings for maximum available days"""
    if request.method == 'GET':
        # Allow custom days parameter or use maximum available
        days = request.GET.get('days', 'max')
        
        if not FMP_API_KEY:
            return JsonResponse({
                'error': 'FMP API key not configured',
                'status': 'error'
            }, status=500)
        
        try:
            # Get earnings for maximum available period or custom days
            from_date = datetime.now().strftime('%Y-%m-%d')
            
            if days == 'max':
                # Try to get earnings for the next 365 days (maximum available)
                to_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
                max_days = 365
            else:
                try:
                    days_int = int(days)
                    days_int = min(days_int, 365)  # Cap at 365 days
                    to_date = (datetime.now() + timedelta(days=days_int)).strftime('%Y-%m-%d')
                    max_days = days_int
                except ValueError:
                    return JsonResponse({
                        'error': 'Invalid days parameter. Use integer or "max"',
                        'status': 'error'
                    }, status=400)
            
            # FMP earnings calendar endpoint
            fmp_url = f"https://financialmodelingprep.com/api/v3/earning_calendar"
            params = {
                'from': from_date,
                'to': to_date,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(fmp_url, params=params)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                # Group by date and filter for upcoming only
                upcoming_earnings = {}
                total_upcoming = 0
                
                for earning in earnings_data:
                    if earning.get('eps') is None:  # Only upcoming earnings
                        date = earning.get('date', 'N/A')
                        if date not in upcoming_earnings:
                            upcoming_earnings[date] = []
                        
                        # Add earnings/guidance tagging
                        tag = "guidance" if earning.get('eps') is None else "earnings"
                        
                        upcoming_earnings[date].append({
                            'symbol': earning.get('symbol', 'N/A'),
                            'company_name': earning.get('companyName', 'N/A'),
                            'quarter': earning.get('quarter', 'N/A'),
                            'eps_estimated': earning.get('epsEstimated', None),
                            'revenue_estimated': earning.get('revenueEstimated', None),
                            'time': earning.get('time', 'N/A'),
                            'tag': tag,
                            'type': 'upcoming'
                        })
                        total_upcoming += 1
                
                # Sort dates
                sorted_dates = sorted(upcoming_earnings.keys())
                sorted_upcoming = {date: upcoming_earnings[date] for date in sorted_dates}
                
                # Calculate statistics
                date_count = len(sorted_dates)
                furthest_date = sorted_dates[-1] if sorted_dates else from_date
                
                # Calculate actual days covered
                try:
                    furthest_date_obj = datetime.strptime(furthest_date, '%Y-%m-%d')
                    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
                    actual_days_covered = (furthest_date_obj - from_date_obj).days
                except:
                    actual_days_covered = 0
                
                return JsonResponse({
                    'days_requested': max_days,
                    'days_covered': actual_days_covered,
                    'total_earnings': total_upcoming,
                    'earnings_by_date': sorted_upcoming
                })
            else:
                return JsonResponse({
                    'error': f'Failed to fetch upcoming earnings from FMP API. Status code: {response.status_code}',
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

def get_earnings_insights_api(request):
    """Get simplified earnings insights for stock array"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symbols = data.get('symbols', [])
            
            if not symbols:
                return JsonResponse({'error': 'Symbols array required'}, status=400)
            
            if not FMP_API_KEY:
                return JsonResponse({'error': 'API key not configured'}, status=500)
            
            # Simplified analysis
            beats = 0
            misses = 0
            inline = 0
            total_analyzed = 0
            surprise_percentages = []
            
            for symbol in symbols:
                try:
                    fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
                    params = {'apikey': FMP_API_KEY}
                    
                    response = requests.get(fmp_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        earnings_data = response.json()
                        
                        if earnings_data and isinstance(earnings_data, list) and len(earnings_data) > 0:
                            # Look through recent earnings to find actual vs estimated data
                            for earning in earnings_data[:10]:  # Check last 10 earnings reports
                                eps_est = earning.get('epsEstimated')
                                eps_act = earning.get('eps')
                                
                                # More flexible criteria - we need both estimated and actual, but allow zero values
                                if (eps_est is not None and eps_act is not None and 
                                    isinstance(eps_est, (int, float)) and isinstance(eps_act, (int, float))):
                                    
                                    total_analyzed += 1
                                    try:
                                        # Handle case where estimate is zero
                                        if abs(eps_est) < 0.001:  # Very small number, treat as zero
                                            if eps_act > 0:
                                                surprise = 100  # Beat by 100% if estimate was zero
                                            elif eps_act < 0:
                                                surprise = -100  # Miss by 100% if estimate was zero
                                            else:
                                                surprise = 0  # Inline if both are zero
                                        else:
                                            surprise = ((float(eps_act) - float(eps_est)) / abs(float(eps_est))) * 100
                                        
                                        surprise_percentages.append(surprise)
                                        
                                        if surprise > 5:  # Beat by more than 5%
                                            beats += 1
                                        elif surprise < -5:  # Miss by more than 5%
                                            misses += 1
                                        else:
                                            inline += 1
                                        break  # Only analyze the most recent valid earnings
                                    except (ValueError, TypeError, ZeroDivisionError):
                                        continue
                except Exception:
                    continue
            
            if total_analyzed == 0:
                return JsonResponse({'error': 'No valid earnings data found for any symbols'})
            
            avg_surprise = round(sum(surprise_percentages) / len(surprise_percentages), 2) if surprise_percentages else 0
            beat_rate = round((beats / total_analyzed) * 100, 1)
            miss_rate = round((misses / total_analyzed) * 100, 1)
            
            return JsonResponse({
                'symbols_analyzed': total_analyzed,
                'beats': beats,
                'misses': misses,
                'inline': inline,
                'beat_rate': beat_rate,
                'miss_rate': miss_rate,
                'avg_surprise': avg_surprise
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'POST required'}, status=405)

def get_earnings_insights_by_date_api(request):
    """Get earnings insights for companies reporting on a specific date"""
    if request.method == 'GET':
        target_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not FMP_API_KEY:
            return JsonResponse({
                'error': 'FMP API key not configured',
                'status': 'error'
            }, status=500)
        
        try:
            # Get earnings calendar for the specific date
            fmp_url = f"https://financialmodelingprep.com/api/v3/earning_calendar"
            params = {
                'from': target_date,
                'to': target_date,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(fmp_url, params=params)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                if not earnings_data:
                    return JsonResponse({
                        'date': target_date,
                        'message': 'No earnings reported on this date',
                        'status': 'success'
                    })
                
                # Extract symbols for analysis
                symbols = [earning.get('symbol') for earning in earnings_data if earning.get('symbol')]
                
                # Use the existing insights function logic but with the symbols from the date
                return get_earnings_insights_for_symbols(symbols, target_date)
            
            else:
                return JsonResponse({
                    'error': f'Failed to fetch earnings calendar from FMP API. Status code: {response.status_code}',
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

def get_earnings_insights_for_symbols(symbols, analysis_date=None):
    """Helper function to get insights for a list of symbols with guidance analysis"""
    if not analysis_date:
        analysis_date = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize tracking variables
    total_companies = len(symbols)
    companies_with_data = 0
    earnings_beat = 0
    earnings_missed = 0
    earnings_inline = 0
    not_reported = 0
    
    # Guidance tracking variables
    guidance_raised = 0
    guidance_lowered = 0
    guidance_maintained = 0
    guidance_available = 0
    
    surprise_percentages = []
    revenue_growth_rates = []
    positive_earnings_count = 0
    
    company_details = []
    
    # Analyze each symbol
    for symbol in symbols:
        try:
            # Get historical earnings for each symbol
            fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
            params = {'apikey': FMP_API_KEY}
            
            response = requests.get(fmp_url, params=params)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                if earnings_data:
                    companies_with_data += 1
                    latest_earning = earnings_data[0]  # Most recent earning
                    
                    eps_estimated = latest_earning.get('epsEstimated')
                    eps_actual = latest_earning.get('eps')
                    revenue_estimated = latest_earning.get('revenueEstimated')
                    revenue_actual = latest_earning.get('revenueActual')
                    
                    # Get guidance data if available (look for upcoming quarters)
                    guidance_data = None
                    guidance_status = "not_available"
                    
                    # Check if there's guidance information in next earnings
                    if len(earnings_data) > 1:
                        next_earning = earnings_data[1]
                        next_eps_est = next_earning.get('epsEstimated')
                        current_eps_est = eps_estimated
                        
                        if next_eps_est is not None and current_eps_est is not None:
                            guidance_available += 1
                            if next_eps_est > current_eps_est:
                                guidance_raised += 1
                                guidance_status = "raised"
                            elif next_eps_est < current_eps_est:
                                guidance_lowered += 1
                                guidance_status = "lowered"
                            else:
                                guidance_maintained += 1
                                guidance_status = "maintained"
                    
                    # Tag as earnings or guidance based on actual results availability
                    tag = "earnings" if eps_actual is not None else "guidance"
                    
                    company_detail = {
                        'symbol': symbol,
                        'date': latest_earning.get('date', 'N/A'),
                        'quarter': latest_earning.get('quarter', 'N/A'),
                        'eps_estimated': eps_estimated,
                        'eps_actual': eps_actual,
                        'revenue_estimated': revenue_estimated,
                        'revenue_actual': revenue_actual,
                        'surprise_percentage': None,
                        'revenue_growth': None,
                        'status': 'not_reported',
                        'tag': tag,
                        'guidance_status': guidance_status,
                        'type': 'historical' if eps_actual is not None else 'upcoming'
                    }
                    
                    # Analyze earnings performance
                    if eps_actual is not None and eps_estimated is not None:
                        if eps_estimated != 0:
                            surprise_pct = ((eps_actual - eps_estimated) / abs(eps_estimated)) * 100
                            surprise_percentages.append(surprise_pct)
                            company_detail['surprise_percentage'] = round(surprise_pct, 2)
                            
                            # Categorize earnings performance (within 2% considered inline)
                            if surprise_pct > 2:
                                earnings_beat += 1
                                company_detail['status'] = 'beat'
                            elif surprise_pct < -2:
                                earnings_missed += 1
                                company_detail['status'] = 'missed'
                            else:
                                earnings_inline += 1
                                company_detail['status'] = 'inline'
                        
                        # Check for positive earnings
                        if eps_actual > 0:
                            positive_earnings_count += 1
                    else:
                        not_reported += 1
                    
                    # Calculate revenue growth
                    if revenue_actual is not None and revenue_estimated is not None and revenue_estimated != 0:
                        revenue_growth = ((revenue_actual - revenue_estimated) / abs(revenue_estimated)) * 100
                        revenue_growth_rates.append(revenue_growth)
                        company_detail['revenue_growth'] = round(revenue_growth, 2)
                    
                    company_details.append(company_detail)
                else:
                    not_reported += 1
                    company_details.append({
                        'symbol': symbol,
                        'status': 'no_data',
                        'tag': 'no_data',
                        'error': 'No earnings data available'
                    })
            
        except Exception as symbol_error:
            company_details.append({
                'symbol': symbol,
                'status': 'error',
                'tag': 'error',
                'error': str(symbol_error)
            })
    
    # Calculate summary statistics
    avg_surprise = round(sum(surprise_percentages) / len(surprise_percentages), 2) if surprise_percentages else 0
    avg_revenue_growth = round(sum(revenue_growth_rates) / len(revenue_growth_rates), 2) if revenue_growth_rates else 0
    
    # Calculate rates
    reported_companies = earnings_beat + earnings_missed + earnings_inline
    beat_rate = round((earnings_beat / reported_companies) * 100, 2) if reported_companies > 0 else 0
    miss_rate = round((earnings_missed / reported_companies) * 100, 2) if reported_companies > 0 else 0
    inline_rate = round((earnings_inline / reported_companies) * 100, 2) if reported_companies > 0 else 0
    positive_earnings_rate = round((positive_earnings_count / companies_with_data) * 100, 2) if companies_with_data > 0 else 0
    
    # Calculate guidance rates
    guidance_raised_rate = round((guidance_raised / guidance_available) * 100, 2) if guidance_available > 0 else 0
    guidance_lowered_rate = round((guidance_lowered / guidance_available) * 100, 2) if guidance_available > 0 else 0
    guidance_maintained_rate = round((guidance_maintained / guidance_available) * 100, 2) if guidance_available > 0 else 0
    
    return JsonResponse({
        'symbols_analyzed': companies_with_data,
        'earnings': {
            'beat': earnings_beat,
            'missed': earnings_missed,
            'inline': earnings_inline,
            'beat_rate': beat_rate,
            'miss_rate': miss_rate
        },
        'guidance': {
            'raised': guidance_raised,
            'lowered': guidance_lowered,
            'beat_expectations': guidance_beat_expectations,
            'miss_expectations': guidance_miss_expectations,
            'accuracy': avg_guidance_accuracy
        },
        'avg_surprise': avg_surprise,
        'avg_revenue_growth': avg_revenue_growth,
        'companies': company_details
    })

def get_comprehensive_earnings_insights_api(request):
    """Get comprehensive earnings insights with guidance implementation for array of stocks"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symbols = data.get('symbols', [])
            
            if not symbols:
                return JsonResponse({'error': 'Symbols array required'}, status=400)
            
            if not FMP_API_KEY:
                return JsonResponse({'error': 'API key not configured'}, status=500)
            
            # Initialize comprehensive tracking variables
            total_companies = len(symbols)
            companies_with_data = 0
            
            # Earnings performance tracking
            earnings_beat = 0
            earnings_missed = 0
            earnings_inline = 0
            not_reported = 0
            
            # Guidance tracking with enhanced formula
            guidance_raised = 0
            guidance_lowered = 0
            guidance_maintained = 0
            guidance_available = 0
            guidance_beat_expectations = 0
            guidance_miss_expectations = 0
            
            # KPIs tracking
            positive_earnings_count = 0
            revenue_growth_positive = 0
            low_margin_companies = 0
            
            # Performance metrics
            surprise_percentages = []
            revenue_growth_rates = []
            guidance_accuracy_scores = []
            
            company_details = []
            
            # Analyze each symbol comprehensively
            for symbol in symbols:
                try:
                    # Get historical earnings data
                    fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
                    params = {'apikey': FMP_API_KEY}
                    
                    response = requests.get(fmp_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        earnings_data = response.json()
                        
                        if earnings_data and isinstance(earnings_data, list):
                            companies_with_data += 1
                            
                            # Get latest and previous earnings for guidance analysis
                            latest_earning = earnings_data[0] if len(earnings_data) > 0 else {}
                            previous_earning = earnings_data[1] if len(earnings_data) > 1 else {}
                            
                            eps_estimated = latest_earning.get('epsEstimated')
                            eps_actual = latest_earning.get('eps')
                            revenue_estimated = latest_earning.get('revenueEstimated')
                            revenue_actual = latest_earning.get('revenueActual')
                            
                            # Initialize company detail record
                            company_detail = {
                                'symbol': symbol,
                                'date': latest_earning.get('date', 'N/A'),
                                'quarter': latest_earning.get('quarter', 'N/A'),
                                'eps_estimated': eps_estimated,
                                'eps_actual': eps_actual,
                                'revenue_estimated': revenue_estimated,
                                'revenue_actual': revenue_actual,
                                'surprise_percentage': None,
                                'revenue_growth': None,
                                'guidance_status': 'not_available',
                                'guidance_accuracy': None,
                                'kpi_score': 0,
                                'tag': 'earnings' if eps_actual is not None else 'guidance',
                                'type': 'historical' if eps_actual is not None else 'upcoming'
                            }
                            
                            # Analyze earnings performance
                            if eps_actual is not None and eps_estimated is not None:
                                if eps_estimated != 0:
                                    surprise_pct = ((eps_actual - eps_estimated) / abs(eps_estimated)) * 100
                                    surprise_percentages.append(surprise_pct)
                                    company_detail['surprise_percentage'] = round(surprise_pct, 2)
                                    
                                    # Categorize earnings performance
                                    if surprise_pct > 2:
                                        earnings_beat += 1
                                        company_detail['earnings_status'] = 'beat'
                                    elif surprise_pct < -2:
                                        earnings_missed += 1
                                        company_detail['earnings_status'] = 'missed'
                                    else:
                                        earnings_inline += 1
                                        company_detail['earnings_status'] = 'inline'
                                
                                # Check for positive earnings KPI
                                if eps_actual > 0:
                                    positive_earnings_count += 1
                                    company_detail['kpi_score'] += 1
                            else:
                                not_reported += 1
                                company_detail['earnings_status'] = 'not_reported'
                            
                            # Revenue growth analysis
                            if revenue_actual is not None and revenue_estimated is not None and revenue_estimated != 0:
                                revenue_growth = ((revenue_actual - revenue_estimated) / abs(revenue_estimated)) * 100
                                revenue_growth_rates.append(revenue_growth)
                                company_detail['revenue_growth'] = round(revenue_growth, 2)
                                
                                if revenue_growth > 0:
                                    revenue_growth_positive += 1
                                    company_detail['kpi_score'] += 1
                            
                            # Guidance analysis with enhanced formula
                            if previous_earning:
                                prev_eps_est = previous_earning.get('epsEstimated')
                                prev_eps_actual = previous_earning.get('eps')
                                
                                # Guidance accuracy calculation
                                if (prev_eps_est is not None and prev_eps_actual is not None and 
                                    eps_estimated is not None and eps_actual is not None):
                                    
                                    guidance_available += 1
                                    
                                    # Calculate guidance accuracy score
                                    prev_guidance_error = abs(prev_eps_actual - prev_eps_est) / abs(prev_eps_est) if prev_eps_est != 0 else 0
                                    current_guidance_error = abs(eps_actual - eps_estimated) / abs(eps_estimated) if eps_estimated != 0 else 0
                                    
                                    # Guidance improved if current error is smaller
                                    if current_guidance_error < prev_guidance_error:
                                        guidance_beat_expectations += 1
                                        company_detail['guidance_status'] = 'beat_expectations'
                                        guidance_accuracy_score = 100 - (current_guidance_error * 100)
                                    elif current_guidance_error > prev_guidance_error:
                                        guidance_miss_expectations += 1
                                        company_detail['guidance_status'] = 'miss_expectations'
                                        guidance_accuracy_score = 100 - (current_guidance_error * 100)
                                    else:
                                        guidance_maintained += 1
                                        company_detail['guidance_status'] = 'maintained'
                                        guidance_accuracy_score = 100 - (current_guidance_error * 100)
                                    
                                    guidance_accuracy_scores.append(guidance_accuracy_score)
                                    company_detail['guidance_accuracy'] = round(guidance_accuracy_score, 2)
                                    
                                    # Guidance direction analysis
                                    if eps_estimated > prev_eps_est:
                                        guidance_raised += 1
                                        company_detail['guidance_direction'] = 'raised'
                                    elif eps_estimated < prev_eps_est:
                                        guidance_lowered += 1
                                        company_detail['guidance_direction'] = 'lowered'
                                    else:
                                        company_detail['guidance_direction'] = 'maintained'
                            
                            # Calculate margin analysis (simplified)
                            if revenue_actual is not None and eps_actual is not None and revenue_actual != 0:
                                # Estimate margin based on EPS/Revenue ratio
                                estimated_margin = (eps_actual / revenue_actual) * 100
                                if estimated_margin < 5:  # Low margin threshold
                                    low_margin_companies += 1
                                    company_detail['low_margin'] = True
                                else:
                                    company_detail['low_margin'] = False
                                    company_detail['kpi_score'] += 1
                            
                            company_details.append(company_detail)
                            
                except Exception as symbol_error:
                    company_details.append({
                        'symbol': symbol,
                        'status': 'error',
                        'error': str(symbol_error)
                    })
            
            # Calculate comprehensive metrics
            reported_companies = earnings_beat + earnings_missed + earnings_inline
            
            # Performance rates
            beat_rate = round((earnings_beat / reported_companies) * 100, 2) if reported_companies > 0 else 0
            miss_rate = round((earnings_missed / reported_companies) * 100, 2) if reported_companies > 0 else 0
            inline_rate = round((earnings_inline / reported_companies) * 100, 2) if reported_companies > 0 else 0
            
            # Guidance rates
            guidance_beat_rate = round((guidance_beat_expectations / guidance_available) * 100, 2) if guidance_available > 0 else 0
            guidance_miss_rate = round((guidance_miss_expectations / guidance_available) * 100, 2) if guidance_available > 0 else 0
            guidance_raised_rate = round((guidance_raised / guidance_available) * 100, 2) if guidance_available > 0 else 0
            guidance_lowered_rate = round((guidance_lowered / guidance_available) * 100, 2) if guidance_available > 0 else 0
            
            # KPI rates
            positive_earnings_rate = round((positive_earnings_count / companies_with_data) * 100, 2) if companies_with_data > 0 else 0
            revenue_growth_rate = round((revenue_growth_positive / companies_with_data) * 100, 2) if companies_with_data > 0 else 0
            low_margin_rate = round((low_margin_companies / companies_with_data) * 100, 2) if companies_with_data > 0 else 0
            
            # Average metrics
            avg_surprise = round(sum(surprise_percentages) / len(surprise_percentages), 2) if surprise_percentages else 0
            avg_revenue_growth = round(sum(revenue_growth_rates) / len(revenue_growth_rates), 2) if revenue_growth_rates else 0
            avg_guidance_accuracy = round(sum(guidance_accuracy_scores) / len(guidance_accuracy_scores), 2) if guidance_accuracy_scores else 0
            
            return JsonResponse({
                'symbols_analyzed': companies_with_data,
                'earnings': {
                    'beat': earnings_beat,
                    'missed': earnings_missed,
                    'inline': earnings_inline,
                    'beat_rate': beat_rate,
                    'miss_rate': miss_rate
                },
                'guidance': {
                    'raised': guidance_raised,
                    'lowered': guidance_lowered,
                    'beat_expectations': guidance_beat_expectations,
                    'miss_expectations': guidance_miss_expectations,
                    'accuracy': avg_guidance_accuracy
                },
                'avg_surprise': avg_surprise,
                'avg_revenue_growth': avg_revenue_growth,
                'companies': company_details
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'POST required'}, status=405)

def get_earnings_correlation_api(request):
    """Get earnings correlation analysis for a stock with cloud revenue, AI/ML growth, chip demand, enterprise spending"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            # Get historical earnings data for the symbol
            fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
            params = {'apikey': FMP_API_KEY}
            
            response = requests.get(fmp_url, params=params, timeout=30)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                if not earnings_data:
                    return JsonResponse({'error': 'No earnings data available for this symbol'}, status=404)
                
                # Extract recent earnings performance
                recent_earnings = earnings_data[:8]  # Last 8 quarters
                earnings_surprises = []
                
                for earning in recent_earnings:
                    eps_est = earning.get('epsEstimated')
                    eps_act = earning.get('eps')
                    
                    if eps_est is not None and eps_act is not None and eps_est != 0:
                        surprise = ((eps_act - eps_est) / abs(eps_est)) * 100
                        earnings_surprises.append({
                            'quarter': earning.get('quarter', 'N/A'),
                            'date': earning.get('date', 'N/A'),
                            'surprise_percent': round(surprise, 2),
                            'eps_actual': eps_act,
                            'eps_estimated': eps_est
                        })
                
                # AI-Generated Correlation Analysis
                correlation_analysis = {}
                
                try:
                    from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
                    from openai import AzureOpenAI
                    
                    if all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                        client = AzureOpenAI(
                            api_key=AZURE_OPENAI_KEY,
                            api_version="2023-05-15",
                            azure_endpoint=AZURE_OPENAI_ENDPOINT
                        )
                        
                        # Create analysis prompts for each correlation factor
                        correlation_factors = {
                            'cloud_revenue': f"Analyze how {symbol}'s earnings performance over the last 8 quarters correlates with cloud computing market growth and enterprise cloud adoption trends. Consider cloud infrastructure spending, SaaS growth, and digital transformation initiatives.",
                            'ai_ml_growth': f"Evaluate the correlation between {symbol}'s earnings and AI/ML market expansion. Consider AI hardware demand, machine learning software adoption, and AI-driven business transformation across industries.",
                            'chip_demand': f"Assess how {symbol}'s earnings correlate with semiconductor industry trends and chip demand. Consider factors like data center chip requirements, automotive semiconductors, consumer electronics, and supply chain dynamics.",
                            'enterprise_spending': f"Analyze the relationship between {symbol}'s earnings performance and enterprise IT spending patterns. Consider enterprise software budgets, infrastructure investments, and corporate digital transformation spending."
                        }
                        
                        for factor, prompt in correlation_factors.items():
                            try:
                                full_prompt = f"{prompt}\n\nBased on recent market trends and the company's business model, provide a brief 2-sentence analysis focusing on the correlation strength (High/Medium/Low) and key factors driving the relationship. Do not include citations."
                                
                                ai_response = client.chat.completions.create(
                                    model=MODEL_NAME,
                                    messages=[{"role": "user", "content": full_prompt}]
                                )
                                
                                analysis_text = ai_response.choices[0].message.content.strip()
                                
                                # Extract correlation strength from the response
                                if 'high' in analysis_text.lower():
                                    correlation_strength = 'High'
                                elif 'medium' in analysis_text.lower():
                                    correlation_strength = 'Medium'
                                elif 'low' in analysis_text.lower():
                                    correlation_strength = 'Low'
                                else:
                                    correlation_strength = 'Unknown'
                                
                                correlation_analysis[factor] = {
                                    'correlation_strength': correlation_strength,
                                    'analysis': analysis_text,
                                    'factor_name': factor.replace('_', ' ').title()
                                }
                                
                            except Exception as factor_error:
                                correlation_analysis[factor] = {
                                    'correlation_strength': 'Unknown',
                                    'analysis': f'Analysis unavailable: {str(factor_error)}',
                                    'factor_name': factor.replace('_', ' ').title()
                                }
                    
                    else:
                        # Fallback analysis without AI
                        correlation_analysis = {
                            'cloud_revenue': {
                                'correlation_strength': 'Unknown',
                                'analysis': 'AI analysis unavailable. Cloud revenue correlation depends on company\'s exposure to cloud computing market.',
                                'factor_name': 'Cloud Revenue'
                            },
                            'ai_ml_growth': {
                                'correlation_strength': 'Unknown',
                                'analysis': 'AI analysis unavailable. AI/ML growth correlation varies by company\'s technology sector involvement.',
                                'factor_name': 'AI/ML Growth'
                            },
                            'chip_demand': {
                                'correlation_strength': 'Unknown',
                                'analysis': 'AI analysis unavailable. Chip demand correlation depends on semiconductor industry exposure.',
                                'factor_name': 'Chip Demand'
                            },
                            'enterprise_spending': {
                                'correlation_strength': 'Unknown',
                                'analysis': 'AI analysis unavailable. Enterprise spending correlation varies by business model and customer base.',
                                'factor_name': 'Enterprise Spending'
                            }
                        }
                
                except Exception as ai_error:
                    correlation_analysis = {
                        'error': f'AI correlation analysis failed: {str(ai_error)}'
                    }
                
                # Calculate earnings performance metrics
                avg_surprise = round(sum(item['surprise_percent'] for item in earnings_surprises) / len(earnings_surprises), 2) if earnings_surprises else 0
                positive_surprises = sum(1 for item in earnings_surprises if item['surprise_percent'] > 0)
                beat_rate = round((positive_surprises / len(earnings_surprises)) * 100, 2) if earnings_surprises else 0
                
                return JsonResponse({
                    'symbol': symbol,
                    'avg_surprise': avg_surprise,
                    'beat_rate': beat_rate,
                    'correlations': correlation_analysis
                })
                
            else:
                return JsonResponse({'error': f'FMP API error: {response.status_code}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)
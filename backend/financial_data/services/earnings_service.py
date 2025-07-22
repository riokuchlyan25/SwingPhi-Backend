# internal
from financial_data.config import FMP_API_KEY

# external
import requests
import json
from datetime import datetime, timedelta

# built-in
from django.http import JsonResponse

def calculate_earnings_surprise_percentage(eps_actual, eps_estimated):
    """
    Calculate earnings surprise percentage with proper mathematical handling
    
    Formula: ((actual - estimated) / |estimated|) * 100
    Special cases:
    - If estimated is 0 and actual > 0: +100% (perfect beat)
    - If estimated is 0 and actual < 0: -100% (complete miss)  
    - If estimated is 0 and actual = 0: 0% (inline)
    - If estimated is negative: handle properly without abs()
    """
    try:
        eps_actual = float(eps_actual)
        eps_estimated = float(eps_estimated)
        
        # Handle zero estimate case
        if abs(eps_estimated) < 0.001:  # Treat very small numbers as zero
            if eps_actual > 0.001:
                return 100.0  # Beat by 100%
            elif eps_actual < -0.001:
                return -100.0  # Miss by 100%
            else:
                return 0.0  # Inline
        
        # Standard calculation - use estimated value directly, not abs()
        # This properly handles negative estimates
        surprise_pct = ((eps_actual - eps_estimated) / eps_estimated) * 100
        
        # Cap extreme values for sanity
        return max(-500.0, min(500.0, surprise_pct))
        
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def calculate_revenue_growth_percentage(revenue_actual, revenue_estimated):
    """
    Calculate revenue growth percentage with proper mathematical handling
    """
    try:
        revenue_actual = float(revenue_actual)
        revenue_estimated = float(revenue_estimated)
        
        # Revenue should always be positive, so abs() is appropriate here
        if abs(revenue_estimated) < 0.001:
            return None  # Can't calculate growth without baseline
        
        growth_pct = ((revenue_actual - revenue_estimated) / abs(revenue_estimated)) * 100
        
        # Cap extreme values
        return max(-100.0, min(1000.0, growth_pct))
        
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def calculate_guidance_accuracy_score(current_error, previous_error=None):
    """
    Calculate guidance accuracy score with proper bounds
    
    Returns accuracy score from 0-100 where:
    - 100 = perfect accuracy (0% error)
    - 0 = completely inaccurate (100%+ error)
    """
    try:
        # Ensure error is within reasonable bounds
        current_error = max(0.0, min(10.0, float(current_error)))  # Cap at 1000% error
        
        # Convert error percentage to accuracy score
        accuracy = max(0.0, 100.0 - (current_error * 100))
        
        return round(accuracy, 2)
        
    except (ValueError, TypeError):
        return 50.0  # Default neutral score

def calculate_percentage_rate(numerator, denominator):
    """
    Calculate percentage rate with proper zero division protection
    """
    try:
        if denominator <= 0:
            return 0.0
        return round((float(numerator) / float(denominator)) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

def get_earnings_calendar_api(request):
    """Get earnings calendar for date range with simplified data format"""
    if request.method == 'GET':
        from_date = request.GET.get('from_date', '')
        to_date = request.GET.get('to_date', '')
        
        if not from_date or not to_date:
            return JsonResponse({'error': 'Both from_date and to_date required (YYYY-MM-DD format)'}, status=400)
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            fmp_url = f"https://financialmodelingprep.com/api/v3/earning_calendar"
            params = {
                'from': from_date,
                'to': to_date,
                'apikey': FMP_API_KEY
            }
            
            response = requests.get(fmp_url, params=params, timeout=15)
            
            if response.status_code == 200:
                earnings_data = response.json()
                simplified_earnings = []
                
                for earning in earnings_data:
                    if earning and earning.get('date'):
                        eps_est = earning.get('epsEstimated')
                        eps_act = earning.get('eps')
                        
                        # Only include if we have at least one meaningful EPS value
                        if eps_est is not None or eps_act is not None:
                            # Use improved surprise calculation
                            surprise = calculate_earnings_surprise_percentage(eps_act, eps_est) if (eps_est is not None and eps_act is not None) else None
                            
                            # Tag as earnings or guidance based on whether actual results are available
                            tag = "earnings" if eps_act is not None else "guidance"
                            
                            simplified_earnings.append({
                                'symbol': earning['symbol'],
                                'date': earning['date'],
                                'eps_estimated': eps_est,
                                'eps_actual': eps_act,
                                'surprise_percent': round(surprise, 2) if surprise is not None else None,
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
        return JsonResponse({'error': 'GET method required'}, status=405)

def get_earnings_for_symbol_api(request):
    """Get historical earnings for specific symbol with simplified data format"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'API key not configured'}, status=500)
        
        try:
            fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
            params = {'apikey': FMP_API_KEY}
            
            response = requests.get(fmp_url, params=params, timeout=15)
            
            if response.status_code == 200:
                earnings_data = response.json()
                simplified_earnings = []
                
                if isinstance(earnings_data, list):
                    for earning in earnings_data[:10]:
                        if earning and earning.get('date'):
                            eps_est = earning.get('epsEstimated')
                            eps_act = earning.get('eps')
                            
                            # Use improved surprise calculation
                            surprise = calculate_earnings_surprise_percentage(eps_act, eps_est) if (eps_est is not None and eps_act is not None) else None
                            
                            # Tag as earnings or guidance based on whether actual results are available
                            tag = "earnings" if eps_act is not None else "guidance"
                            
                            simplified_earnings.append({
                                'date': earning['date'],
                                'quarter': earning.get('fiscalDateEnding', '')[:7] if earning.get('fiscalDateEnding') else '',
                                'eps_estimated': eps_est,
                                'eps_actual': eps_act,
                                'surprise_percent': round(surprise, 2) if surprise is not None else None,
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
        return JsonResponse({'error': 'GET method required'}, status=405)

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
                                        # Use improved surprise calculation
                                        surprise = calculate_earnings_surprise_percentage(eps_act, eps_est)
                                        
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
                    
                    # Analyze earnings performance using improved calculation
                    if eps_actual is not None and eps_estimated is not None:
                        surprise_pct = calculate_earnings_surprise_percentage(eps_actual, eps_estimated)
                        if surprise_pct is not None:
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
                    
                    # Calculate revenue growth using improved calculation
                    if revenue_actual is not None and revenue_estimated is not None:
                        revenue_growth = calculate_revenue_growth_percentage(revenue_actual, revenue_estimated)
                        if revenue_growth is not None:
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
    
    # Calculate rates using improved calculation
    reported_companies = earnings_beat + earnings_missed + earnings_inline
    beat_rate = calculate_percentage_rate(earnings_beat, reported_companies)
    miss_rate = calculate_percentage_rate(earnings_missed, reported_companies)
    inline_rate = calculate_percentage_rate(earnings_inline, reported_companies)
    positive_earnings_rate = calculate_percentage_rate(positive_earnings_count, companies_with_data)
    
    # Calculate guidance rates using improved calculation
    guidance_raised_rate = calculate_percentage_rate(guidance_raised, guidance_available)
    guidance_lowered_rate = calculate_percentage_rate(guidance_lowered, guidance_available)
    guidance_maintained_rate = calculate_percentage_rate(guidance_maintained, guidance_available)
    
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
                            
                            # Analyze earnings performance using improved calculation
                            if eps_actual is not None and eps_estimated is not None:
                                surprise_pct = calculate_earnings_surprise_percentage(eps_actual, eps_estimated)
                                if surprise_pct is not None:
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
                                    
                                    # Calculate guidance accuracy score with improved math
                                    prev_guidance_error = abs(prev_eps_actual - prev_eps_est) / abs(prev_eps_est) if abs(prev_eps_est) > 0.001 else 1.0
                                    current_guidance_error = abs(eps_actual - eps_estimated) / abs(eps_estimated) if abs(eps_estimated) > 0.001 else 1.0
                                    
                                    # Use improved guidance accuracy calculation
                                    guidance_accuracy_score = calculate_guidance_accuracy_score(current_guidance_error)
                                    
                                    # Guidance improved if current error is smaller
                                    if current_guidance_error < prev_guidance_error:
                                        guidance_beat_expectations += 1
                                        company_detail['guidance_status'] = 'beat_expectations'
                                    elif current_guidance_error > prev_guidance_error:
                                        guidance_miss_expectations += 1
                                        company_detail['guidance_status'] = 'miss_expectations'
                                    else:
                                        guidance_maintained += 1
                                        company_detail['guidance_status'] = 'maintained'
                                    
                                    guidance_accuracy_scores.append(guidance_accuracy_score)
                                    company_detail['guidance_accuracy'] = guidance_accuracy_score
                                    
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
            
            # Performance rates using improved calculation
            beat_rate = calculate_percentage_rate(earnings_beat, reported_companies)
            miss_rate = calculate_percentage_rate(earnings_missed, reported_companies)
            inline_rate = calculate_percentage_rate(earnings_inline, reported_companies)
            
            # Guidance rates using improved calculation
            guidance_beat_rate = calculate_percentage_rate(guidance_beat_expectations, guidance_available)
            guidance_miss_rate = calculate_percentage_rate(guidance_miss_expectations, guidance_available)
            guidance_raised_rate = calculate_percentage_rate(guidance_raised, guidance_available)
            guidance_lowered_rate = calculate_percentage_rate(guidance_lowered, guidance_available)
            
            # KPI rates using improved calculation
            positive_earnings_rate = calculate_percentage_rate(positive_earnings_count, companies_with_data)
            revenue_growth_rate = calculate_percentage_rate(revenue_growth_positive, companies_with_data)
            low_margin_rate = calculate_percentage_rate(low_margin_companies, companies_with_data)
            
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
    """Get 4 separate earnings correlation percentages (0-100%) for cloud revenue, AI/ML growth, chip demand, enterprise spending"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        try:
            # Use OpenAI to analyze correlation with tech factors
            from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
            from openai import AzureOpenAI
            
            if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                return JsonResponse({
                    'cloud_revenue': 50,
                    'ai_ml_growth': 50,
                    'chip_demand': 50,
                    'enterprise_spending': 50
                }, status=500)
            
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_KEY,
                api_version="2023-05-15",
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            
            prompt = f"""
            Analyze how strongly {symbol}'s earnings performance correlates with each of these four technology market factors individually:
            
            1. Cloud Revenue: Cloud computing market growth, enterprise cloud adoption, cloud infrastructure spending
            2. AI/ML Growth: AI/ML market expansion, machine learning adoption, AI hardware demand
            3. Chip Demand: Semiconductor industry trends, data center chips, automotive semiconductors, consumer electronics
            4. Enterprise Spending: Enterprise IT spending, corporate software budgets, digital transformation investments
            
            For each factor, provide a correlation percentage from 0-100% where:
            - 0-20% = Very low correlation (minimal exposure)
            - 21-40% = Low correlation (some indirect exposure)
            - 41-60% = Medium correlation (moderate exposure)
            - 61-80% = High correlation (significant exposure)
            - 81-100% = Extremely high correlation (core business dependency)
            
            Based on {symbol}'s business model, industry position, and revenue streams, respond ONLY with a JSON object in this exact format:
            {{
                "cloud_revenue": [0-100 integer],
                "ai_ml_growth": [0-100 integer],
                "chip_demand": [0-100 integer],
                "enterprise_spending": [0-100 integer]
            }}
            """
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a financial correlation analysis expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            try:
                # Try to find JSON in the response (in case there's extra text)
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_response = json_match.group()
                
                result = json.loads(ai_response)
                
                # Extract and validate each correlation percentage
                cloud_revenue = int(result.get('cloud_revenue', 50))
                ai_ml_growth = int(result.get('ai_ml_growth', 50))
                chip_demand = int(result.get('chip_demand', 50))
                enterprise_spending = int(result.get('enterprise_spending', 50))
                
                # Ensure all percentages are within 0-100 range
                cloud_revenue = max(0, min(100, cloud_revenue))
                ai_ml_growth = max(0, min(100, ai_ml_growth))
                chip_demand = max(0, min(100, chip_demand))
                enterprise_spending = max(0, min(100, enterprise_spending))
                
                return JsonResponse({
                    'cloud_revenue': cloud_revenue,
                    'ai_ml_growth': ai_ml_growth,
                    'chip_demand': chip_demand,
                    'enterprise_spending': enterprise_spending
                })
                
            except (json.JSONDecodeError, ValueError, KeyError):
                # Fallback if AI response isn't valid JSON
                return JsonResponse({
                    'cloud_revenue': 50,
                    'ai_ml_growth': 50,
                    'chip_demand': 50,
                    'enterprise_spending': 50
                })
                
        except Exception as e:
            return JsonResponse({
                'cloud_revenue': 50,
                'ai_ml_growth': 50,
                'chip_demand': 50,
                'enterprise_spending': 50
            }, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)

def get_earnings_correlation_impact_api(request):
    """Get earnings correlation data with impact level analysis (high/medium/low) using FMP API and OpenAI"""
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        if not FMP_API_KEY:
            return JsonResponse({'error': 'FMP API key not configured'}, status=500)
        
        try:
            # Get earnings data from FMP API
            fmp_url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
            params = {'apikey': FMP_API_KEY}
            
            response = requests.get(fmp_url, params=params, timeout=15)
            
            if response.status_code == 200:
                earnings_data = response.json()
                
                # Also get company profile for additional context
                profile_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
                profile_response = requests.get(profile_url, params=params, timeout=15)
                company_profile = profile_response.json() if profile_response.status_code == 200 else []
                
                # Use OpenAI to analyze earnings correlation and impact
                from ai_models.config import AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT
                from openai import AzureOpenAI
                
                if not all([AZURE_OPENAI_KEY, MODEL_NAME, AZURE_OPENAI_ENDPOINT]):
                    return JsonResponse({
                        'earnings_correlation': 50,
                        'impact_level': 'medium'
                    }, status=500)
                
                client = AzureOpenAI(
                    api_key=AZURE_OPENAI_KEY,
                    api_version="2023-05-15",
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                )
                
                # Prepare earnings data summary for analysis
                recent_earnings = earnings_data[:8] if earnings_data else []  # Last 8 quarters
                company_info = company_profile[0] if company_profile else {}
                
                earnings_summary = ""
                if recent_earnings:
                    earnings_summary = f"Recent earnings data: {len(recent_earnings)} quarters analyzed. "
                    beats = sum(1 for e in recent_earnings if e.get('eps', 0) > e.get('epsEstimated', 0))
                    misses = sum(1 for e in recent_earnings if e.get('eps', 0) < e.get('epsEstimated', 0))
                    earnings_summary += f"Beats: {beats}, Misses: {misses}. "
                
                company_summary = ""
                if company_info:
                    company_summary = f"Company: {company_info.get('companyName', symbol)}, "
                    company_summary += f"Industry: {company_info.get('industry', 'N/A')}, "
                    company_summary += f"Sector: {company_info.get('sector', 'N/A')}, "
                    company_summary += f"Market Cap: ${company_info.get('mktCap', 0):,}. "
                
                prompt = f"""
                Analyze {symbol}'s earnings correlation and market impact based on the following data:
                
                {company_summary}
                {earnings_summary}
                
                Company Description: {company_info.get('description', 'N/A')[:500]}...
                
                Provide analysis for:
                1. Earnings Correlation (0-100): How strongly this stock's earnings performance correlates with overall market movements, sector trends, and economic indicators.
                2. Impact Level: Overall market impact classification based on company size, sector influence, and earnings volatility.
                
                Consider factors like:
                - Company size and market capitalization
                - Sector importance and market influence
                - Earnings consistency and surprise history
                - Economic sensitivity and cyclicality
                - Market leadership position
                
                For Impact Level:
                - High Impact: Large cap companies with significant market influence, earnings that move markets
                - Medium Impact: Mid-cap companies with moderate influence, sector-specific impact
                - Low Impact: Small cap companies with limited broader market influence
                
                Respond ONLY with a JSON object in this exact format:
                {{
                    "earnings_correlation": [0-100 integer],
                    "impact_level": "[high|medium|low]"
                }}
                """
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a financial analysis expert specializing in earnings correlation and market impact analysis. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                ai_response = response.choices[0].message.content.strip()
                
                try:
                    # Try to find JSON in the response (in case there's extra text)
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        ai_response = json_match.group()
                    
                    result = json.loads(ai_response)
                    
                    # Extract and validate results
                    earnings_correlation = int(result.get('earnings_correlation', 50))
                    impact_level = result.get('impact_level', 'medium').lower()
                    
                    # Ensure correlation is within 0-100 range
                    earnings_correlation = max(0, min(100, earnings_correlation))
                    
                    # Ensure impact level is valid
                    if impact_level not in ['high', 'medium', 'low']:
                        impact_level = 'medium'
                    
                    return JsonResponse({
                        'earnings_correlation': earnings_correlation,
                        'impact_level': impact_level
                    })
                    
                except (json.JSONDecodeError, ValueError, KeyError):
                    # Fallback if AI response isn't valid JSON
                    return JsonResponse({
                        'earnings_correlation': 50,
                        'impact_level': 'medium'
                    })
                    
            else:
                return JsonResponse({
                    'earnings_correlation': 50,
                    'impact_level': 'medium'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'earnings_correlation': 50,
                'impact_level': 'medium'
            }, status=500)
    
    else:
        return JsonResponse({'error': 'GET required'}, status=405)
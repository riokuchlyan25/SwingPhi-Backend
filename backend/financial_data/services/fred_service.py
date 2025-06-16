#internal
from financial_data.config import FRED_API_KEY

# external
import requests

# built-in
from django.http import JsonResponse

FRED_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations'

# Helper to fetch FRED data
def fetch_fred_data(series_id, frequency):
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'frequency': frequency,
    }
    response = requests.get(FRED_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('observations', [])
    return []

def fred_yearly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'a')  # annual
        return JsonResponse({'yearly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_monthly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'm')  # monthly
        return JsonResponse({'monthly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_weekly_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'w')  # weekly
        return JsonResponse({'weekly': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_max_api(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '')
        data = fetch_fred_data(ticker, 'd')
        return JsonResponse({'max': data})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_economic_indicators_api(request):
    """Get key economic indicators (CPI, GDP, Unemployment, etc.)"""
    if request.method == 'POST':
        # Key economic indicators
        indicators = {
            'CPI_All_Urban': 'CPIAUCSL',  # Consumer Price Index for All Urban Consumers
            'CPI_Core': 'CPILFESL',       # Core CPI (less food and energy)
            'Unemployment_Rate': 'UNRATE', # Unemployment Rate
            'GDP': 'GDP',                  # Gross Domestic Product
            'Federal_Funds_Rate': 'FEDFUNDS', # Federal Funds Rate
            'Treasury_10Y': 'DGS10',       # 10-Year Treasury Rate
            'Industrial_Production': 'INDPRO', # Industrial Production Index
            'Consumer_Confidence': 'UMCSENT', # Consumer Sentiment
        }
        
        results = {}
        for name, series_id in indicators.items():
            try:
                data = fetch_fred_data(series_id, 'm')  # Monthly frequency
                # Get latest value if data exists
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'full_data': data[-12:]  # Last 12 months
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'economic_indicators': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_market_events_api(request):
    """Get data related to market events and economic releases"""
    if request.method == 'POST':
        # Market event related indicators
        market_indicators = {
            'VIX': 'VIXCLS',              # VIX Volatility Index
            'SP500': 'SP500',             # S&P 500 Index
            'Dollar_Index': 'DTWEXBGS',   # Trade Weighted US Dollar Index
            'Gold_Price': 'GOLDAMGBD228NLBM', # Gold Price
            'Oil_Price': 'DCOILWTICO',    # WTI Crude Oil Price
            'Treasury_Yield_Spread': 'T10Y2Y', # 10-Year Treasury Constant Maturity Minus 2-Year
            'Credit_Spread': 'BAMLH0A0HYM2', # High Yield Corporate Bond Spread
            'Real_GDP_Growth': 'A191RL1Q225SBEA', # Real GDP Growth Rate
        }
        
        results = {}
        for name, series_id in market_indicators.items():
            try:
                # Use daily frequency for market data, monthly for economic data
                frequency = 'd' if name in ['VIX', 'SP500', 'Dollar_Index', 'Gold_Price', 'Oil_Price'] else 'm'
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    # Get recent data (last 30 for daily, last 12 for monthly)
                    recent_count = 30 if frequency == 'd' else 12
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'market_events': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_cpi_detailed_api(request):
    """Get detailed CPI data and inflation metrics"""
    if request.method == 'POST':
        cpi_indicators = {
            'Headline_CPI': 'CPIAUCSL',        # All items CPI
            'Core_CPI': 'CPILFESL',            # Core CPI (less food and energy)
            'Food_CPI': 'CPIUFDSL',            # Food CPI
            'Energy_CPI': 'CPIENGSL',          # Energy CPI
            'Housing_CPI': 'CPIHOSNS',         # Housing CPI
            'Transportation_CPI': 'CPITRNSL',   # Transportation CPI
            'Medical_CPI': 'CPIMEDSL',         # Medical care CPI
            'Recreation_CPI': 'CPIRECSL',      # Recreation CPI
            'Education_CPI': 'CPIEDUSL',       # Education CPI
            'PCE_Price_Index': 'PCEPI',        # Personal Consumption Expenditures Price Index
            'PPI': 'PPIFIS',                   # Producer Price Index
        }
        
        results = {}
        for name, series_id in cpi_indicators.items():
            try:
                data = fetch_fred_data(series_id, 'm')  # Monthly frequency
                
                if data and len(data) >= 2:
                    latest = data[-1]
                    previous = data[-2]
                    
                    # Calculate month-over-month and year-over-year changes
                    current_value = float(latest.get('value', 0)) if latest.get('value') != '.' else None
                    previous_value = float(previous.get('value', 0)) if previous.get('value') != '.' else None
                    
                    mom_change = None
                    yoy_change = None
                    
                    if current_value and previous_value:
                        mom_change = round(((current_value - previous_value) / previous_value) * 100, 2)
                    
                    # Year-over-year calculation (if we have 12+ months of data)
                    if len(data) >= 13:
                        year_ago = data[-13]
                        year_ago_value = float(year_ago.get('value', 0)) if year_ago.get('value') != '.' else None
                        if current_value and year_ago_value:
                            yoy_change = round(((current_value - year_ago_value) / year_ago_value) * 100, 2)
                    
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'month_over_month_change': f"{mom_change}%" if mom_change else 'N/A',
                        'year_over_year_change': f"{yoy_change}%" if yoy_change else 'N/A',
                        'last_12_months': data[-12:]
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'Insufficient data for calculations'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'cpi_detailed': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_money_banking_api(request):
    """Get money, banking & finance indicators"""
    if request.method == 'POST':
        banking_indicators = {
            'M1_Money_Supply': 'M1SL',                    # M1 Money Supply
            'M2_Money_Supply': 'M2SL',                    # M2 Money Supply
            'Bank_Credit': 'TOTLL',                       # Total Bank Credit
            'Commercial_Bank_Deposits': 'DPSACBW027SBOG', # Commercial Bank Deposits
            'Bank_Leverage_Ratio': 'EQTA',                # Bank Equity to Total Assets
            'Business_Lending': 'BUSLOANS',               # Commercial and Industrial Loans
            'Small_Business_Lending': 'SBLOANS',          # Small Business Loans
            'Real_Exchange_Rate': 'REER',                 # Real Effective Exchange Rate
            'Dollar_Index_Broad': 'DTWEXBGS',             # Dollar Index Broad
            'Treasury_3M': 'DGS3MO',                      # 3-Month Treasury Rate
            'Treasury_2Y': 'DGS2',                        # 2-Year Treasury Rate
            'Treasury_5Y': 'DGS5',                        # 5-Year Treasury Rate
            'Treasury_30Y': 'DGS30',                      # 30-Year Treasury Rate
            'Corporate_AAA': 'DAAA',                      # Corporate AAA Bond Yield
            'Corporate_BAA': 'DBAA',                      # Corporate BAA Bond Yield
            'High_Yield_Spread': 'BAMLH0A0HYM2',         # High Yield Corporate Bond Spread
        }
        
        results = {}
        for name, series_id in banking_indicators.items():
            try:
                # Use appropriate frequency based on data type
                frequency = 'd' if 'Treasury' in name or 'Corporate' in name or 'Exchange' in name else 'm'
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    recent_count = 30 if frequency == 'd' else 12
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'money_banking': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_employment_labor_api(request):
    """Get employment and labor market indicators"""
    if request.method == 'POST':
        labor_indicators = {
            'Unemployment_Rate': 'UNRATE',                # Unemployment Rate
            'Labor_Force_Participation': 'CIVPART',      # Labor Force Participation Rate
            'Employment_Population_Ratio': 'EMRATIO',     # Employment-Population Ratio
            'Nonfarm_Payrolls': 'PAYEMS',                # Total Nonfarm Payrolls
            'ADP_Employment': 'NPPTTL',                   # ADP National Employment
            'Initial_Claims': 'ICSA',                     # Initial Unemployment Claims
            'Continuing_Claims': 'CCSA',                  # Continuing Unemployment Claims
            'Job_Openings': 'JTSJOL',                     # Job Openings (JOLTS)
            'Quits_Rate': 'JTSQUR',                       # Quits Rate
            'Hires_Rate': 'JTSHIR',                       # Hires Rate
            'Layoffs_Rate': 'JTSLDL',                     # Layoffs and Discharges
            'Employment_Cost_Index': 'ECIALLCIV',         # Employment Cost Index
            'Average_Hourly_Earnings': 'AHETPI',          # Average Hourly Earnings
            'Average_Weekly_Hours': 'AWHAETP',            # Average Weekly Hours
            'Productivity': 'OPHNFB',                     # Nonfarm Business Productivity
            'Unit_Labor_Costs': 'ULCNFB',                 # Unit Labor Costs
            'Consumer_Confidence': 'UMCSENT',             # Consumer Sentiment
            'Retail_Sales': 'RSXFS',                      # Retail Sales Ex Autos
        }
        
        results = {}
        for name, series_id in labor_indicators.items():
            try:
                # Use weekly for claims data, monthly for others
                frequency = 'w' if 'Claims' in name else 'm'
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    if frequency == 'w':
                        recent_count = 52  # 52 weeks
                    else:
                        recent_count = 12  # 12 months
                    
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'employment_labor': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_price_commodities_api(request):
    """Get price and commodity indicators"""
    if request.method == 'POST':
        price_indicators = {
            'WTI_Oil': 'DCOILWTICO',                      # WTI Crude Oil Price
            'Brent_Oil': 'DCOILBRENTEU',                  # Brent Crude Oil Price
            'Natural_Gas': 'DHHNGSP',                     # Natural Gas Price
            'Gold_Price': 'GOLDAMGBD228NLBM',             # Gold Price
            'Silver_Price': 'SLVPRUSD',                   # Silver Price
            'Copper_Price': 'PCOPPUSDM',                  # Copper Price
            'Corn_Price': 'PMAIZMTUSDM',                  # Corn Price
            'Wheat_Price': 'PWHEAMTUSDM',                 # Wheat Price
            'Soybeans_Price': 'PSOYBUSDQ',                # Soybeans Price
            'Commodity_Index': 'PPIACO',                  # All Commodities PPI
            'Energy_PPI': 'PPIENG',                       # Energy PPI
            'Food_PPI': 'PPIFOOD',                        # Food PPI
            'Metals_PPI': 'PPIMETAL',                     # Metals PPI
            'Healthcare_CPI': 'CPIMEDSL',                 # Medical Care CPI
            'Housing_CPI': 'CPIHOSNS',                    # Housing CPI
            'Transportation_CPI': 'CPITRNSL',             # Transportation CPI
            'Education_CPI': 'CPIEDUSL',                  # Education CPI
        }
        
        results = {}
        for name, series_id in price_indicators.items():
            try:
                # Use daily for commodity prices, monthly for indices
                frequency = 'd' if 'Price' in name else 'm'
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    recent_count = 30 if frequency == 'd' else 12
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'price_commodities': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_international_data_api(request):
    """Get international economic data"""
    if request.method == 'POST':
        international_indicators = {
            'China_GDP': 'CHNGDPNQDSMEI',                 # China GDP
            'Eurozone_GDP': 'CLVMNACSCAB1GQEZ',          # Eurozone GDP
            'Japan_GDP': 'JPNRGDPEXP',                    # Japan GDP
            'UK_GDP': 'GBRRGDPQDSNAQ',                    # UK GDP
            'Canada_GDP': 'CANRGDPQDSNAQ',                # Canada GDP
            'Brazil_GDP': 'BRAORGDPQDSNAQ',               # Brazil GDP
            'India_GDP': 'INDRGDPQDSNAQ',                 # India GDP
            'DXY_Dollar_Index': 'DXY',                    # DXY Dollar Index
            'EUR_USD': 'DEXUSEU',                         # EUR/USD Exchange Rate
            'USD_JPY': 'DEXJPUS',                         # USD/JPY Exchange Rate
            'GBP_USD': 'DEXUSUK',                         # GBP/USD Exchange Rate
            'USD_CAD': 'DEXCAUS',                         # USD/CAD Exchange Rate
            'USD_CNY': 'DEXCHUS',                         # USD/CNY Exchange Rate
            'Trade_Balance': 'BOPGSTB',                   # Trade Balance
            'Current_Account': 'NETFI',                   # Net International Investment Position
        }
        
        results = {}
        for name, series_id in international_indicators.items():
            try:
                # Use daily for FX rates, quarterly/monthly for GDP and trade
                if 'USD' in name or 'EUR' in name or 'GBP' in name or 'DXY' in name:
                    frequency = 'd'
                    recent_count = 30
                elif 'GDP' in name:
                    frequency = 'q'  # quarterly
                    recent_count = 8   # 8 quarters (2 years)
                else:
                    frequency = 'm'
                    recent_count = 12
                
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'international_data': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_national_accounts_api(request):
    """Get national accounts data"""
    if request.method == 'POST':
        national_indicators = {
            'GDP_Real': 'GDPC1',                          # Real GDP
            'GDP_Nominal': 'GDP',                         # Nominal GDP
            'GDP_Deflator': 'GDPDEF',                     # GDP Deflator
            'Personal_Income': 'PI',                      # Personal Income
            'Personal_Spending': 'PCE',                   # Personal Consumption Expenditures
            'Personal_Saving_Rate': 'PSAVERT',           # Personal Saving Rate
            'Disposable_Income': 'DSPIC96',               # Real Disposable Personal Income
            'Government_Spending': 'FGEXPND',             # Federal Government Expenditures
            'Government_Debt': 'FYGFD',                   # Federal Debt Total Public Debt
            'Debt_to_GDP': 'GFDGDPA188S',                 # Federal Debt to GDP Ratio
            'Trade_Deficit': 'BOPGSTB',                   # Trade Balance
            'Current_Account_Balance': 'BOPBCA',          # Current Account Balance
            'Foreign_Exchange_Reserves': 'TRESEGUSM052N', # US Foreign Exchange Reserves
            'Capital_Flows': 'BOPBCAA',                   # Capital Account Balance
            'Net_Exports': 'NETEXP',                      # Net Exports of Goods and Services
        }
        
        results = {}
        for name, series_id in national_indicators.items():
            try:
                # Most national account data is quarterly or monthly
                if 'Debt' in name or 'Deficit' in name:
                    frequency = 'a'  # annual
                    recent_count = 10
                else:
                    frequency = 'q'  # quarterly
                    recent_count = 12  # 3 years
                
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'national_accounts': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_academic_research_api(request):
    """Get academic research and policy uncertainty data"""
    if request.method == 'POST':
        academic_indicators = {
            'Economic_Policy_Uncertainty': 'USEPUINDXD',   # Economic Policy Uncertainty Index
            'VIX_Volatility': 'VIXCLS',                    # VIX Volatility Index
            'Recession_Probability': 'RECPROUSM156N',      # Recession Probability
            'Yield_Curve_Spread': 'T10Y2Y',                # 10Y-2Y Treasury Spread
            'Term_Spread': 'T10Y3M',                       # 10Y-3M Treasury Spread
            'Credit_Spread_BAA': 'BAA10Y',                 # BAA Corporate Bond Spread
            'NFCI_Financial_Conditions': 'NFCI',          # Chicago Fed Financial Conditions
            'Real_Interest_Rate': 'REAINTRATREARAT10Y',   # 10-Year Real Interest Rate
            'Breakeven_Inflation': 'T5YIE',               # 5-Year Breakeven Inflation
            'Dollar_Strength': 'DTWEXBGS',                # Trade Weighted Dollar Index
            'Liquidity_Premium': 'BAMLC0A0CM',           # Corporate Bond Liquidity Premium
            'Market_Volatility': 'VIXCLS',                # VIX (duplicate for completeness)
        }
        
        results = {}
        for name, series_id in academic_indicators.items():
            try:
                # Most research indicators are daily or monthly
                frequency = 'd'
                recent_count = 60  # 60 days for research purposes
                
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'academic_research': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_housing_real_estate_api(request):
    """Get housing and real estate indicators"""
    if request.method == 'POST':
        housing_indicators = {
            'Housing_Starts': 'HOUST',                    # Housing Starts
            'Building_Permits': 'PERMIT',                # Building Permits
            'New_Home_Sales': 'HSN1F',                   # New Home Sales
            'Existing_Home_Sales': 'EXHOSLUSM495S',      # Existing Home Sales
            'Home_Price_Index': 'CSUSHPINSA',            # Case-Shiller Home Price Index
            'Median_Home_Price': 'MSPUS',                # Median Sales Price of Houses
            'Housing_Inventory': 'MSACSR',               # Months Supply of Houses
            'Mortgage_30Y_Rate': 'MORTGAGE30US',         # 30-Year Fixed Mortgage Rate
            'Mortgage_15Y_Rate': 'MORTGAGE15US',         # 15-Year Fixed Mortgage Rate
            'Mortgage_Applications': 'HBMAMTSA',         # Mortgage Bankers Assoc Applications
            'Construction_Spending': 'TTLCONS',          # Total Construction Spending
            'Homeownership_Rate': 'RHORUSQ156N',         # Homeownership Rate
            'Rental_Vacancy_Rate': 'RRVRUSQ156N',        # Rental Vacancy Rate
            'Home_Ownership_Vacancy': 'RHVRUSQ156N',     # Homeowner Vacancy Rate
        }
        
        results = {}
        for name, series_id in housing_indicators.items():
            try:
                # Most housing data is monthly
                frequency = 'm'
                recent_count = 24  # 2 years of data
                
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'housing_real_estate': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_manufacturing_industrial_api(request):
    """Get manufacturing and industrial indicators"""
    if request.method == 'POST':
        manufacturing_indicators = {
            'Industrial_Production': 'INDPRO',            # Industrial Production Index
            'Manufacturing_Production': 'IPMAN',          # Manufacturing Production
            'Capacity_Utilization': 'TCU',                # Total Capacity Utilization
            'Manufacturing_Capacity': 'MCUMFN',           # Manufacturing Capacity Utilization
            'ISM_Manufacturing': 'NAPM',                  # ISM Manufacturing PMI
            'ISM_Services': 'NAPMSII',                    # ISM Services PMI
            'Chicago_PMI': 'NAPMCHI',                     # Chicago PMI
            'Philly_Fed_Index': 'PHILLY',                # Philadelphia Fed Business Index
            'NY_Empire_State': 'GACDINA066MNFRBNY',      # NY Empire State Manufacturing
            'Durable_Goods_Orders': 'DGORDER',           # Durable Goods Orders
            'New_Orders_Nondefense': 'NEWORDER',         # Manufacturers New Orders
            'Factory_Orders': 'AMTMNO',                  # Manufacturers Total Orders
            'Inventories': 'AMTMTI',                     # Manufacturers Total Inventories
            'Shipments': 'AMTMTS',                       # Manufacturers Total Shipments
        }
        
        results = {}
        for name, series_id in manufacturing_indicators.items():
            try:
                frequency = 'm'  # Most manufacturing data is monthly
                recent_count = 24  # 2 years of data
                
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'manufacturing_industrial': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_healthcare_indexes_api(request):
    """Get healthcare cost and utilization indicators"""
    if request.method == 'POST':
        healthcare_indicators = {
            'Healthcare_CPI': 'CPIMEDSL',                 # Medical Care CPI
            'Prescription_Drug_CPI': 'CPIRXSL',          # Prescription Drug CPI
            'Hospital_Services_CPI': 'CPIHOSNS',         # Hospital Services CPI
            'Physician_Services_CPI': 'CPIAPPSL',        # Professional Services CPI
            'Health_Insurance_CPI': 'CPIHLTIN',          # Health Insurance CPI
            'Medical_Equipment_CPI': 'CPIMEDCRE',        # Medical Equipment CPI
            'Healthcare_PCE': 'DHLCRG3A086NBEA',         # Healthcare PCE Real
            'Hospital_Utilization': 'HOSINPATDAYS',      # Hospital Patient Days
            'Medicare_Enrollment': 'MEDICAREEN',         # Medicare Enrollment
            'Health_Spending_GDP': 'HLTHSCPCHP',         # Health Spending as % of GDP
        }
        
        results = {}
        for name, series_id in healthcare_indicators.items():
            try:
                frequency = 'm'
                recent_count = 24
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'healthcare_indexes': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_education_productivity_api(request):
    """Get education and productivity indicators"""
    if request.method == 'POST':
        education_indicators = {
            'Educational_Services_CPI': 'CPIEDUSL',      # Educational Services CPI
            'College_Tuition_CPI': 'CUSR0000SEEB02',     # College Tuition CPI
            'Labor_Productivity': 'OPHNFB',              # Nonfarm Business Productivity
            'Manufacturing_Productivity': 'OPHPBS',      # Manufacturing Productivity
            'Unit_Labor_Costs': 'ULCNFB',                # Unit Labor Costs
            'Multifactor_Productivity': 'MPU4910063',    # Multifactor Productivity
            'Educational_Attainment': 'LES1252881600Q',  # College Graduate Rate
            'Student_Loans': 'SLOAS',                    # Student Loans Outstanding
            'R_and_D_Spending': 'Y694RC1Q027SBEA',       # R&D as % of GDP
            'Patents_Granted': 'USPATGRT',               # US Patents Granted
        }
        
        results = {}
        for name, series_id in education_indicators.items():
            try:
                if 'Patents' in name:
                    frequency = 'a'
                    recent_count = 10
                elif 'Productivity' in name:
                    frequency = 'q'
                    recent_count = 20
                else:
                    frequency = 'm'
                    recent_count = 24
                    
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'education_productivity': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_trade_transportation_api(request):
    """Get trade indexes and transportation indicators"""
    if request.method == 'POST':
        trade_indicators = {
            'Import_Price_Index': 'IR',                   # Import Price Index
            'Export_Price_Index': 'IPTOT',               # Export Price Index
            'Trade_Weighted_Dollar': 'DTWEXBGS',         # Trade Weighted Dollar
            'Container_Traffic': 'RAILFRTCARLOAD',       # Rail Container Traffic
            'Air_Freight': 'LOADFACTOR',                 # Air Load Factor
            'Truck_Tonnage': 'TRUCKD11',                 # Truck Tonnage Index
            'Baltic_Dry_Index': 'BALTICDRYBULK',         # Baltic Dry Index (if available)
            'Transportation_CPI': 'CPITRNSL',            # Transportation CPI
            'Motor_Fuel_CPI': 'CUUR0000SETB01',         # Motor Fuel CPI
            'Transportation_PCE': 'DTRANRG3A086NBEA',    # Transportation PCE
            'Vehicle_Sales': 'TOTALSA',                  # Total Vehicle Sales
            'Imports_Goods': 'IMPGS',                    # Imports of Goods
            'Exports_Goods': 'EXPGS',                    # Exports of Goods
        }
        
        results = {}
        for name, series_id in trade_indicators.items():
            try:
                frequency = 'm'
                recent_count = 24
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'trade_transportation': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_income_demographics_api(request):
    """Get income distribution and demographic indicators"""
    if request.method == 'POST':
        income_indicators = {
            'Median_Household_Income': 'MEHOINUSA672N',   # Median Household Income
            'Income_Inequality_Gini': 'SIPOVGINIUSA',     # Gini Coefficient
            'Poverty_Rate': 'PPAAUS00000A156NCEN',        # Poverty Rate
            'Real_Median_Income': 'RMHIPOV185A647NCEN',   # Real Median Income
            'Income_Top_5_Percent': 'RINCQ5USA156NCEN',   # Top 5% Income Share
            'Income_Bottom_20_Percent': 'RINCQ1USA156NCEN', # Bottom 20% Income Share
            'Population_Total': 'POPTHM',                 # Total Population
            'Population_Working_Age': 'LFWA64TTUSM647S',  # Working Age Population
            'Labor_Force_Participation': 'CIVPART',      # Labor Force Participation
            'Women_Labor_Force': 'LNS11300002',          # Women Labor Force Participation
            'Minimum_Wage_Federal': 'FEDMINNFRWG',       # Federal Minimum Wage
            'Living_Wage': 'LIVINGWAGE',                 # Living Wage Estimate
        }
        
        results = {}
        for name, series_id in income_indicators.items():
            try:
                if 'Income' in name or 'Poverty' in name:
                    frequency = 'a'
                    recent_count = 15
                elif 'Population' in name:
                    frequency = 'm'
                    recent_count = 60
                else:
                    frequency = 'm'
                    recent_count = 24
                    
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'income_demographics': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_cryptocurrency_fintech_api(request):
    """Get cryptocurrency and fintech sentiment indicators"""
    if request.method == 'POST':
        crypto_indicators = {
            'Bitcoin_Price': 'CBBTCUSD',                  # Bitcoin Price (if available)
            'Digital_Payments': 'TDSP',                   # Digital Payment Volume
            'Credit_Card_Debt': 'CCLACBW027SBOG',        # Credit Card Debt
            'Fintech_Investment': 'FINTECHINV',          # Fintech Investment (if available)
            'Mobile_Payment_Adoption': 'MOBILEPAY',      # Mobile Payment Adoption
            'Electronic_Benefits': 'TEBPD',              # Electronic Benefits Transfer
            'Online_Banking': 'ONLINEBANK',              # Online Banking Usage
            'Digital_Currency_CBDC': 'CBDC',             # Central Bank Digital Currency
            'Crypto_Market_Cap': 'CRYPTOMARKET',         # Crypto Market Cap
            'Blockchain_Adoption': 'BLOCKCHAIN',         # Blockchain Adoption Index
        }
        
        results = {}
        for name, series_id in crypto_indicators.items():
            try:
                frequency = 'd' if 'Price' in name else 'm'
                recent_count = 30 if frequency == 'd' else 24
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'cryptocurrency_fintech': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_historical_academic_api(request):
    """Get historical and academic research indicators"""
    if request.method == 'POST':
        academic_indicators = {
            'Economic_Policy_Uncertainty': 'USEPUINDXD',   # Economic Policy Uncertainty
            'NBER_Recession_Indicator': 'USRECM',          # NBER Recession Indicator
            'Recession_Probability': 'RECPROUSM156N',      # Recession Probability
            'Historical_Fed_Funds': 'FEDFUNDS',           # Federal Funds Rate (Historical)
            'Long_Term_Interest_Rates': 'IRLTLT01USM156N', # Long Term Interest Rates
            'Yield_Curve_10Y2Y': 'T10Y2Y',               # 10Y-2Y Treasury Spread
            'Yield_Curve_10Y3M': 'T10Y3M',               # 10Y-3M Treasury Spread
            'Chicago_Fed_NFCI': 'NFCI',                  # National Financial Conditions Index
            'Aruoba_Diebold_Scotti': 'ADSBDI',           # Business Conditions Index
            'Weekly_Economic_Index': 'WEI',               # NY Fed Weekly Economic Index
            'Sahm_Rule_Indicator': 'SAHMREALTIME',       # Sahm Rule Recession Indicator
            'Financial_Stress_Index': 'STLFSI4',         # St. Louis Fed Financial Stress
        }
        
        results = {}
        for name, series_id in academic_indicators.items():
            try:
                if 'Weekly' in name:
                    frequency = 'w'
                    recent_count = 52
                elif 'Daily' in name or 'Policy' in name:
                    frequency = 'd'
                    recent_count = 90
                else:
                    frequency = 'm'
                    recent_count = 60
                    
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'historical_academic': results})
    return JsonResponse({'error': 'POST required'}, status=400)

def fred_sector_specific_api(request):
    """Get sector-specific economic indicators"""
    if request.method == 'POST':
        sector_indicators = {
            'Energy_Production': 'IPG211111CN',          # Energy Production Index
            'Technology_Production': 'IPG334111N',       # Computer Production
            'Financial_Conditions': 'NFCI',              # Financial Conditions
            'Small_Business_Optimism': 'SBOPTIM',        # Small Business Optimism
            'Consumer_Sentiment': 'UMCSENT',             # Consumer Sentiment
            'Business_Applications': 'BABABABUSINESSAPP', # Business Applications
            'Startup_Activity': 'STARTUP',               # Startup Activity Index
            'Venture_Capital': 'VENTURECAP',             # Venture Capital Investment
            'Corporate_Profits': 'CP',                   # Corporate Profits
            'Business_Investment': 'FIXEDASSETS',        # Business Fixed Investment
            'Innovation_Index': 'INNOVATION',            # Innovation Index
            'Digital_Economy': 'DIGITALECO',             # Digital Economy Indicators
        }
        
        results = {}
        for name, series_id in sector_indicators.items():
            try:
                if 'Production' in name:
                    frequency = 'm'
                    recent_count = 24
                elif 'Investment' in name or 'Profits' in name:
                    frequency = 'q'
                    recent_count = 20
                else:
                    frequency = 'm'
                    recent_count = 24
                    
                data = fetch_fred_data(series_id, frequency)
                
                if data and len(data) > 0:
                    latest = data[-1]
                    results[name] = {
                        'series_id': series_id,
                        'latest_value': latest.get('value', 'N/A'),
                        'latest_date': latest.get('date', 'N/A'),
                        'recent_data': data[-recent_count:],
                        'frequency': frequency
                    }
                else:
                    results[name] = {
                        'series_id': series_id,
                        'error': 'No data available'
                    }
            except Exception as e:
                results[name] = {
                    'series_id': series_id,
                    'error': str(e)
                }
        
        return JsonResponse({'sector_specific': results})
    return JsonResponse({'error': 'POST required'}, status=400)
# internal
from financial_data.config import FMP_API_KEY
from .fmp_service import fmp_service

# external
import requests
import pandas as pd
import numpy as np
from django.http import JsonResponse
import json

# NYSE Stock Data - Comprehensive list of major NYSE stocks with their industries/sectors
NYSE_STOCKS = {
    # Technology (50+ stocks)
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Social Media'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'CRM': {'name': 'Salesforce Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'ADBE': {'name': 'Adobe Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'ORCL': {'name': 'Oracle Corporation', 'sector': 'Technology', 'industry': 'Software'},
    'AMD': {'name': 'Advanced Micro Devices Inc.', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'INTC': {'name': 'Intel Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'QCOM': {'name': 'Qualcomm Incorporated', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'AVGO': {'name': 'Broadcom Inc.', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'TXN': {'name': 'Texas Instruments Incorporated', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'CSCO': {'name': 'Cisco Systems Inc.', 'sector': 'Technology', 'industry': 'Networking'},
    'IBM': {'name': 'International Business Machines Corp.', 'sector': 'Technology', 'industry': 'IT Services'},
    'HPQ': {'name': 'HP Inc.', 'sector': 'Technology', 'industry': 'Computer Hardware'},
    'DELL': {'name': 'Dell Technologies Inc.', 'sector': 'Technology', 'industry': 'Computer Hardware'},
    'SNOW': {'name': 'Snowflake Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'PLTR': {'name': 'Palantir Technologies Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'ZM': {'name': 'Zoom Video Communications Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'TEAM': {'name': 'Atlassian Corporation', 'sector': 'Technology', 'industry': 'Software'},
    'NOW': {'name': 'ServiceNow Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'WDAY': {'name': 'Workday Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'SPLK': {'name': 'Splunk Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'CRWD': {'name': 'CrowdStrike Holdings Inc.', 'sector': 'Technology', 'industry': 'Cybersecurity'},
    'ZS': {'name': 'Zscaler Inc.', 'sector': 'Technology', 'industry': 'Cybersecurity'},
    'PANW': {'name': 'Palo Alto Networks Inc.', 'sector': 'Technology', 'industry': 'Cybersecurity'},
    'OKTA': {'name': 'Okta Inc.', 'sector': 'Technology', 'industry': 'Cybersecurity'},
    'FTNT': {'name': 'Fortinet Inc.', 'sector': 'Technology', 'industry': 'Cybersecurity'},
    'NET': {'name': 'Cloudflare Inc.', 'sector': 'Technology', 'industry': 'Internet Services'},
    'DDOG': {'name': 'Datadog Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'MDB': {'name': 'MongoDB Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'PATH': {'name': 'UiPath Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'RBLX': {'name': 'Roblox Corporation', 'sector': 'Technology', 'industry': 'Gaming'},
    'EA': {'name': 'Electronic Arts Inc.', 'sector': 'Technology', 'industry': 'Gaming'},
    'ATVI': {'name': 'Activision Blizzard Inc.', 'sector': 'Technology', 'industry': 'Gaming'},
    'TTWO': {'name': 'Take-Two Interactive Software Inc.', 'sector': 'Technology', 'industry': 'Gaming'},
    'U': {'name': 'Unity Software Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'RPTX': {'name': 'Repare Therapeutics Inc.', 'sector': 'Technology', 'industry': 'Biotechnology'},
    'SQ': {'name': 'Block Inc.', 'sector': 'Technology', 'industry': 'Financial Technology'},
    'PYPL': {'name': 'PayPal Holdings Inc.', 'sector': 'Technology', 'industry': 'Financial Technology'},
    'COIN': {'name': 'Coinbase Global Inc.', 'sector': 'Technology', 'industry': 'Financial Technology'},
    'HOOD': {'name': 'Robinhood Markets Inc.', 'sector': 'Technology', 'industry': 'Financial Technology'},
    'SHOP': {'name': 'Shopify Inc.', 'sector': 'Technology', 'industry': 'E-commerce'},
    'EBAY': {'name': 'eBay Inc.', 'sector': 'Technology', 'industry': 'E-commerce'},
    'ETSY': {'name': 'Etsy Inc.', 'sector': 'Technology', 'industry': 'E-commerce'},
    'PINS': {'name': 'Pinterest Inc.', 'sector': 'Technology', 'industry': 'Social Media'},
    'SNAP': {'name': 'Snap Inc.', 'sector': 'Technology', 'industry': 'Social Media'},
    'TWTR': {'name': 'Twitter Inc.', 'sector': 'Technology', 'industry': 'Social Media'},
    'UBER': {'name': 'Uber Technologies Inc.', 'sector': 'Technology', 'industry': 'Transportation'},
    'LYFT': {'name': 'Lyft Inc.', 'sector': 'Technology', 'industry': 'Transportation'},
    'DASH': {'name': 'DoorDash Inc.', 'sector': 'Technology', 'industry': 'Food Delivery'},
    'ABNB': {'name': 'Airbnb Inc.', 'sector': 'Technology', 'industry': 'Travel'},
    'SPOT': {'name': 'Spotify Technology S.A.', 'sector': 'Technology', 'industry': 'Entertainment'},
    'PELO': {'name': 'Peloton Interactive Inc.', 'sector': 'Technology', 'industry': 'Fitness'},
    'PTON': {'name': 'Peloton Interactive Inc.', 'sector': 'Technology', 'industry': 'Fitness'},
    'DOCU': {'name': 'DocuSign Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'TWLO': {'name': 'Twilio Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'ESTC': {'name': 'Elastic N.V.', 'sector': 'Technology', 'industry': 'Software'},
    'OKTA': {'name': 'Okta Inc.', 'sector': 'Technology', 'industry': 'Software'},
    'ZM': {'name': 'Zoom Video Communications Inc.', 'sector': 'Technology', 'industry': 'Software'},
    
    # Healthcare (40+ stocks)
    'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'UNH': {'name': 'UnitedHealth Group Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'PFE': {'name': 'Pfizer Inc.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'ABBV': {'name': 'AbbVie Inc.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'MRK': {'name': 'Merck & Co. Inc.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'TMO': {'name': 'Thermo Fisher Scientific Inc.', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'ABT': {'name': 'Abbott Laboratories', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'DHR': {'name': 'Danaher Corporation', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'MDT': {'name': 'Medtronic plc', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'BMY': {'name': 'Bristol-Myers Squibb Company', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'AMGN': {'name': 'Amgen Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'GILD': {'name': 'Gilead Sciences Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'BIIB': {'name': 'Biogen Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'REGN': {'name': 'Regeneron Pharmaceuticals Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'VRTX': {'name': 'Vertex Pharmaceuticals Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'MRNA': {'name': 'Moderna Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'BIONT': {'name': 'BioNTech SE', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'NVAX': {'name': 'Novavax Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'INO': {'name': 'Inovio Pharmaceuticals Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'CVS': {'name': 'CVS Health Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'CI': {'name': 'Cigna Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'ANTM': {'name': 'Anthem Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'HUM': {'name': 'Humana Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'AET': {'name': 'Aetna Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'BSX': {'name': 'Boston Scientific Corporation', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'ISRG': {'name': 'Intuitive Surgical Inc.', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'ALGN': {'name': 'Align Technology Inc.', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'DXCM': {'name': 'DexCom Inc.', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'IDXX': {'name': 'IDEXX Laboratories Inc.', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'WAT': {'name': 'Waters Corporation', 'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'ILMN': {'name': 'Illumina Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'CRL': {'name': 'Charles River Laboratories International Inc.', 'sector': 'Healthcare', 'industry': 'Biotechnology'},
    'IQV': {'name': 'IQVIA Holdings Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'LH': {'name': 'Laboratory Corporation of America Holdings', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'DGX': {'name': 'Quest Diagnostics Incorporated', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'HCA': {'name': 'HCA Healthcare Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'UHS': {'name': 'Universal Health Services Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'TEN': {'name': 'Tenet Healthcare Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'CNC': {'name': 'Centene Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'WBA': {'name': 'Walgreens Boots Alliance Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'RAD': {'name': 'Rite Aid Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'MCK': {'name': 'McKesson Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'ABC': {'name': 'AmerisourceBergen Corporation', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'CAH': {'name': 'Cardinal Health Inc.', 'sector': 'Healthcare', 'industry': 'Healthcare Services'},
    'PRGO': {'name': 'Perrigo Company plc', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'TEVA': {'name': 'Teva Pharmaceutical Industries Limited', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    'VTRS': {'name': 'Viatris Inc.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    
    # Financial (50+ stocks)
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial', 'industry': 'Banking'},
    'BAC': {'name': 'Bank of America Corp.', 'sector': 'Financial', 'industry': 'Banking'},
    'WFC': {'name': 'Wells Fargo & Company', 'sector': 'Financial', 'industry': 'Banking'},
    'GS': {'name': 'Goldman Sachs Group Inc.', 'sector': 'Financial', 'industry': 'Investment Banking'},
    'MS': {'name': 'Morgan Stanley', 'sector': 'Financial', 'industry': 'Investment Banking'},
    'C': {'name': 'Citigroup Inc.', 'sector': 'Financial', 'industry': 'Banking'},
    'BLK': {'name': 'BlackRock Inc.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'SPGI': {'name': 'S&P Global Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'ICE': {'name': 'Intercontinental Exchange Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'CME': {'name': 'CME Group Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'USB': {'name': 'U.S. Bancorp', 'sector': 'Financial', 'industry': 'Banking'},
    'PNC': {'name': 'PNC Financial Services Group Inc.', 'sector': 'Financial', 'industry': 'Banking'},
    'COF': {'name': 'Capital One Financial Corporation', 'sector': 'Financial', 'industry': 'Banking'},
    'TFC': {'name': 'Truist Financial Corporation', 'sector': 'Financial', 'industry': 'Banking'},
    'KEY': {'name': 'KeyCorp', 'sector': 'Financial', 'industry': 'Banking'},
    'RF': {'name': 'Regions Financial Corporation', 'sector': 'Financial', 'industry': 'Banking'},
    'HBAN': {'name': 'Huntington Bancshares Incorporated', 'sector': 'Financial', 'industry': 'Banking'},
    'FITB': {'name': 'Fifth Third Bancorp', 'sector': 'Financial', 'industry': 'Banking'},
    'ZION': {'name': 'Zions Bancorporation N.A.', 'sector': 'Financial', 'industry': 'Banking'},
    'CMA': {'name': 'Comerica Incorporated', 'sector': 'Financial', 'industry': 'Banking'},
    'NTRS': {'name': 'Northern Trust Corporation', 'sector': 'Financial', 'industry': 'Asset Management'},
    'STT': {'name': 'State Street Corporation', 'sector': 'Financial', 'industry': 'Asset Management'},
    'BEN': {'name': 'Franklin Resources Inc.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'TROW': {'name': 'T. Rowe Price Group Inc.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'IVZ': {'name': 'Invesco Ltd.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'AMG': {'name': 'Affiliated Managers Group Inc.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'SEIC': {'name': 'SEI Investments Company', 'sector': 'Financial', 'industry': 'Asset Management'},
    'LM': {'name': 'Legg Mason Inc.', 'sector': 'Financial', 'industry': 'Asset Management'},
    'PGR': {'name': 'Progressive Corporation', 'sector': 'Financial', 'industry': 'Insurance'},
    'TRV': {'name': 'Travelers Companies Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'AIG': {'name': 'American International Group Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'MET': {'name': 'MetLife Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'PRU': {'name': 'Prudential Financial Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'ALL': {'name': 'Allstate Corporation', 'sector': 'Financial', 'industry': 'Insurance'},
    'HIG': {'name': 'Hartford Financial Services Group Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'PFG': {'name': 'Principal Financial Group Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'LNC': {'name': 'Lincoln National Corporation', 'sector': 'Financial', 'industry': 'Insurance'},
    'AFL': {'name': 'Aflac Incorporated', 'sector': 'Financial', 'industry': 'Insurance'},
    'UNM': {'name': 'Unum Group', 'sector': 'Financial', 'industry': 'Insurance'},
    'L': {'name': 'Loews Corporation', 'sector': 'Financial', 'industry': 'Insurance'},
    'BRK-A': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'BRK-B': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'V': {'name': 'Visa Inc.', 'sector': 'Financial', 'industry': 'Payment Processing'},
    'MA': {'name': 'Mastercard Incorporated', 'sector': 'Financial', 'industry': 'Payment Processing'},
    'AXP': {'name': 'American Express Company', 'sector': 'Financial', 'industry': 'Credit Services'},
    'DFS': {'name': 'Discover Financial Services', 'sector': 'Financial', 'industry': 'Credit Services'},
    'SYF': {'name': 'Synchrony Financial', 'sector': 'Financial', 'industry': 'Credit Services'},
    'COF': {'name': 'Capital One Financial Corporation', 'sector': 'Financial', 'industry': 'Credit Services'},
    'ALLY': {'name': 'Ally Financial Inc.', 'sector': 'Financial', 'industry': 'Credit Services'},
    'CIT': {'name': 'CIT Group Inc.', 'sector': 'Financial', 'industry': 'Credit Services'},
    'NDAQ': {'name': 'Nasdaq Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'CBOE': {'name': 'Cboe Global Markets Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'MKTX': {'name': 'MarketAxess Holdings Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'TW': {'name': 'Tradeweb Markets Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'LPLA': {'name': 'LPL Financial Holdings Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'RJF': {'name': 'Raymond James Financial Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'SCHW': {'name': 'Charles Schwab Corporation', 'sector': 'Financial', 'industry': 'Financial Services'},
    'ETFC': {'name': 'E*TRADE Financial Corporation', 'sector': 'Financial', 'industry': 'Financial Services'},
    'AMTD': {'name': 'TD Ameritrade Holding Corporation', 'sector': 'Financial', 'industry': 'Financial Services'},
    'IBKR': {'name': 'Interactive Brokers Group Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    'LPL': {'name': 'LPL Financial Holdings Inc.', 'sector': 'Financial', 'industry': 'Financial Services'},
    
    # Energy
    'XOM': {'name': 'Exxon Mobil Corporation', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    'CVX': {'name': 'Chevron Corporation', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    'COP': {'name': 'ConocoPhillips', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    'EOG': {'name': 'EOG Resources Inc.', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    'SLB': {'name': 'Schlumberger Limited', 'sector': 'Energy', 'industry': 'Oil Services'},
    'KMI': {'name': 'Kinder Morgan Inc.', 'sector': 'Energy', 'industry': 'Pipeline'},
    'PSX': {'name': 'Phillips 66', 'sector': 'Energy', 'industry': 'Refining'},
    'VLO': {'name': 'Valero Energy Corporation', 'sector': 'Energy', 'industry': 'Refining'},
    'MPC': {'name': 'Marathon Petroleum Corporation', 'sector': 'Energy', 'industry': 'Refining'},
    'OXY': {'name': 'Occidental Petroleum Corporation', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    
    # Consumer Discretionary (40+ stocks)
    'HD': {'name': 'Home Depot Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'MCD': {'name': 'McDonald\'s Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'NKE': {'name': 'Nike Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'SBUX': {'name': 'Starbucks Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'DIS': {'name': 'Walt Disney Company', 'sector': 'Consumer Discretionary', 'industry': 'Entertainment'},
    'NFLX': {'name': 'Netflix Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Entertainment'},
    'CMG': {'name': 'Chipotle Mexican Grill Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'LOW': {'name': 'Lowe\'s Companies Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'TJX': {'name': 'TJX Companies Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'BKNG': {'name': 'Booking Holdings Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'industry': 'E-commerce'},
    'TGT': {'name': 'Target Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'COST': {'name': 'Costco Wholesale Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'BBY': {'name': 'Best Buy Co. Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'ULTA': {'name': 'Ulta Beauty Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'ROST': {'name': 'Ross Stores Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'BURL': {'name': 'Burlington Stores Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Retail'},
    'GPS': {'name': 'Gap Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'LULU': {'name': 'Lululemon Athletica Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'UA': {'name': 'Under Armour Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'UAA': {'name': 'Under Armour Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'VFC': {'name': 'V.F. Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'RL': {'name': 'Ralph Lauren Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'PVH': {'name': 'PVH Corp.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'HBI': {'name': 'Hanesbrands Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'LB': {'name': 'L Brands Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'BKE': {'name': 'Buckle Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Apparel'},
    'YUM': {'name': 'Yum! Brands Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'DRI': {'name': 'Darden Restaurants Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'DPZ': {'name': 'Domino\'s Pizza Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'WING': {'name': 'Wingstop Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'SHAK': {'name': 'Shake Shack Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'CAKE': {'name': 'Cheesecake Factory Incorporated', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'RUTH': {'name': 'Ruth\'s Hospitality Group Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'DIN': {'name': 'Dine Brands Global Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'EAT': {'name': 'Brinker International Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'BLMN': {'name': 'Bloomin\' Brands Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'TXRH': {'name': 'Texas Roadhouse Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Restaurants'},
    'F': {'name': 'Ford Motor Company', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'GM': {'name': 'General Motors Company', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'FCAU': {'name': 'Fiat Chrysler Automobiles N.V.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'STLA': {'name': 'Stellantis N.V.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'TM': {'name': 'Toyota Motor Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'HMC': {'name': 'Honda Motor Co. Ltd.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'NSANY': {'name': 'Nissan Motor Co. Ltd.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'RIVN': {'name': 'Rivian Automotive Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'LCID': {'name': 'Lucid Group Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'NIO': {'name': 'NIO Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'XPEV': {'name': 'XPeng Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'LI': {'name': 'Li Auto Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Automotive'},
    'WYNN': {'name': 'Wynn Resorts Limited', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'LVS': {'name': 'Las Vegas Sands Corp.', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'MGM': {'name': 'MGM Resorts International', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'CZR': {'name': 'Caesars Entertainment Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'PENN': {'name': 'Penn National Gaming Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'BYD': {'name': 'Boyd Gaming Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'IGT': {'name': 'International Game Technology PLC', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'SGMS': {'name': 'Scientific Games Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'LVS': {'name': 'Las Vegas Sands Corp.', 'sector': 'Consumer Discretionary', 'industry': 'Gaming'},
    'MAR': {'name': 'Marriott International Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'HLT': {'name': 'Hilton Worldwide Holdings Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'IHG': {'name': 'InterContinental Hotels Group PLC', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'H': {'name': 'Hyatt Hotels Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'WH': {'name': 'Wyndham Hotels & Resorts Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'CHH': {'name': 'Choice Hotels International Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Hospitality'},
    'RCL': {'name': 'Royal Caribbean Cruises Ltd.', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'CCL': {'name': 'Carnival Corporation', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'NCLH': {'name': 'Norwegian Cruise Line Holdings Ltd.', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'EXPE': {'name': 'Expedia Group Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'TRIP': {'name': 'TripAdvisor Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Travel'},
    'LYV': {'name': 'Live Nation Entertainment Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Entertainment'},
    'SPOT': {'name': 'Spotify Technology S.A.', 'sector': 'Consumer Discretionary', 'industry': 'Entertainment'},
    'PELO': {'name': 'Peloton Interactive Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Fitness'},
    'PTON': {'name': 'Peloton Interactive Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Fitness'},
    'PLNT': {'name': 'Planet Fitness Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Fitness'},
    'XPOF': {'name': 'Xponential Fitness Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Fitness'},
    
    # Consumer Staples
    'PG': {'name': 'Procter & Gamble Co.', 'sector': 'Consumer Staples', 'industry': 'Household Products'},
    'KO': {'name': 'Coca-Cola Company', 'sector': 'Consumer Staples', 'industry': 'Beverages'},
    'PEP': {'name': 'PepsiCo Inc.', 'sector': 'Consumer Staples', 'industry': 'Beverages'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Staples', 'industry': 'Retail'},
    'COST': {'name': 'Costco Wholesale Corporation', 'sector': 'Consumer Staples', 'industry': 'Retail'},
    'PM': {'name': 'Philip Morris International', 'sector': 'Consumer Staples', 'industry': 'Tobacco'},
    'MO': {'name': 'Altria Group Inc.', 'sector': 'Consumer Staples', 'industry': 'Tobacco'},
    'UL': {'name': 'Unilever plc', 'sector': 'Consumer Staples', 'industry': 'Household Products'},
    'CL': {'name': 'Colgate-Palmolive Company', 'sector': 'Consumer Staples', 'industry': 'Household Products'},
    'GIS': {'name': 'General Mills Inc.', 'sector': 'Consumer Staples', 'industry': 'Food Products'},
    
    # Industrials
    'BA': {'name': 'Boeing Company', 'sector': 'Industrials', 'industry': 'Aerospace'},
    'CAT': {'name': 'Caterpillar Inc.', 'sector': 'Industrials', 'industry': 'Machinery'},
    'GE': {'name': 'General Electric Company', 'sector': 'Industrials', 'industry': 'Conglomerate'},
    'HON': {'name': 'Honeywell International Inc.', 'sector': 'Industrials', 'industry': 'Conglomerate'},
    'MMM': {'name': '3M Company', 'sector': 'Industrials', 'industry': 'Conglomerate'},
    'UPS': {'name': 'United Parcel Service Inc.', 'sector': 'Industrials', 'industry': 'Transportation'},
    'FDX': {'name': 'FedEx Corporation', 'sector': 'Industrials', 'industry': 'Transportation'},
    'UNP': {'name': 'Union Pacific Corporation', 'sector': 'Industrials', 'industry': 'Railroad'},
    'CSX': {'name': 'CSX Corporation', 'sector': 'Industrials', 'industry': 'Railroad'},
    'RTX': {'name': 'Raytheon Technologies Corporation', 'sector': 'Industrials', 'industry': 'Aerospace'},
    
    # Utilities
    'NEE': {'name': 'NextEra Energy Inc.', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'DUK': {'name': 'Duke Energy Corporation', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'SO': {'name': 'Southern Company', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'D': {'name': 'Dominion Energy Inc.', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'EXC': {'name': 'Exelon Corporation', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'AEP': {'name': 'American Electric Power Company', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'XEL': {'name': 'Xcel Energy Inc.', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'WEC': {'name': 'WEC Energy Group Inc.', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'DTE': {'name': 'DTE Energy Company', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    'ED': {'name': 'Consolidated Edison Inc.', 'sector': 'Utilities', 'industry': 'Electric Utilities'},
    
    # Materials
    'LIN': {'name': 'Linde plc', 'sector': 'Materials', 'industry': 'Chemicals'},
    'APD': {'name': 'Air Products and Chemicals Inc.', 'sector': 'Materials', 'industry': 'Chemicals'},
    'ECL': {'name': 'Ecolab Inc.', 'sector': 'Materials', 'industry': 'Chemicals'},
    'SHW': {'name': 'Sherwin-Williams Company', 'sector': 'Materials', 'industry': 'Chemicals'},
    'FCX': {'name': 'Freeport-McMoRan Inc.', 'sector': 'Materials', 'industry': 'Metals & Mining'},
    'NEM': {'name': 'Newmont Corporation', 'sector': 'Materials', 'industry': 'Metals & Mining'},
    'AA': {'name': 'Alcoa Corporation', 'sector': 'Materials', 'industry': 'Metals & Mining'},
    'X': {'name': 'United States Steel Corporation', 'sector': 'Materials', 'industry': 'Metals & Mining'},
    'CLF': {'name': 'Cleveland-Cliffs Inc.', 'sector': 'Materials', 'industry': 'Metals & Mining'},
    'BLL': {'name': 'Ball Corporation', 'sector': 'Materials', 'industry': 'Packaging'},
    
    # Real Estate
    'AMT': {'name': 'American Tower Corporation', 'sector': 'Real Estate', 'industry': 'REIT'},
    'PLD': {'name': 'Prologis Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'CCI': {'name': 'Crown Castle International Corp.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'EQIX': {'name': 'Equinix Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'WELL': {'name': 'Welltower Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'PSA': {'name': 'Public Storage', 'sector': 'Real Estate', 'industry': 'REIT'},
    'O': {'name': 'Realty Income Corporation', 'sector': 'Real Estate', 'industry': 'REIT'},
    'SPG': {'name': 'Simon Property Group Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'DLR': {'name': 'Digital Realty Trust Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    'AVB': {'name': 'AvalonBay Communities Inc.', 'sector': 'Real Estate', 'industry': 'REIT'},
    
    # Communication Services
    'VZ': {'name': 'Verizon Communications Inc.', 'sector': 'Communication Services', 'industry': 'Telecommunications'},
    'T': {'name': 'AT&T Inc.', 'sector': 'Communication Services', 'industry': 'Telecommunications'},
    'TMUS': {'name': 'T-Mobile US Inc.', 'sector': 'Communication Services', 'industry': 'Telecommunications'},
    'CHTR': {'name': 'Charter Communications Inc.', 'sector': 'Communication Services', 'industry': 'Cable'},
    'CMCSA': {'name': 'Comcast Corporation', 'sector': 'Communication Services', 'industry': 'Cable'},
    'PARA': {'name': 'Paramount Global', 'sector': 'Communication Services', 'industry': 'Entertainment'},
    'WBD': {'name': 'Warner Bros. Discovery Inc.', 'sector': 'Communication Services', 'industry': 'Entertainment'},
    'FOX': {'name': 'Fox Corporation', 'sector': 'Communication Services', 'industry': 'Entertainment'},
    'NWSA': {'name': 'News Corporation', 'sector': 'Communication Services', 'industry': 'Publishing'},
    'LYV': {'name': 'Live Nation Entertainment Inc.', 'sector': 'Communication Services', 'industry': 'Entertainment'},
    
    # Additional Technology
    'AMD': {'name': 'Advanced Micro Devices Inc.', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'INTC': {'name': 'Intel Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'QCOM': {'name': 'Qualcomm Incorporated', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'AVGO': {'name': 'Broadcom Inc.', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'TXN': {'name': 'Texas Instruments Incorporated', 'sector': 'Technology', 'industry': 'Semiconductors'},
    'CSCO': {'name': 'Cisco Systems Inc.', 'sector': 'Technology', 'industry': 'Networking'},
    'IBM': {'name': 'International Business Machines Corp.', 'sector': 'Technology', 'industry': 'IT Services'},
    'HPQ': {'name': 'HP Inc.', 'sector': 'Technology', 'industry': 'Computer Hardware'},
    'DELL': {'name': 'Dell Technologies Inc.', 'sector': 'Technology', 'industry': 'Computer Hardware'},
    'SNOW': {'name': 'Snowflake Inc.', 'sector': 'Technology', 'industry': 'Software'},
    
    # Additional Financial
    'V': {'name': 'Visa Inc.', 'sector': 'Financial', 'industry': 'Payment Processing'},
    'MA': {'name': 'Mastercard Incorporated', 'sector': 'Financial', 'industry': 'Payment Processing'},
    'AXP': {'name': 'American Express Company', 'sector': 'Financial', 'industry': 'Credit Services'},
    'BRK-A': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'BRK-B': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'PGR': {'name': 'Progressive Corporation', 'sector': 'Financial', 'industry': 'Insurance'},
    'TRV': {'name': 'Travelers Companies Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'AIG': {'name': 'American International Group Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'MET': {'name': 'MetLife Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
    'PRU': {'name': 'Prudential Financial Inc.', 'sector': 'Financial', 'industry': 'Insurance'},
}

def get_nyse_stocks_api(request):
    """Get list of NYSE stocks with their industries and sectors"""
    if request.method == 'GET':
        try:
            # Convert to list format for easier consumption
            stocks_list = []
            for ticker, info in NYSE_STOCKS.items():
                stocks_list.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'sector': info['sector'],
                    'industry': info['industry']
                })
            
            # Sort by ticker for consistency
            stocks_list.sort(key=lambda x: x['ticker'])
            
            return JsonResponse({
                'total_stocks': len(stocks_list),
                'stocks': stocks_list,
                'sectors': list(set([stock['sector'] for stock in stocks_list])),
                'industries': list(set([stock['industry'] for stock in stocks_list]))
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to fetch NYSE stocks: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'GET method required'}, status=405)

def get_stock_correlation_api(request):
    """Get correlation between two stocks from the NYSE list"""
    if request.method == 'POST':
        try:
            # Get tickers from request
            ticker1 = request.POST.get('ticker1', '').strip().upper()
            ticker2 = request.POST.get('ticker2', '').strip().upper()
            
            # Try JSON if form data is empty
            if not ticker1 or not ticker2:
                try:
                    data = json.loads(request.body)
                    ticker1 = data.get('ticker1', '').strip().upper()
                    ticker2 = data.get('ticker2', '').strip().upper()
                except json.JSONDecodeError:
                    pass
            
            if not ticker1 or not ticker2:
                return JsonResponse({
                    'error': 'Both ticker1 and ticker2 are required'
                }, status=400)
            
            # Validate that both stocks are in our NYSE list
            if ticker1 not in NYSE_STOCKS:
                return JsonResponse({
                    'error': f'Ticker {ticker1} not found in NYSE stocks list'
                }, status=400)
            
            if ticker2 not in NYSE_STOCKS:
                return JsonResponse({
                    'error': f'Ticker {ticker2} not found in NYSE stocks list'
                }, status=400)
            
            # Calculate correlation
            correlation_data = calculate_stock_correlation(ticker1, ticker2)
            
            return JsonResponse(correlation_data)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to calculate correlation: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def calculate_stock_correlation(ticker1: str, ticker2: str) -> dict:
    """Calculate correlation between two stocks using 6 months of price data from FMP"""
    try:
        # Get stock data for both tickers using FMP
        data1 = fmp_service.get_historical_price_data(ticker1, period="6mo")
        data2 = fmp_service.get_historical_price_data(ticker2, period="6mo")
        
        if data1.empty or data2.empty:
            return {
                'error': 'Insufficient data for correlation calculation',
                'ticker1': ticker1,
                'ticker2': ticker2
            }
        
        # Calculate daily returns (percentage change)
        returns1 = data1['close'].pct_change().dropna()
        returns2 = data2['close'].pct_change().dropna()
        
        # Align the data by date
        common_dates = returns1.index.intersection(returns2.index)
        if len(common_dates) < 30:  # Need at least 30 days of data
            return {
                'error': 'Insufficient overlapping data for correlation calculation',
                'ticker1': ticker1,
                'ticker2': ticker2
            }
        
        aligned_returns1 = returns1[common_dates]
        aligned_returns2 = returns2[common_dates]
        
        # Calculate correlation
        correlation = aligned_returns1.corr(aligned_returns2)
        
        # Get current prices
        current_price1 = float(data1['close'].iloc[-1])
        current_price2 = float(data2['close'].iloc[-1])
        
        # Get stock information from FMP
        stock1_profile = fmp_service.get_company_profile(ticker1)
        stock2_profile = fmp_service.get_company_profile(ticker2)
        
        # Get stock information from our NYSE list as fallback
        stock1_info = NYSE_STOCKS.get(ticker1, {})
        stock2_info = NYSE_STOCKS.get(ticker2, {})
        
        # Use FMP data if available, otherwise use our NYSE list
        stock1_name = stock1_profile.get('companyName', stock1_info.get('name', 'Unknown'))
        stock1_sector = stock1_profile.get('sector', stock1_info.get('sector', 'Unknown'))
        stock1_industry = stock1_profile.get('industry', stock1_info.get('industry', 'Unknown'))
        
        stock2_name = stock2_profile.get('companyName', stock2_info.get('name', 'Unknown'))
        stock2_sector = stock2_profile.get('sector', stock2_info.get('sector', 'Unknown'))
        stock2_industry = stock2_profile.get('industry', stock2_info.get('industry', 'Unknown'))
        
        # Determine correlation strength
        if abs(correlation) >= 0.7:
            strength = "Strong"
        elif abs(correlation) >= 0.4:
            strength = "Moderate"
        elif abs(correlation) >= 0.2:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        # Determine correlation direction
        if correlation > 0:
            direction = "Positive"
        elif correlation < 0:
            direction = "Negative"
        else:
            direction = "No Correlation"
        
        return {
            'ticker1': {
                'symbol': ticker1,
                'name': stock1_name,
                'sector': stock1_sector,
                'industry': stock1_industry,
                'current_price': round(current_price1, 2)
            },
            'ticker2': {
                'symbol': ticker2,
                'name': stock2_name,
                'sector': stock2_sector,
                'industry': stock2_industry,
                'current_price': round(current_price2, 2)
            },
            'correlation': {
                'value': round(correlation, 4),
                'strength': strength,
                'direction': direction,
                'data_points': len(common_dates),
                'period': '6 months'
            },
            'analysis': {
                'same_sector': stock1_sector == stock2_sector,
                'sector_correlation': stock1_sector == stock2_sector,
                'industry_correlation': stock1_industry == stock2_industry
            }
        }
        
    except Exception as e:
        return {
            'error': f'Failed to calculate correlation: {str(e)}',
            'ticker1': ticker1,
            'ticker2': ticker2
        } 
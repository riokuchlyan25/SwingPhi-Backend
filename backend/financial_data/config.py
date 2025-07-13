# internal

# external
from dotenv import load_dotenv

# built-in
import os

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
PHI_RESEARCH_CHARLES_SCHWAB_KEY = os.getenv("PHI_RESEARCH_CHARLES_SCHWAB_KEY")
PHI_RESEARCH_CHARLES_SCHWAB_SECRET = os.getenv("PHI_RESEARCH_CHARLES_SCHWAB_SECRET")
FMP_API_KEY = os.getenv("FMP_API_KEY")
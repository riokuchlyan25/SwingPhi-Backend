# internal

# external
from dotenv import load_dotenv

# built-in
import os

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
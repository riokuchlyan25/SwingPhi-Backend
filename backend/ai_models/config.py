# internal

# external
from dotenv import load_dotenv

# built-in
import os

load_dotenv()

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
FRED_API_KEY = os.getenv("FRED_API_KEY")
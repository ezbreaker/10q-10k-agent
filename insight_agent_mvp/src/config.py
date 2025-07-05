"""
Configuration file for InsightAgent MVP
Contains all hyperparameters and constants
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.0

# SEC API Configuration
SEC_BASE_URL = "https://data.sec.gov"
SEC_EDGAR_URL = "https://www.sec.gov/Archives/edgar/data"
SEC_USER_AGENT = "InsightAgent MVP Project agent@insightagent.com"

# Rate limiting configuration
SEC_REQUEST_DELAY = 0.2  # seconds between requests to respect SEC rate limits (10 req/sec)

# Supported tickers and their CIK mappings
# CIKs must be 10 digits, padded with leading zeros
TICKER_TO_CIK = {
    "AAPL": "0000320193",
    "MSFT": "0000789019", 
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "TSLA": "0001318605",
    "META": "0001326801",
    "NVDA": "0001045810",
    "NFLX": "0001065280"
}

# XBRL Configuration
TARGET_XBRL_TAG = "us-gaap:Revenues"
XBRL_PARSER = "lxml"  # BeautifulSoup parser

# API Configuration
API_TITLE = "InsightAgent MVP"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Financial data extraction API that retrieves SEC EDGAR filings and extracts XBRL financial metrics.

Features:
- Retrieve 10-K and 10-Q filings from SEC EDGAR database
- Extract financial metrics using XBRL tags
- Natural language query processing with GPT-3.5-turbo
- Support for major US public companies
- RESTful API with OpenAPI documentation
""" 
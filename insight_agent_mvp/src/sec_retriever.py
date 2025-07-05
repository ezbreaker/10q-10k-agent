import requests
import time
from typing import Optional
from .config import (
    TICKER_TO_CIK, 
    SEC_BASE_URL, 
    SEC_EDGAR_URL, 
    SEC_USER_AGENT, 
    SEC_REQUEST_DELAY
)

# SEC requires a custom User-Agent for all programmatic requests.
HEADERS = {'User-Agent': SEC_USER_AGENT}

def get_filing_html(ticker: str, year: int, form_type: str = "10-K") -> str:
    """
    Fetches the HTML content of a specific filing for a given ticker, year, and form type.
    
    Args:
        ticker: Company ticker symbol (e.g., 'AAPL')
        year: The year of the filing to retrieve (e.g., 2023)
        form_type: Type of filing to retrieve (default: "10-K", can also be "10-Q")
    
    Returns:
        The HTML content of the requested filing
        
    Raises:
        ValueError: If ticker is not supported
        FileNotFoundError: If no filing found for the specified criteria
    """
    if ticker.upper() not in TICKER_TO_CIK:
        raise ValueError(f"Ticker {ticker} not found in CIK mapping. Supported tickers: {list(TICKER_TO_CIK.keys())}")

    cik = TICKER_TO_CIK[ticker.upper()]
    
    # 1. Get the submissions history for the company.
    submissions_url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    response = requests.get(submissions_url, headers=HEADERS)
    response.raise_for_status()
    submissions_data = response.json()
    
    # 2. Find the filing that matches the specified year and form type
    target_filing = _find_filing_by_year_and_type(submissions_data, year, form_type)
    
    if not target_filing:
        raise FileNotFoundError(f"No {form_type} found for {ticker} in year {year}.")

    accession_number, primary_document = target_filing
    
    # 3. Construct the URL for the actual HTML filing.
    filing_url = f"{SEC_EDGAR_URL}/{int(cik)}/{accession_number}/{primary_document}"
    
    # Add a small delay to respect SEC rate limits
    time.sleep(SEC_REQUEST_DELAY)
    
    # 4. Download the HTML content.
    filing_response = requests.get(filing_url, headers=HEADERS)
    filing_response.raise_for_status()
    
    return filing_response.text

def _find_filing_by_year_and_type(submissions_data: dict, target_year: int, form_type: str) -> Optional[tuple]:
    """
    Helper function to find a filing by year and form type from submissions data.
    
    Args:
        submissions_data: The JSON response from SEC submissions API
        target_year: The target year to search for
        form_type: The form type to search for (e.g., "10-K", "10-Q")
    
    Returns:
        Tuple of (accession_number, primary_document) if found, None otherwise
    """
    # First, check recent filings
    recent_filings = submissions_data.get('filings', {}).get('recent', {})
    result = _search_filings_in_data(recent_filings, target_year, form_type)
    if result:
        return result
    
    # If not found in recent, check archived filings
    files = submissions_data.get('filings', {}).get('files', [])
    for file_info in files:
        if file_info.get('name', '').startswith('CIK'):
            # Download and search the archived filing data
            archive_url = f"{SEC_BASE_URL}/submissions/{file_info['name']}"
            try:
                response = requests.get(archive_url, headers=HEADERS)
                response.raise_for_status()
                archive_data = response.json()
                
                result = _search_filings_in_data(archive_data, target_year, form_type)
                if result:
                    return result
                    
                time.sleep(SEC_REQUEST_DELAY)  # Rate limiting
            except Exception as e:
                print(f"Warning: Could not fetch archive file {file_info['name']}: {e}")
                continue
    
    return None

def _search_filings_in_data(filings_data: dict, target_year: int, form_type: str) -> Optional[tuple]:
    """
    Search for a filing in a filings data structure.
    
    Args:
        filings_data: Filing data containing arrays of forms, dates, etc.
        target_year: The target year to search for
        form_type: The form type to search for
    
    Returns:
        Tuple of (accession_number, primary_document) if found, None otherwise
    """
    forms = filings_data.get('form', [])
    filing_dates = filings_data.get('filingDate', [])
    accession_numbers = filings_data.get('accessionNumber', [])
    primary_documents = filings_data.get('primaryDocument', [])
    
    # Search through the filings
    for i in range(len(forms)):
        if (i < len(filing_dates) and 
            i < len(accession_numbers) and 
            i < len(primary_documents)):
            
            # Check if form type matches
            if forms[i] == form_type:
                # Extract year from filing date (format: YYYY-MM-DD)
                filing_year = int(filing_dates[i][:4])
                
                # Check if year matches
                if filing_year == target_year:
                    accession_number = accession_numbers[i].replace('-', '')
                    primary_document = primary_documents[i]
                    return (accession_number, primary_document)
    
    return None

# Keep the old function for backward compatibility
def get_latest_10k_html(ticker: str) -> str:
    """
    Fetches the HTML content of the most recent 10-K filing for a given ticker.
    This function is kept for backward compatibility.
    """
    # Get current year and try recent years if not found
    import datetime
    current_year = datetime.datetime.now().year
    
    for year_offset in range(3):  # Try current year and 2 previous years
        try:
            return get_filing_html(ticker, current_year - year_offset, "10-K")
        except FileNotFoundError:
            continue
    
    raise FileNotFoundError(f"No recent 10-K found for {ticker}.") 
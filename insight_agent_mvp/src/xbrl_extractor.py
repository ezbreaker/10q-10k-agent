from bs4 import BeautifulSoup
from typing import Tuple, Optional
from .config import TARGET_XBRL_TAG, XBRL_PARSER

def extract_metric_from_html(html_content: str, metric_tag: str) -> Optional[Tuple[str, str]]:
    """
    Parses HTML content to find the iXBRL tag for a specified metric and returns its value and unit.
    
    Args:
        html_content: The HTML content to parse
        metric_tag: The XBRL tag to search for (e.g., 'us-gaap:Revenues', 'us-gaap:NetIncomeLoss')
    
    Returns:
        Tuple of (value, unit) if found, None otherwise
    """
    soup = BeautifulSoup(html_content, "xml")
    
    # Find the iXBRL tag for the specified metric. The tag name is 'ix:nonFraction'.
    # The 'name' attribute corresponds to the XBRL concept.
    metric_tag_element = soup.find('ix:nonFraction', {'name': metric_tag})
    
    if not metric_tag_element:
        return None
        
    # The value is the text content of the tag.
    value = metric_tag_element.get_text(strip=True)
    
    # The unit is usually in the 'unitref' attribute of the tag.
    unit_ref = metric_tag_element.get('unitref')
    
    return value, unit_ref

# Keep the old function for backward compatibility
def extract_revenue_from_html(html_content: str) -> Optional[Tuple[str, str]]:
    """
    Parses HTML content to find the iXBRL tag for 'Revenues' and returns its value and unit.
    This function is kept for backward compatibility.
    """
    return extract_metric_from_html(html_content, TARGET_XBRL_TAG) 
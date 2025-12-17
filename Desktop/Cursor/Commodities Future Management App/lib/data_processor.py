"""
Data processing utilities.
"""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd

def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string or None
    """
    if not date_str:
        return None
    
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %b %Y",
        "%Y-%m",
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Try pandas parsing as fallback
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def clean_price(price_str: any) -> Optional[float]:
    """
    Clean and convert price string/number to float.
    
    Args:
        price_str: Price value (string, number, etc.)
        
    Returns:
        Float price or None
    """
    if price_str is None:
        return None
    
    if isinstance(price_str, (int, float)):
        return float(price_str)
    
    if isinstance(price_str, str):
        cleaned = price_str.replace(",", "").replace("$", "").strip()
        if cleaned in ["NA", "-", "", "N/A", "null", "None"]:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None

def deduplicate_records(records: List[Dict], key_fields: List[str]) -> List[Dict]:
    """
    Remove duplicate records based on key fields.
    
    Args:
        records: List of record dictionaries
        key_fields: List of field names to use for deduplication
        
    Returns:
        List of unique records
    """
    seen = set()
    unique_records = []
    
    for record in records:
        key = tuple(record.get(field) for field in key_fields)
        if key not in seen:
            seen.add(key)
            unique_records.append(record)
    
    return unique_records

def validate_futures_record(record: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate a futures contract record.
    
    Args:
        record: Futures contract record dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["commodity", "contractMonth", "settlementPrice", "settlementDate"]
    
    for field in required_fields:
        if field not in record or record[field] is None:
            return False, f"Missing required field: {field}"
    
    if record["commodity"] not in ["WTI", "HH"]:
        return False, f"Invalid commodity: {record['commodity']}"
    
    if not isinstance(record["settlementPrice"], (int, float)) or record["settlementPrice"] <= 0:
        return False, "Invalid settlement price"
    
    return True, None

def validate_spot_record(record: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate a spot price record.
    
    Args:
        record: Spot price record dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["commodity", "price", "date"]
    
    for field in required_fields:
        if field not in record or record[field] is None:
            return False, f"Missing required field: {field}"
    
    if record["commodity"] not in ["WTI", "HH"]:
        return False, f"Invalid commodity: {record['commodity']}"
    
    if not isinstance(record["price"], (int, float)) or record["price"] <= 0:
        return False, "Invalid price"
    
    return True, None


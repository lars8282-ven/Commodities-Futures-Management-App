"""
Futures data table component.
"""
import pandas as pd
from typing import List, Dict, Optional
from lib.instant_client import get_db

def create_futures_data_table(
    commodity: Optional[str] = None,
    contract_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Create futures contracts data table.
    
    Args:
        commodity: Optional commodity filter
        contract_month: Optional contract month filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        DataFrame with futures contract data
    """
    db = get_db()
    
    filters = {}
    if commodity:
        filters["commodity"] = commodity
    if contract_month:
        filters["contractMonth"] = contract_month
    if start_date:
        filters["settlementDate"] = {"$gte": start_date}
    if end_date:
        if "settlementDate" in filters:
            filters["settlementDate"]["$lte"] = end_date
        else:
            filters["settlementDate"] = {"$lte": end_date}
    
    futures = db.query("futuresContracts", filters=filters if filters else None)
    
    if not futures:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(futures)
    
    # Select and order columns
    columns = [
        "commodity",
        "contractMonth",
        "contractSymbol",
        "settlementDate",
        "settlementPrice",
        "volume",
        "openInterest",
        "source",
    ]
    
    # Only include columns that exist
    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]
    
    # Sort by date
    if "settlementDate" in df.columns:
        df = df.sort_values("settlementDate", ascending=False)
    
    return df

def create_spot_data_table(
    commodity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Create spot prices data table.
    
    Args:
        commodity: Optional commodity filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        DataFrame with spot price data
    """
    db = get_db()
    
    filters = {}
    if commodity:
        filters["commodity"] = commodity
    if start_date:
        filters["date"] = {"$gte": start_date}
    if end_date:
        if "date" in filters:
            filters["date"]["$lte"] = end_date
        else:
            filters["date"] = {"$lte": end_date}
    
    spots = db.query("spotPrices", filters=filters if filters else None)
    
    if not spots:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(spots)
    
    # Select and order columns
    columns = [
        "commodity",
        "date",
        "price",
        "source",
    ]
    
    # Only include columns that exist
    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]
    
    # Sort by date
    if "date" in df.columns:
        df = df.sort_values("date", ascending=False)
    
    return df


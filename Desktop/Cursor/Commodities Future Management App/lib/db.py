"""
Supabase database client for storing CME futures settlement data.
Uses PostgREST client directly to avoid storage dependencies.
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from postgrest import SyncPostgrestClient
from dotenv import load_dotenv

load_dotenv()

# Global PostgREST client instance
_client: Optional[SyncPostgrestClient] = None


def get_db() -> SyncPostgrestClient:
    """Get or create the global PostgREST client instance."""
    global _client
    
    if _client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        # PostgREST endpoint is at /rest/v1
        postgrest_url = f"{supabase_url}/rest/v1"
        _client = SyncPostgrestClient(
            base_url=postgrest_url,
            schema="public",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
        )
    
    return _client


def save_futures_data(data: List[Dict]) -> Dict[str, int]:
    """
    Save scraped futures data to Supabase with deduplication.
    
    Args:
        data: List of futures contract records
        
    Returns:
        Dictionary with 'saved' and 'skipped' counts, and optional 'error' message
    """
    db = get_db()
    saved = 0
    skipped = 0
    errors = []
    
    for record in data:
        try:
            # Validate required fields
            if not record.get("date") or not record.get("commodity") or not record.get("month"):
                errors.append(f"Missing required fields: date={record.get('date')}, commodity={record.get('commodity')}, month={record.get('month')}")
                skipped += 1
                continue
            
            # Check if record already exists (date, commodity, month combination)
            existing = db.from_("futures_settlements").select("id").eq(
                "date", record["date"]
            ).eq(
                "commodity", record["commodity"]
            ).eq(
                "month", record["month"]
            ).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing record
                record_id = existing.data[0]["id"]
                update_data = {
                    "open": record.get("open"),
                    "high": record.get("high"),
                    "low": record.get("low"),
                    "last": record.get("last"),
                    "change": record.get("change"),
                    "settle": record.get("settle"),
                    "est_volume": record.get("est_volume"),
                    "prior_day_oi": record.get("prior_day_oi"),
                    "created_at": datetime.now().isoformat()
                }
                # Add contract_expiry_date if present
                if record.get("contract_expiry_date"):
                    update_data["contract_expiry_date"] = record.get("contract_expiry_date")
                result = db.from_("futures_settlements").update(update_data).eq("id", record_id).execute()
                
                if result.data:
                    saved += 1
                else:
                    skipped += 1
            else:
                # Insert new record
                result = db.from_("futures_settlements").insert(record).execute()
                if result.data:
                    saved += 1
                else:
                    skipped += 1
        except Exception as e:
            error_msg = f"Error saving record (date={record.get('date')}, commodity={record.get('commodity')}, month={record.get('month')}): {str(e)}"
            errors.append(error_msg)
            print(error_msg)  # Also print for terminal logs
            skipped += 1
    
    result = {"saved": saved, "skipped": skipped}
    if errors:
        result["errors"] = errors[:5]  # Limit to first 5 errors to avoid overwhelming
        result["error_count"] = len(errors)
    
    return result


def get_futures_data(date: str, commodity: Optional[str] = None) -> List[Dict]:
    """
    Query futures data from Supabase.
    
    Args:
        date: Date string in YYYY-MM-DD format
        commodity: Optional commodity filter ('WTI' or 'HH')
        
    Returns:
        List of futures records
    """
    db = get_db()
    
    query = db.from_("futures_settlements").select("*").eq("date", date)
    
    if commodity:
        query = query.eq("commodity", commodity)
    
    result = query.order("month").execute()
    return result.data if result.data else []


def data_exists_for_date(date: str, commodity: Optional[str] = None) -> bool:
    """
    Check if data already exists for a given date.
    
    Args:
        date: Date string in YYYY-MM-DD format
        commodity: Optional commodity filter ('WTI' or 'HH')
        
    Returns:
        True if data exists, False otherwise
    """
    db = get_db()
    
    query = db.from_("futures_settlements").select("id", count="exact").eq("date", date)
    
    if commodity:
        query = query.eq("commodity", commodity)
    
    result = query.execute()
    return result.count > 0 if hasattr(result, 'count') and result.count is not None else False


def get_latest_scrape_date(commodity: Optional[str] = None) -> Optional[str]:
    """
    Get the most recent date with data in the database.
    
    Args:
        commodity: Optional commodity filter ('WTI' or 'HH')
        
    Returns:
        Date string in YYYY-MM-DD format or None
    """
    db = get_db()
    
    query = db.from_("futures_settlements").select("date")
    
    if commodity:
        query = query.eq("commodity", commodity)
    
    # PostgREST uses .order() with column name and desc parameter
    try:
        result = query.order("date", desc=True).limit(1).execute()
    except:
        # Fallback: order ascending and get last
        result = query.order("date").limit(1).execute()
        if result.data:
            # Reverse to get most recent
            result.data = [result.data[-1]]
    
    if result.data and len(result.data) > 0:
        return result.data[0]["date"]
    
    return None

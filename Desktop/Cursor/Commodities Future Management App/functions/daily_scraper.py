"""
Automated daily scraper for CME futures data.
Designed to run as a cloud function (AWS Lambda, Vercel, etc.) on a daily schedule.
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path to import lib modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.scraper import CMEScraper
from lib.db import get_db, save_futures_data, data_exists_for_date


def handler(request):
    """
    HTTP handler for Vercel serverless function.
    
    Args:
        request: HTTP request object from Vercel
        
    Returns:
        HTTP response with JSON result
    """
    result = scrape_daily()
    
    return {
        "statusCode": 200 if result["success"] else 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }


def scrape_daily(event: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    """
    Main entry point for cloud function.
    Scrapes WTI and HH futures data for the current date (or yesterday if before market close).
    
    Args:
        event: Event data from cloud function trigger (optional)
        context: Context object from cloud function (optional)
        
    Returns:
        Dictionary with scrape results and status
    """
    result = {
        "success": True,
        "date": None,
        "wti": {"scraped": 0, "saved": 0, "skipped": 0, "error": None},
        "hh": {"scraped": 0, "saved": 0, "skipped": 0, "error": None},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        scraper = CMEScraper(headless=True)
        
        print("Scraping prior business day data (default on CME page)...")
        
        # Scrape WTI
        print("Scraping WTI...")
        try:
            wti_records = scraper.scrape_wti()
            result["wti"]["scraped"] = len(wti_records)
            
            if wti_records:
                # Extract date from first record
                scrape_date = wti_records[0].get("date") if wti_records else None
                result["date"] = scrape_date or result["date"]
                
                # Check if data already exists for this date
                if scrape_date and data_exists_for_date(scrape_date, "WTI"):
                    print(f"WTI data already exists for {scrape_date}, skipping...")
                    result["wti"]["skipped"] = len(wti_records)
                else:
                    save_result = save_futures_data(wti_records)
                    result["wti"]["saved"] = save_result["saved"]
                    result["wti"]["skipped"] = save_result["skipped"]
                    print(f"WTI: Scraped {len(wti_records)} contracts for {scrape_date}, Saved: {save_result['saved']}")
            else:
                print("WTI: No data found")
        except Exception as e:
            result["wti"]["error"] = str(e)
            result["success"] = False
            print(f"Error scraping WTI: {e}")
        
        # Scrape HH
        print("Scraping HH...")
        try:
            hh_records = scraper.scrape_henry_hub()
            result["hh"]["scraped"] = len(hh_records)
            
            if hh_records:
                # Extract date from first record
                scrape_date = hh_records[0].get("date") if hh_records else None
                if scrape_date:
                    result["date"] = scrape_date
                
                # Check if data already exists for this date
                if scrape_date and data_exists_for_date(scrape_date, "HH"):
                    print(f"HH data already exists for {scrape_date}, skipping...")
                    result["hh"]["skipped"] = len(hh_records)
                else:
                    save_result = save_futures_data(hh_records)
                    result["hh"]["saved"] = save_result["saved"]
                    result["hh"]["skipped"] = save_result["skipped"]
                    print(f"HH: Scraped {len(hh_records)} contracts for {scrape_date}, Saved: {save_result['saved']}")
            else:
                print("HH: No data found")
        except Exception as e:
            result["hh"]["error"] = str(e)
            result["success"] = False
            print(f"Error scraping HH: {e}")
        
        # Close driver after scraping
        scraper._close_driver()
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        print(f"Fatal error in daily scraper: {e}")
    
    return result


# For local testing
if __name__ == "__main__":
    print("Running daily scraper...")
    result = scrape_daily()
    print("\nResults:")
    print(json.dumps(result, indent=2))


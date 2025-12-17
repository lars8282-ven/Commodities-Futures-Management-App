#!/usr/bin/env python3
"""
Test script for CME Scraper with Supabase integration.
Tests scraper functionality and database operations.
"""
import sys
import os
from datetime import datetime, timedelta

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from lib.scraper import CMEScraper
from lib.db import get_db, save_futures_data, get_futures_data, data_exists_for_date

def test_available_dates():
    """Test getting available dates from CME."""
    print("\n" + "="*60)
    print("TEST 1: Get Available Dates")
    print("="*60)
    
    try:
        scraper = CMEScraper(headless=True)
        
        print("\nFetching available dates for WTI...")
        wti_dates = scraper.get_available_dates("WTI", debug=True)
        print(f"Found {len(wti_dates)} available WTI dates")
        if wti_dates:
            print("Sample dates:")
            for date_info in wti_dates[:3]:
                print(f"  - {date_info['display']} ({date_info['date']})")
        else:
            print("WARNING: No WTI dates found. This might indicate:")
            print("  - CME website structure has changed")
            print("  - Network/connection issue")
            print("  - Page needs more time to load")
        
        print("\nFetching available dates for HH...")
        hh_dates = scraper.get_available_dates("HH", debug=True)
        print(f"Found {len(hh_dates)} available HH dates")
        if hh_dates:
            print("Sample dates:")
            for date_info in hh_dates[:3]:
                print(f"  - {date_info['display']} ({date_info['date']})")
        else:
            print("WARNING: No HH dates found.")
        
        scraper._close_driver()
        
        # Return most recent date for next tests
        all_dates = []
        if wti_dates:
            all_dates.extend([d["date"] for d in wti_dates])
        if hh_dates:
            all_dates.extend([d["date"] for d in hh_dates])
        
        if all_dates:
            most_recent = sorted(set(all_dates), reverse=True)[0]
            print(f"\nMost recent available date: {most_recent}")
            return most_recent
        else:
            print("\nWARNING: No dates found!")
            return None
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_scrape_wti(test_date: str):
    """Test scraping WTI data."""
    print("\n" + "="*60)
    print(f"TEST 2: Scrape WTI Data for {test_date}")
    print("="*60)
    
    try:
        scraper = CMEScraper(headless=True)
        
        print(f"\nScraping WTI data for {test_date}...")
        records = scraper.scrape_wti(test_date)
        scraper._close_driver()
        
        print(f"Scraped {len(records)} WTI contracts")
        
        if records:
            print("\nSample records (first 3):")
            for i, record in enumerate(records[:3], 1):
                print(f"\nRecord {i}:")
                print(f"  Month: {record.get('month')}")
                print(f"  Settle: ${record.get('settle')}")
                print(f"  Open: ${record.get('open')}")
                print(f"  High: ${record.get('high')}")
                print(f"  Low: ${record.get('low')}")
            
            print(f"\nLast record:")
            last = records[-1]
            print(f"  Month: {last.get('month')}")
            print(f"  Settle: ${last.get('settle')}")
            
            return records
        else:
            print("\nWARNING: No records scraped!")
            return []
            
    except ValueError as e:
        print(f"\nERROR (Date not available): {e}")
        return None
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_scrape_hh(test_date: str):
    """Test scraping HH data."""
    print("\n" + "="*60)
    print(f"TEST 3: Scrape HH Data for {test_date}")
    print("="*60)
    
    try:
        scraper = CMEScraper(headless=True)
        
        print(f"\nScraping HH data for {test_date}...")
        records = scraper.scrape_henry_hub(test_date)
        scraper._close_driver()
        
        print(f"Scraped {len(records)} HH contracts")
        
        if records:
            print("\nSample records (first 3):")
            for i, record in enumerate(records[:3], 1):
                print(f"\nRecord {i}:")
                print(f"  Month: {record.get('month')}")
                print(f"  Settle: ${record.get('settle')}")
                print(f"  Open: ${record.get('open')}")
                print(f"  High: ${record.get('high')}")
                print(f"  Low: ${record.get('low')}")
            
            print(f"\nLast record:")
            last = records[-1]
            print(f"  Month: {last.get('month')}")
            print(f"  Settle: ${last.get('settle')}")
            
            return records
        else:
            print("\nWARNING: No records scraped!")
            return []
            
    except ValueError as e:
        print(f"\nERROR (Date not available): {e}")
        return None
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_database_connection():
    """Test Supabase database connection."""
    print("\n" + "="*60)
    print("TEST 4: Database Connection")
    print("="*60)
    
    try:
        db = get_db()
        print("\n[OK] Database connection successful")
        
        # Try a simple query
        result = db.from_("futures_settlements").select("id").limit(1).execute()
        print(f"[OK] Database query successful (found {len(result.data) if result.data else 0} records)")
        
        return True
    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_save_data(records: list, commodity: str):
    """Test saving data to database."""
    print("\n" + "="*60)
    print(f"TEST 5: Save {commodity} Data to Database")
    print("="*60)
    
    if not records:
        print("\nNo records to save")
        return None
    
    try:
        print(f"\nSaving {len(records)} {commodity} records...")
        result = save_futures_data(records)
        
        print(f"\nResults:")
        print(f"  Saved: {result['saved']}")
        print(f"  Skipped: {result['skipped']}")
        
        return result
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_retrieve_data(test_date: str, commodity: str = None):
    """Test retrieving data from database."""
    print("\n" + "="*60)
    print(f"TEST 6: Retrieve Data from Database for {test_date}")
    print("="*60)
    
    try:
        data = get_futures_data(test_date, commodity)
        
        print(f"\nRetrieved {len(data)} records")
        
        if data:
            print("\nSample records (first 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"\nRecord {i}:")
                print(f"  Commodity: {record.get('commodity')}")
                print(f"  Month: {record.get('month')}")
                print(f"  Settle: ${record.get('settle')}")
                print(f"  Date: {record.get('date')}")
        
        return data
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_data_exists(test_date: str):
    """Test checking if data exists."""
    print("\n" + "="*60)
    print(f"TEST 7: Check if Data Exists for {test_date}")
    print("="*60)
    
    try:
        wti_exists = data_exists_for_date(test_date, "WTI")
        hh_exists = data_exists_for_date(test_date, "HH")
        
        print(f"\nWTI data exists: {wti_exists}")
        print(f"HH data exists: {hh_exists}")
        
        return wti_exists, hh_exists
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CME Scraper Test Suite")
    print("="*60)
    
    # Test database connection first
    if not test_database_connection():
        print("\n[ERROR] Database connection failed. Please check your .env file.")
        print("Required: SUPABASE_URL and SUPABASE_KEY")
        return
    
    # Test getting available dates
    test_date = test_available_dates()
    
    if not test_date:
        print("\n[ERROR] Could not get available dates. Cannot continue with scraping tests.")
        return
    
    # Ask user if they want to scrape (this can be slow)
    print("\n" + "="*60)
    print("NOTE: Scraping tests will take a few minutes...")
    print("="*60)
    response = input("\nDo you want to run scraping tests? (y/n): ").strip().lower()
    
    if response == 'y':
        # Test scraping WTI
        wti_records = test_scrape_wti(test_date)
        
        if wti_records:
            # Test saving WTI data
            save_result = test_save_data(wti_records, "WTI")
            
            # Test retrieving WTI data
            test_retrieve_data(test_date, "WTI")
        
        # Test scraping HH
        hh_records = test_scrape_hh(test_date)
        
        if hh_records:
            # Test saving HH data
            save_result = test_save_data(hh_records, "HH")
            
            # Test retrieving HH data
            test_retrieve_data(test_date, "HH")
        
        # Test data exists check
        test_data_exists(test_date)
    else:
        print("\nSkipping scraping tests.")
        # Just test data retrieval if data already exists
        test_retrieve_data(test_date)
        test_data_exists(test_date)
    
    print("\n" + "="*60)
    print("Test Suite Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Debug script for CME Scraper.
Runs in visible mode (non-headless) with detailed debug output.
"""
import sys
import os

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from lib.scraper import CMEScraper

def main():
    print("\n" + "="*60)
    print("CME Scraper Debug Tool")
    print("="*60)
    print("\nThis will open a browser window so you can see what's happening.")
    print("The browser will stay open for a few seconds after completion.")
    print("\nPress Ctrl+C to stop early if needed.\n")
    
    # Run in visible mode with debug output
    scraper = CMEScraper(headless=False)
    
    try:
        print("\n" + "-"*60)
        print("Testing WTI Date Detection")
        print("-"*60)
        wti_dates = scraper.get_available_dates("WTI", debug=True)
        print(f"\n[RESULT] Found {len(wti_dates)} WTI dates")
        
        if wti_dates:
            print("\nAll WTI dates found:")
            for date_info in wti_dates:
                print(f"  - {date_info['display']} ({date_info['date']})")
        else:
            print("\n[WARNING] No dates found for WTI!")
            print("The browser window should still be open - check what's on the page.")
        
        # Keep browser open for a moment
        import time
        print("\n[INFO] Keeping browser open for 5 seconds so you can inspect...")
        time.sleep(5)
        
        print("\n" + "-"*60)
        print("Testing HH Date Detection")
        print("-"*60)
        hh_dates = scraper.get_available_dates("HH", debug=True)
        print(f"\n[RESULT] Found {len(hh_dates)} HH dates")
        
        if hh_dates:
            print("\nAll HH dates found:")
            for date_info in hh_dates:
                print(f"  - {date_info['display']} ({date_info['date']})")
        else:
            print("\n[WARNING] No dates found for HH!")
        
        # Keep browser open for a moment
        print("\n[INFO] Keeping browser open for 5 seconds so you can inspect...")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[INFO] Closing browser...")
        scraper._close_driver()
        print("[INFO] Done!")
    
    print("\n" + "="*60)
    print("Debug Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()


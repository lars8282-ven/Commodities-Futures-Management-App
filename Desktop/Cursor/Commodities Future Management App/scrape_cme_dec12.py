#!/usr/bin/env python3
"""
CME Settlement Price Scraper with Trade Date Selection

Handles:
1. Selecting trade date from dropdown (e.g., December 12, 2024)
2. Clicking Load button to load extended contracts
3. Scraping all contracts including extended ones (e.g., Feb 37)

Usage: python scrape_cme_dec12.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time


def _build_target_patterns(target_date: str, target_label: str | None = None) -> list[str]:
    """
    Build a list of strings to match for the trade date dropdown.
    """
    patterns = [
        target_date,  # ISO
        target_date.replace("-", "/"),
        target_date.replace("-", "/")[2:],
    ]
    try:
        dt = datetime.strptime(target_date, "%Y-%m-%d")
        patterns.extend(
            [
                dt.strftime("%b %d, %Y"),
                dt.strftime("%b %d %Y"),
                dt.strftime("%B %d, %Y"),
                dt.strftime("%B %d %Y"),
                dt.strftime("%m/%d/%Y"),
                dt.strftime("%m/%d/%y"),
                dt.strftime("%m-%d-%Y"),
                dt.strftime("%m-%d-%y"),
            ]
        )
    except ValueError:
        pass
    if target_label:
        patterns.append(target_label)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for p in patterns:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq


def _click_futures_tab(driver) -> bool:
    """
    Ensure the Futures tab/button is active (not Options).
    """
    selectors = [
        (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'futures')]"),
        (By.XPATH, "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'futures')]"),
        (By.CSS_SELECTOR, "button[data-product='futures']"),
    ]
    for by, sel in selectors:
        try:
            for el in driver.find_elements(by, sel):
                if el.is_displayed():
                    el.click()
                    print("    Clicked Futures tab")
                    time.sleep(1)
                    return True
        except Exception as e:
            print(f"    Futures tab attempt failed: {e}")
    print("    [WARNING] Futures tab not found; continuing")
    return False


def _select_trade_date(driver, target_patterns: list[str]) -> bool:
    """
    Select the trade date from a dropdown-like control.
    """
    date_selected = False

    # Strategy 1: visible select with date-like options
    selects = driver.find_elements(By.TAG_NAME, "select")
    for select_elem in selects:
        if not select_elem.is_displayed():
            continue
        try:
            select = Select(select_elem)
            options = select.options
            first_option = options[0].text.strip() if options else ""
            # Skip obvious non-date selects (e.g., Options)
            if "option" in first_option.lower() or "american" in first_option.lower():
                continue

            # Heuristic: first few options must contain digits and separators
            has_dates = False
            for opt in options[:5]:
                opt_text = opt.text.strip()
                if any(char.isdigit() for char in opt_text) and ("/" in opt_text or "-" in opt_text or "," in opt_text):
                    has_dates = True
                    break
            if not has_dates:
                continue

            print(f"    Found date select with {len(options)} options")
            print("    Sample options:")
            for i, opt in enumerate(options[:5]):
                print(f"      Option {i+1}: '{opt.text.strip()}'")

            for option in options:
                option_text = option.text.strip()
                for pattern in target_patterns:
                    if pattern in option_text:
                        select.select_by_visible_text(option_text)
                        print(f"    Selected date: {option_text} (matched pattern: {pattern})")
                        date_selected = True
                        time.sleep(2)
                        break
                if date_selected:
                    break
            if date_selected:
                return True
        except Exception as e:
            print(f"    Error with select: {e}")

    # Strategy 2: dropdown button with menu items
    dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "div.trade-date-row button.dropdown-toggle")
    for btn in dropdown_buttons:
        if not btn.is_displayed():
            continue
        try:
            btn.click()
            time.sleep(1)
            menu_items = btn.find_elements(By.XPATH, ".//following::ul[1]//li") or driver.find_elements(By.CSS_SELECTOR, "ul.dropdown-menu li")
            for item in menu_items:
                text = item.text.strip()
                for pattern in target_patterns:
                    if pattern in text:
                        item.click()
                        print(f"    Selected date via dropdown menu: {text}")
                        time.sleep(2)
                        return True
            # If not found, close dropdown by pressing Escape
            btn.send_keys("\u001b")
        except Exception as e:
            print(f"    Dropdown button selection failed: {e}")

    # Strategy 3: inputs named like date
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for inp in inputs:
        if not inp.is_displayed():
            continue
        attr_blob = " ".join(
            [
                inp.get_attribute("id") or "",
                inp.get_attribute("name") or "",
                inp.get_attribute("class") or "",
                inp.get_attribute("aria-label") or "",
            ]
        ).lower()
        if "date" in attr_blob:
            try:
                inp.click()
                time.sleep(0.5)
                inp.clear()
                inp.send_keys(target_patterns[0])
                print(f"    Entered date into input: {target_patterns[0]}")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"    Date input entry failed: {e}")

    print("    [WARNING] Could not select date; proceeding with default data")
    return False


def _click_load_all(driver) -> bool:
    """
    Click the 'LOAD ALL' (or similar) button to load extended contracts.
    """
    selectors = [
        (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load all')]"),
        (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load')]"),
        (By.CSS_SELECTOR, "button"),
        (By.XPATH, "//input[@value='LOAD ALL' or @value='Load All' or @value='Load']"),
    ]
    for by, sel in selectors:
        try:
            buttons = driver.find_elements(by, sel)
            for btn in buttons:
                if not btn.is_displayed():
                    continue
                text = (btn.text or "").strip().lower()
                val = (btn.get_attribute("value") or "").strip().lower()
                if "load all" in text or "load all" in val or "load" in text or "load" in val:
                    btn.click()
                    print(f"    Clicked Load/Load All button: '{btn.text or btn.get_attribute('value')}'")
                    time.sleep(8)
                    return True
        except Exception as e:
            print(f"    Load All attempt failed: {e}")
    print("    [WARNING] Load All button not found; continuing")
    return False

def scrape_wti_crude(target_date="2024-12-12", target_label="Monday, 15 Dec 2025"):
    """
    Scrape WTI Crude Oil futures settlement prices from CME
    
    Args:
        target_date: Settlement date to select (format: YYYY-MM-DD)
        target_label: Optional label text as shown in dropdown (e.g., "Monday, 15 Dec 2025")
    """
    url = "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html"
    
    print("[*] Fetching WTI Crude Oil settlement page...")
    print(f"    URL: {url}")
    print(f"    Target Settlement Date: {target_date}\n")
    
    try:
        # Use Selenium to handle JavaScript-rendered content
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        print("    Waiting for page to load...")
        time.sleep(5)
        
        # Ensure Futures tab selected
        _click_futures_tab(driver)

        # Select trade date and click Load All
        target_patterns = _build_target_patterns(target_date, target_label)
        _select_trade_date(driver, target_patterns)
        _click_load_all(driver)

        # Get page source after all interactions
        page_source = driver.page_source
        driver.quit()
        
        # Get page source after all interactions
        page_source = driver.page_source
        driver.quit()
        
        # Parse HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"    Found {len(tables)} tables on the page\n")
        
        # Look for settlement table
        for idx, table in enumerate(tables):
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text().strip() for h in headers])
            
            if 'Month' in header_text and 'Settle' in header_text:
                print(f"    [OK] Found settlement table (Table #{idx + 1})")
                print(f"    Headers: {header_text[:100]}...\n")
                
                # Extract all rows
                rows = []
                tbody = table.find('tbody')
                if tbody:
                    data_rows = tbody.find_all('tr')
                else:
                    data_rows = table.find_all('tr')[1:]
                
                print(f"    Found {len(data_rows)} data rows")
                
                # Check last contract
                if len(data_rows) > 0:
                    last_row = data_rows[-1]
                    last_cells = last_row.find_all(['td', 'th'])
                    if last_cells:
                        last_month = last_cells[0].get_text().strip()
                        print(f"    Last contract in table: {last_month}")
                        
                        # Check if we got extended contracts
                        if '37' in last_month or '38' in last_month or '39' in last_month:
                            print(f"    [SUCCESS] Extended contracts loaded (up to {last_month})!")
                        else:
                            print(f"    [NOTE] Only standard contracts found (up to {last_month})")
                print()
                
                # Extract column headers
                header_cells = [h.get_text().strip() for h in headers]
                
                # Process each row
                for row_idx, row in enumerate(data_rows):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == 0:
                        continue
                    
                    row_data = {}
                    for col_idx, cell in enumerate(cells):
                        if col_idx < len(header_cells):
                            row_data[header_cells[col_idx]] = cell.get_text().strip()
                    
                    if row_data:
                        rows.append(row_data)
                    
                    # Print first 3 and last 3 rows
                    if row_idx < 3:
                        print(f"    Row {row_idx + 1}: {row_data}")
                    elif row_idx == len(data_rows) - 3:
                        print(f"    ...")
                        print(f"    Row {row_idx + 1}: {row_data}")
                
                # Create DataFrame
                if rows:
                    df = pd.DataFrame(rows)
                    print(f"\n    [OK] Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
                    print(f"    Columns: {list(df.columns)}\n")
                    return df
        
        print("    [WARNING] No settlement table found")
        return None
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_natural_gas(target_date="2024-12-12", target_label="Monday, 15 Dec 2025"):
    """
    Scrape Henry Hub Natural Gas futures settlement prices from CME
    
    Args:
        target_date: Settlement date to select (format: YYYY-MM-DD)
        target_label: Optional label text as shown in dropdown (e.g., "Monday, 15 Dec 2025")
    """
    url = "https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.settlements.html"
    
    print("[*] Fetching Natural Gas settlement page...")
    print(f"    URL: {url}")
    print(f"    Target Settlement Date: {target_date}\n")
    
    try:
        # Use Selenium to handle JavaScript-rendered content
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        print("    Waiting for page to load...")
        time.sleep(5)
        
        # Ensure Futures tab selected
        _click_futures_tab(driver)

        # Select trade date and click Load All
        target_patterns = _build_target_patterns(target_date, target_label)
        _select_trade_date(driver, target_patterns)
        _click_load_all(driver)

        # Get page source after all interactions
        page_source = driver.page_source
        driver.quit()
        
        # Parse HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"    Found {len(tables)} tables on the page\n")
        
        # Look for settlement table
        for idx, table in enumerate(tables):
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text().strip() for h in headers])
            
            if 'Month' in header_text and 'Settle' in header_text:
                print(f"    [OK] Found settlement table (Table #{idx + 1})")
                print(f"    Headers: {header_text[:100]}...\n")
                
                rows = []
                tbody = table.find('tbody')
                if tbody:
                    data_rows = tbody.find_all('tr')
                else:
                    data_rows = table.find_all('tr')[1:]
                
                print(f"    Found {len(data_rows)} data rows")
                
                if len(data_rows) > 0:
                    last_row = data_rows[-1]
                    last_cells = last_row.find_all(['td', 'th'])
                    if last_cells:
                        last_month = last_cells[0].get_text().strip()
                        print(f"    Last contract in table: {last_month}")
                        
                        if '37' in last_month or '38' in last_month or '39' in last_month:
                            print(f"    [SUCCESS] Extended contracts loaded (up to {last_month})!")
                        else:
                            print(f"    [NOTE] Only standard contracts found (up to {last_month})")
                print()
                
                header_cells = [h.get_text().strip() for h in headers]
                
                for row_idx, row in enumerate(data_rows):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == 0:
                        continue
                    
                    row_data = {}
                    for col_idx, cell in enumerate(cells):
                        if col_idx < len(header_cells):
                            row_data[header_cells[col_idx]] = cell.get_text().strip()
                    
                    if row_data:
                        rows.append(row_data)
                    
                    if row_idx < 3:
                        print(f"    Row {row_idx + 1}: {row_data}")
                    elif row_idx == len(data_rows) - 3:
                        print(f"    ...")
                        print(f"    Row {row_idx + 1}: {row_data}")
                
                if rows:
                    df = pd.DataFrame(rows)
                    print(f"\n    [OK] Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
                    print(f"    Columns: {list(df.columns)}\n")
                    return df
        
        print("    [WARNING] No settlement table found")
        return None
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("\n" + "="*60)
    print("CME Settlement Price Scraper - December 12, 2024")
    print("="*60 + "\n")
    target_date = "2024-12-12"
    target_label = "Monday, 15 Dec 2025"  # adjust if UI label differs
    
    # Scrape WTI Crude Oil
    print("WTI CRUDE OIL")
    print("-" * 60)
    wti_df = scrape_wti_crude(target_date=target_date, target_label=target_label)
    
    if wti_df is not None:
        print("\nWTI Crude Oil Data Preview:")
        print(wti_df.head(5))
        if len(wti_df) > 5:
            print("\n...")
            print(wti_df.tail(3))
        
        # Save to CSV
        wti_filename = f"wti_settlements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        wti_df.to_csv(wti_filename, index=False)
        print(f"\n[SAVED] {wti_filename}")
        
        # Show contract range
        if len(wti_df) > 0:
            first_month = wti_df.iloc[0].get('Month', 'N/A')
            last_month = wti_df.iloc[-1].get('Month', 'N/A')
            print(f"\nContract Range: {first_month} to {last_month}")
            
            front_month = wti_df.iloc[0]
            print(f"\nFront-Month Contract (for December 12, 2024):")
            print(f"    Contract: {front_month.get('Month', 'N/A')}")
            if 'Settle' in front_month:
                print(f"    Settlement Price: ${front_month['Settle']}/bbl")
    
    print("\n" + "="*60 + "\n")
    
    # Scrape Natural Gas
    print("NATURAL GAS")
    print("-" * 60)
    ng_df = scrape_natural_gas(target_date=target_date, target_label=target_label)
    
    if ng_df is not None:
        print("\nNatural Gas Data Preview:")
        print(ng_df.head(5))
        if len(ng_df) > 5:
            print("\n...")
            print(ng_df.tail(3))
        
        # Save to CSV
        ng_filename = f"ng_settlements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        ng_df.to_csv(ng_filename, index=False)
        print(f"\n[SAVED] {ng_filename}")
        
        # Show contract range
        if len(ng_df) > 0:
            first_month = ng_df.iloc[0].get('Month', 'N/A')
            last_month = ng_df.iloc[-1].get('Month', 'N/A')
            print(f"\nContract Range: {first_month} to {last_month}")
            
            front_month = ng_df.iloc[0]
            print(f"\nFront-Month Contract (for December 12, 2024):")
            print(f"    Contract: {front_month.get('Month', 'N/A')}")
            if 'Settle' in front_month:
                print(f"    Settlement Price: ${front_month['Settle']}/MMBtu")
    
    print("\n" + "="*60)
    print("[SUCCESS] Scraping Complete!")
    print("="*60 + "\n")
    
    # Summary
    if wti_df is not None or ng_df is not None:
        print("Summary:")
        if wti_df is not None:
            print(f"    - WTI: {len(wti_df)} contracts scraped")
            if len(wti_df) > 0:
                print(f"      Range: {wti_df.iloc[0].get('Month', 'N/A')} to {wti_df.iloc[-1].get('Month', 'N/A')}")
        if ng_df is not None:
            print(f"    - Natural Gas: {len(ng_df)} contracts scraped")
            if len(ng_df) > 0:
                print(f"      Range: {ng_df.iloc[0].get('Month', 'N/A')} to {ng_df.iloc[-1].get('Month', 'N/A')}")
        print()

if __name__ == '__main__':
    main()

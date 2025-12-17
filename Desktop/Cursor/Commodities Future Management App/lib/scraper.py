"""
CME Group futures settlement price scraper using Selenium.
Scrapes WTI Crude Oil and Henry Hub Natural Gas futures settlement prices.
Extracts: Month, Open, High, Low, Last, Change, Settle, Est. Volume, Prior day OI
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import calendar
from typing import List, Dict, Optional, Tuple
import os


class CMEScraper:
    """Scraper for CME Group futures settlement prices using Selenium."""
    
    WTI_URL = "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html"
    HH_URL = "https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.settlements.html"
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.rate_limit_seconds = float(os.getenv("SCRAPE_RATE_LIMIT_SECONDS", "2"))
        self.headless = headless
        self.driver = None
    
    def _get_driver(self):
        """Get or create Chrome WebDriver instance."""
        if self.driver is None:
            try:
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Check for system Chrome/Chromium (GitHub Actions, Linux servers)
                chrome_bin = os.getenv("CHROME_BIN")
                chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
                
                if chrome_bin and os.path.exists(chrome_bin):
                    chrome_options.binary_location = chrome_bin
                    print(f"Using Chrome binary at: {chrome_bin}")
                
                try:
                    # Try using system chromedriver if available (GitHub Actions)
                    if chromedriver_path and os.path.exists(chromedriver_path):
                        print(f"Using Chromedriver at: {chromedriver_path}")
                        service = Service(chromedriver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        # Try using Selenium's built-in driver management first (Selenium 4.6+)
                        # This is more reliable on Windows
                        self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as driver_error1:
                    try:
                        # Fallback to webdriver-manager if built-in fails
                        print("Built-in driver management failed, trying webdriver-manager...")
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    except Exception as driver_error2:
                        error_msg = (
                            f"Failed to initialize Chrome WebDriver. "
                            f"Built-in method error: {driver_error1}. "
                            f"Webdriver-manager error: {driver_error2}. "
                            f"Please ensure Chrome browser is installed."
                        )
                        print(error_msg)
                        raise Exception(error_msg) from driver_error2
            except Exception as e:
                print(f"Error creating WebDriver: {e}")
                raise
        return self.driver
    
    def _close_driver(self):
        """Close the WebDriver if it exists."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float, handling suffixes like 'B' or 'A'."""
        if not price_str:
            return None
        try:
            # Remove commas, dollar signs, suffixes (B, A), and other characters
            cleaned = price_str.replace(",", "").replace("$", "").replace("—", "").strip()
            # Remove letter suffixes (B, A) that might appear at the end
            cleaned = re.sub(r'[A-Za-z]+$', '', cleaned).strip()
            if cleaned == "" or cleaned == "-":
                return None
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_change(self, change_str: str) -> Optional[float]:
        """Parse change value (can be negative with minus sign or parentheses)."""
        if not change_str:
            return None
        try:
            cleaned = change_str.replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
            # Remove letter suffixes
            cleaned = re.sub(r'[A-Za-z]+$', '', cleaned).strip()
            if cleaned == "" or cleaned == "-" or cleaned == "—":
                return None
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_date_from_dropdown(self, date_text: str) -> Optional[str]:
        """
        Parse date from dropdown text (e.g., "Monday, 15 Dec 2025") to YYYY-MM-DD.
        
        Args:
            date_text: Date string from dropdown
            
        Returns:
            Date string in YYYY-MM-DD format or None
        """
        try:
            # Format: "Monday, 15 Dec 2025" or similar
            # Extract the date part (after comma)
            parts = date_text.split(",")
            if len(parts) >= 2:
                date_part = parts[1].strip()
                # Parse date
                dt = datetime.strptime(date_part, "%d %b %Y")
                return dt.strftime("%Y-%m-%d")
            return None
        except (ValueError, AttributeError):
            return None
    
    def get_available_dates(self, commodity: str = "WTI", debug: bool = False) -> List[Dict[str, str]]:
        """
        Get list of available dates from the CME dropdown.
        
        Args:
            commodity: "WTI" or "HH"
            debug: Enable debug logging
            
        Returns:
            List of dictionaries with 'date' (YYYY-MM-DD) and 'display' (original text)
        """
        url = self.WTI_URL if commodity == "WTI" else self.HH_URL
        available_dates = []
        
        try:
            driver = self._get_driver()
            if debug:
                print(f"[DEBUG] Loading URL: {url}")
            driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            if debug:
                print("[DEBUG] Waiting for page to load...")
            time.sleep(3)  # Increased wait time for dynamic content
            
            # Wait for date dropdown to be present
            try:
                date_dropdown = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select, [role='combobox'], input[type='text']"))
                )
                if debug:
                    print(f"[DEBUG] Found date dropdown element: {date_dropdown.tag_name}")
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Could not find date dropdown with initial selector: {e}")
                    # Try to find any select elements
                    selects = driver.find_elements(By.TAG_NAME, "select")
                    print(f"[DEBUG] Found {len(selects)} select elements on page")
                    for i, sel in enumerate(selects):
                        print(f"[DEBUG] Select {i}: id={sel.get_attribute('id')}, class={sel.get_attribute('class')}, visible={sel.is_displayed()}")
            
            time.sleep(2)  # Give page time to fully load
            
            # Look for select element or clickable date element
            try:
                # Try standard select element first
                select_elem = driver.find_element(By.TAG_NAME, "select")
                select = Select(select_elem)
                options = select.options
                if debug:
                    print(f"[DEBUG] Found select with {len(options)} options")
                    # Print first few options to see what we're getting
                    print("[DEBUG] First 5 options:")
                    for i, opt in enumerate(options[:5]):
                        print(f"  [{i}] Text: '{opt.text}' | Value: '{opt.get_attribute('value')}'")
                
                for option in options:
                    if option.text and option.text.strip():
                        date_str = self._parse_date_from_dropdown(option.text)
                        if date_str:
                            available_dates.append({
                                "date": date_str,
                                "display": option.text.strip()
                            })
                        elif debug:
                            print(f"[DEBUG] Could not parse date from: '{option.text}'")
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Standard select failed: {e}")
                    import traceback
                    traceback.print_exc()
                # If not a standard select, try to find clickable elements
                # This is a fallback - may need adjustment based on actual CME structure
                date_elements = driver.find_elements(By.CSS_SELECTOR, "[role='option'], .date-option, .dropdown-item")
                if debug:
                    print(f"[DEBUG] Found {len(date_elements)} clickable date elements")
                for elem in date_elements:
                    text = elem.text.strip()
                    if text:
                        date_str = self._parse_date_from_dropdown(text)
                        if date_str:
                            available_dates.append({
                                "date": date_str,
                                "display": text
                            })
            
            if debug:
                print(f"[DEBUG] Total dates found: {len(available_dates)}")
                if available_dates:
                    print("[DEBUG] Sample dates:")
                    for date_info in available_dates[:3]:
                        print(f"  - {date_info['display']} ({date_info['date']})")
            
        except Exception as e:
            print(f"Error getting available dates: {e}")
            if debug:
                import traceback
                traceback.print_exc()
        finally:
            # Don't close driver here - might be reused
            pass
        
        return available_dates
    
    def _ensure_futures_tab(self, driver):
        """Ensure FUTURES tab is selected."""
        try:
            wait = WebDriverWait(driver, 10)
            # Look for FUTURES tab/button
            futures_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'FUTURES')] | //a[contains(text(), 'FUTURES')] | //div[contains(text(), 'FUTURES')]"))
            )
            
            # Check if it's already selected (might have a class or attribute indicating selection)
            if "selected" not in futures_tab.get_attribute("class").lower() and "active" not in futures_tab.get_attribute("class").lower():
                futures_tab.click()
                time.sleep(1)  # Wait for tab to switch
        except Exception as e:
            print(f"Warning: Could not ensure FUTURES tab is selected: {e}")
            # Continue anyway - might already be selected
    
    def _select_date(self, driver, target_date: str):
        """
        Select date from dropdown.
        
        Args:
            driver: WebDriver instance
            target_date: Date in YYYY-MM-DD format
            
        Returns:
            True if date was found and selected, False otherwise
        """
        try:
            wait = WebDriverWait(driver, 10)
            
            # Find date dropdown/selector
            # Try multiple selectors
            date_selectors = [
                "select",
                "[role='combobox']",
                "input[type='text'][placeholder*='date' i]",
                ".date-selector",
                "[aria-label*='date' i]"
            ]
            
            date_element = None
            for selector in date_selectors:
                try:
                    date_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if date_element:
                        break
                except:
                    continue
            
            if not date_element:
                raise Exception("Could not find date selector")
            
            # If it's a select element
            if date_element.tag_name == "select":
                select = Select(date_element)
                # Try to find matching option
                for option in select.options:
                    option_date = self._parse_date_from_dropdown(option.text)
                    if option_date == target_date:
                        select.select_by_visible_text(option.text)
                        time.sleep(1)
                        return True
            else:
                # If it's a clickable element, click it and then select
                date_element.click()
                time.sleep(1)
                
                # Look for the date option in dropdown
                date_options = driver.find_elements(By.CSS_SELECTOR, "[role='option'], .date-option, .dropdown-item")
                for option in date_options:
                    option_date = self._parse_date_from_dropdown(option.text)
                    if option_date == target_date:
                        option.click()
                        time.sleep(1)
                        return True
            
            return False
        except Exception as e:
            print(f"Error selecting date: {e}")
            return False
    
    def _click_load_all(self, driver):
        """Click the LOAD ALL button with robust error handling and diagnostics."""
        try:
            print("  Searching for LOAD ALL button...")
            wait = WebDriverWait(driver, 10)
            
            # Expanded selector list - try multiple approaches
            selectors = [
                # XPath selectors (case-insensitive text matching)
                ("xpath", "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load all')]"),
                ("xpath", "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'loadall')]"),
                ("xpath", "//button[contains(text(), 'LOAD ALL')]"),
                ("xpath", "//button[contains(text(), 'Load All')]"),
                ("xpath", "//button[contains(text(), 'load all')]"),
                ("xpath", "//a[contains(text(), 'LOAD ALL')]"),
                ("xpath", "//a[contains(text(), 'Load All')]"),
                ("xpath", "//input[@value='LOAD ALL' or @value='Load All' or @value='load all']"),
                # CSS selectors
                ("css", "button[class*='load'][class*='all'], button[class*='load-all']"),
                ("css", "button[id*='load'][id*='all'], button[id*='load-all']"),
                ("css", "a[class*='load'][class*='all'], a[class*='load-all']"),
                # By aria-label or title
                ("xpath", "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load all')]"),
                ("xpath", "//button[contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load all')]"),
            ]
            
            load_all_button = None
            found_selector = None
            
            for selector_type, selector in selectors:
                try:
                    print(f"    Trying {selector_type} selector: {selector[:50]}...")
                    if selector_type == "xpath":
                        buttons = driver.find_elements(By.XPATH, selector)
                    else:  # css
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    print(f"    Found {len(buttons)} element(s) with this selector")
                    
                    for btn in buttons:
                        try:
                            # Check if visible
                            if not btn.is_displayed():
                                continue
                            
                            # Get text from various sources
                            text = (btn.text or btn.get_attribute("value") or 
                                   btn.get_attribute("aria-label") or 
                                   btn.get_attribute("title") or "").strip().upper()
                            
                            print(f"    Checking button with text: '{text[:30]}...'")
                            
                            # Check if it matches LOAD ALL pattern
                            if "LOAD ALL" in text or ("LOAD" in text and "ALL" in text):
                                load_all_button = btn
                                found_selector = f"{selector_type}: {selector}"
                                print(f"  [OK] Found LOAD ALL button using: {found_selector}")
                                break
                        except Exception as btn_error:
                            print(f"    Error checking button: {btn_error}")
                            continue
                    
                    if load_all_button:
                        break
                except Exception as selector_error:
                    print(f"    Error with selector: {selector_error}")
                    continue
            
            if not load_all_button:
                # Last resort: try to find all buttons and check their text
                print("  Trying fallback: checking all visible buttons...")
                try:
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    print(f"    Found {len(all_buttons)} total buttons on page")
                    for btn in all_buttons:
                        try:
                            if btn.is_displayed():
                                text = btn.text.strip().upper()
                                if "LOAD ALL" in text or text == "LOAD ALL":
                                    load_all_button = btn
                                    print(f"  [OK] Found LOAD ALL button via fallback method")
                                    break
                        except:
                            continue
                except Exception as fallback_error:
                    print(f"    Fallback search failed: {fallback_error}")
            
            if not load_all_button:
                print("  [ERROR] LOAD ALL button not found with any method")
                raise Exception("LOAD ALL button not found")
            
            # Scroll button into view
            print("  Scrolling button into view...")
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", load_all_button)
                time.sleep(0.5)  # Brief wait after scroll
            except Exception as scroll_error:
                print(f"    Warning: Could not scroll to button: {scroll_error}")
            
            # Wait for button to be clickable
            print("  Waiting for button to be clickable...")
            try:
                wait.until(EC.element_to_be_clickable(load_all_button))
            except Exception as clickable_error:
                print(f"    Warning: Button may not be clickable: {clickable_error}")
            
            # Try to click the button
            print("  Attempting to click LOAD ALL button...")
            try:
                load_all_button.click()
                print("  [OK] Button clicked successfully")
            except Exception as click_error:
                print(f"    Normal click failed ({click_error}), trying JavaScript click...")
                try:
                    driver.execute_script("arguments[0].click();", load_all_button)
                    print("  [OK] Button clicked using JavaScript")
                except Exception as js_error:
                    print(f"    JavaScript click also failed: {js_error}")
                    raise Exception(f"Could not click LOAD ALL button: {click_error}, {js_error}")
            
            # Wait for table to expand/load more data
            print("  Waiting for table to load additional data...")
            time.sleep(2)  # Initial wait
            
            # Wait for table to be present and potentially expanded
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                # Additional wait for dynamic content to load
                time.sleep(3)  # Give more time for extended contracts to load
                print("  [OK] Table loaded, waiting for data expansion...")
            except Exception as table_error:
                print(f"    Warning: Table wait error: {table_error}")
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error clicking LOAD ALL: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_month_to_expiry_date(self, month_str: str) -> Optional[str]:
        """
        Parse month string (e.g., "JAN 26") to expiry date (last day of month).
        
        Examples:
        - "JAN 26" -> "2026-01-31"
        - "DEC 24" -> "2024-12-31"
        - "MAR 30" -> "2030-03-31"
        - "FEB 24" -> "2024-02-29" (leap year)
        
        Args:
            month_str: Month string in format "MMM YY" or "MMM YYYY" (e.g., "JAN 26")
            
        Returns:
            Date string in YYYY-MM-DD format (last day of month) or None if parsing fails
        """
        if not month_str:
            return None
        
        # Month abbreviations to numbers
        month_map = {
            "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
            "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
            "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
        }
        
        # Clean and split the month string
        month_str = month_str.strip().upper()
        parts = month_str.split()
        
        if len(parts) < 2:
            return None
        
        month_abbr = parts[0]
        year_str = parts[1]
        
        # Get month number
        month_num = month_map.get(month_abbr)
        if not month_num:
            return None
        
        # Parse year (handle 2-digit and 4-digit years)
        try:
            if len(year_str) == 2:
                # 2-digit year: assume 2000s if < 50, else 1900s
                year_num = int(year_str)
                year = 2000 + year_num if year_num < 50 else 1900 + year_num
            elif len(year_str) == 4:
                year = int(year_str)
            else:
                return None
        except ValueError:
            return None
        
        # Get last day of month using calendar.monthrange
        # monthrange returns (weekday_of_first_day, number_of_days_in_month)
        _, last_day = calendar.monthrange(year, month_num)
        
        # Format as YYYY-MM-DD
        return f"{year:04d}-{month_num:02d}-{last_day:02d}"
    
    def _get_current_date(self, driver) -> Optional[str]:
        """
        Extract the current settlement date from the page.
        Checks selected dropdown option, page title, or table header.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Date string in YYYY-MM-DD format or None
        """
        try:
            # Strategy 1: Check selected option in date dropdown
            try:
                select_elem = driver.find_element(By.TAG_NAME, "select")
                select = Select(select_elem)
                selected_option = select.first_selected_option
                if selected_option and selected_option.text:
                    date_str = self._parse_date_from_dropdown(selected_option.text)
                    if date_str:
                        return date_str
            except:
                pass
            
            # Strategy 2: Check page title or header for date
            try:
                # Look for date in page title
                page_title = driver.title
                # Try to extract date from title (various formats)
                date_patterns = [
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, page_title)
                    if match:
                        date_str = self._parse_settlement_date(match.group(1))
                        if date_str:
                            return date_str
            except:
                pass
            
            # Strategy 3: Check table header or first row for settlement date
            try:
                tables = driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    # Check header row
                    headers = table.find_elements(By.TAG_NAME, "th")
                    for header in headers:
                        text = header.text.strip()
                        if "settlement" in text.lower() or "date" in text.lower():
                            # Try to extract date from header text
                            date_str = self._parse_settlement_date(text)
                            if date_str:
                                return date_str
            except:
                pass
            
            # Strategy 4: Use today's date as fallback (prior business day logic would go here)
            # For now, return None and let caller handle it
            return None
            
        except Exception as e:
            print(f"Error extracting date from page: {e}")
            return None
    
    def _parse_settlement_date(self, date_str: str) -> Optional[str]:
        """
        Parse settlement date string to ISO format.
        Helper method for date extraction.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            ISO date string (YYYY-MM-DD) or None
        """
        # Try various date formats
        date_formats = [
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%m-%d-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    def _parse_table_from_element(self, driver, table, scrape_date: str, commodity: str) -> List[Dict]:
        """
        Parse a specific table element using BeautifulSoup for robust HTML parsing.
        
        Args:
            driver: WebDriver instance (for context)
            table: Table WebElement to parse
            scrape_date: Date string in YYYY-MM-DD format
            commodity: "WTI" or "HH"
            
        Returns:
            List of futures contract records
        """
        records = []
        
        try:
            # Get the table's HTML and parse with BeautifulSoup
            table_html = table.get_attribute('outerHTML')
            soup = BeautifulSoup(table_html, 'html.parser')
            
            # Find the table element in the soup
            table_soup = soup.find('table')
            if not table_soup:
                print("  Error: Could not find table element in HTML")
                return records
            
            # Get all rows using BeautifulSoup
            rows = table_soup.find_all('tr')
            print(f"  Found {len(rows)} row(s) in table")
            
            if len(rows) < 2:
                print(f"  Table has only {len(rows)} row(s), expected at least 2 (header + data)")
                return records
            
            # Parse header row to find column indices
            header_row = rows[0]
            header_cells = header_row.find_all(['th', 'td'])
            
            if not header_cells:
                print("  Error: No header cells found in first row")
                raise Exception("No header cells found - table structure may have changed")
            
            print(f"  Found {len(header_cells)} header cell(s)")
            header_map = {}
            header_texts = []
            for idx, cell in enumerate(header_cells):
                text = cell.get_text(strip=True)
                header_texts.append(text)
                text_upper = text.upper()
                if "MONTH" in text_upper:
                    header_map["month"] = idx
                elif "OPEN" in text_upper and "INTEREST" not in text_upper:
                    header_map["open"] = idx
                elif "HIGH" in text_upper:
                    header_map["high"] = idx
                elif "LOW" in text_upper:
                    header_map["low"] = idx
                elif "LAST" in text_upper:
                    header_map["last"] = idx
                elif "CHANGE" in text_upper:
                    header_map["change"] = idx
                elif "SETTLE" in text_upper:
                    header_map["settle"] = idx
                elif "VOLUME" in text_upper or "EST. VOLUME" in text_upper:
                    header_map["est_volume"] = idx
                elif "OI" in text_upper or "OPEN INTEREST" in text_upper or "PRIOR DAY OI" in text_upper:
                    header_map["prior_day_oi"] = idx
            
            print(f"  Header texts: {header_texts}")
            print(f"  Header mapping: {header_map}")
            
            # Check if we found the SETTLE column (required)
            if "settle" not in header_map:
                print(f"  Error: SETTLE column not found in header. Found columns: {list(header_map.keys())}")
                raise Exception(f"SETTLE column not found in table header. Found: {list(header_map.keys())}. Headers: {header_texts}")
            
            # Process data rows using BeautifulSoup
            rows_processed = 0
            rows_with_settle = 0
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                rows_processed += 1
                
                # Extract month
                month_idx = header_map.get("month", 0)
                if month_idx >= len(cells):
                    continue
                
                month = cells[month_idx].get_text(strip=True)
                if not month or month == "":
                    continue
                
                # Skip if this looks like a header or separator row
                if month.upper() in ["MONTH", "TOTAL", ""]:
                    continue
                
                # Parse month to expiry date (last day of month)
                contract_expiry_date = self._parse_month_to_expiry_date(month)
                
                # Extract all price fields
                record = {
                    "date": scrape_date,
                    "commodity": commodity,
                    "month": month,
                    "contract_expiry_date": contract_expiry_date,
                    "open": None,
                    "high": None,
                    "low": None,
                    "last": None,
                    "change": None,
                    "settle": None,
                    "est_volume": None,
                    "prior_day_oi": None,
                    "created_at": datetime.now().isoformat()
                }
                
                # Parse each field using BeautifulSoup's get_text
                if "open" in header_map:
                    idx = header_map["open"]
                    if idx < len(cells):
                        record["open"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "high" in header_map:
                    idx = header_map["high"]
                    if idx < len(cells):
                        record["high"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "low" in header_map:
                    idx = header_map["low"]
                    if idx < len(cells):
                        record["low"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "last" in header_map:
                    idx = header_map["last"]
                    if idx < len(cells):
                        record["last"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "change" in header_map:
                    idx = header_map["change"]
                    if idx < len(cells):
                        record["change"] = self._parse_change(cells[idx].get_text(strip=True))
                
                if "settle" in header_map:
                    idx = header_map["settle"]
                    if idx < len(cells):
                        record["settle"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "est_volume" in header_map:
                    idx = header_map["est_volume"]
                    if idx < len(cells):
                        record["est_volume"] = self._parse_price(cells[idx].get_text(strip=True))
                
                if "prior_day_oi" in header_map:
                    idx = header_map["prior_day_oi"]
                    if idx < len(cells):
                        record["prior_day_oi"] = self._parse_price(cells[idx].get_text(strip=True))
                
                # Only add record if we have at least a settle price
                if record["settle"] is not None:
                    records.append(record)
                    rows_with_settle += 1
            
            print(f"  Processed {rows_processed} data row(s), {rows_with_settle} with settle price")
            
            if len(records) == 0 and rows_processed > 0:
                print(f"  Warning: Processed {rows_processed} rows but none had settle prices")
            
        except Exception as e:
            error_msg = f"Error parsing table: {e}"
            print(f"  {error_msg}")
            raise  # Re-raise to let caller know this table failed
        
        return records
    
    def scrape_wti(self, date: Optional[str] = None) -> List[Dict]:
        """
        Scrape WTI Crude Oil futures settlement prices.
        Uses the default date (prior business day) on the page.
        
        Args:
            date: Optional date string in YYYY-MM-DD format (ignored - uses page default)
            
        Returns:
            List of futures contract records
        """
        return self._scrape_commodity(self.WTI_URL, "WTI")
    
    def scrape_henry_hub(self, date: Optional[str] = None) -> List[Dict]:
        """
        Scrape Henry Hub Natural Gas futures settlement prices.
        Uses the default date (prior business day) on the page.
        
        Args:
            date: Optional date string in YYYY-MM-DD format (ignored - uses page default)
            
        Returns:
            List of futures contract records
        """
        return self._scrape_commodity(self.HH_URL, "HH")
    
    def _scrape_commodity(self, url: str, commodity: str) -> List[Dict]:
        """
        Scrape futures settlement prices from CME page using Selenium.
        Uses the default date (prior business day) that's automatically selected on the page.
        Only clicks LOAD ALL button to load all contracts.
        
        Args:
            url: CME settlements page URL
            commodity: "WTI" or "HH"
            
        Returns:
            List of futures contract records
        """
        records = []
        driver = None
        
        try:
            driver = self._get_driver()
            if driver is None:
                raise Exception("Failed to initialize Chrome WebDriver")
            
            driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Additional wait for dynamic content to load
            
            # Ensure FUTURES tab is selected
            self._ensure_futures_tab(driver)
            
            # Extract the current date from the page (default/prior business day)
            scrape_date = self._get_current_date(driver)
            if not scrape_date:
                # Fallback: use yesterday's date (prior business day approximation)
                from datetime import timedelta
                scrape_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                print(f"Warning: Could not extract date from page, using fallback: {scrape_date}")
            else:
                print(f"Detected settlement date: {scrape_date}")
            
            # Click LOAD ALL button to load all contracts
            if not self._click_load_all(driver):
                print("Warning: Failed to click LOAD ALL button, attempting to scrape anyway...")
                # Continue anyway - might have partial data
            
            # Wait a bit more for table to fully populate
            time.sleep(2)
            
            # Try parsing each table (there might be multiple tables on the page)
            tables = driver.find_elements(By.TAG_NAME, "table")
            records = []
            
            for table_idx, table in enumerate(tables):
                print(f"Attempting to parse table {table_idx + 1} of {len(tables)}...")
                try:
                    table_records = self._parse_table_from_element(driver, table, scrape_date, commodity)
                    if len(table_records) > 0:
                        print(f"Found {len(table_records)} records in table {table_idx + 1}")
                        records = table_records
                        break
                except Exception as parse_error:
                    print(f"Error parsing table {table_idx + 1}: {parse_error}")
                    continue
            
            if len(records) == 0:
                # Provide diagnostic information
                try:
                    page_title = driver.title
                    error_msg = (
                        f"No records found after scraping. "
                        f"Page title: {page_title}, "
                        f"Tables found: {len(tables)}, "
                        f"Date: {scrape_date}. "
                        f"Tried parsing all {len(tables)} table(s) but found no valid records. "
                        f"Check terminal output for detailed diagnostics."
                    )
                    print(error_msg)
                    raise Exception(error_msg)
                except Exception as diagnostic_error:
                    # If we can't get diagnostics, raise original error
                    if "No records found" not in str(diagnostic_error):
                        raise diagnostic_error
                    raise
            
            # Rate limiting
            time.sleep(self.rate_limit_seconds)
            
        except Exception as e:
            error_msg = f"Error scraping {commodity} from CME: {str(e)}"
            print(error_msg)
            # Log exception type for debugging
            print(f"Exception type: {type(e).__name__}")
            # Re-raise the exception - Streamlit will handle displaying it properly
            raise
        finally:
            # Don't close driver here - might be reused for multiple scrapes
            pass
        
        return records
    
    def scrape_all(self) -> Dict[str, List[Dict]]:
        """
        Scrape both WTI and Henry Hub futures.
        Uses the default date (prior business day) on each page.
        
        Returns:
            Dictionary with "WTI" and "HH" keys containing lists of records
        """
        results = {
            "WTI": [],
            "HH": []
        }
        
        try:
            print("Scraping WTI futures (using default date)...")
            results["WTI"] = self.scrape_wti()
            print(f"Found {len(results['WTI'])} WTI contracts")
            
            time.sleep(self.rate_limit_seconds)
            
            print("Scraping Henry Hub futures (using default date)...")
            results["HH"] = self.scrape_henry_hub()
            print(f"Found {len(results['HH'])} HH contracts")
        finally:
            # Close driver after all scraping is done
            self._close_driver()
        
        return results
    
    def _parse_contract_symbol(self, symbol: str) -> Optional[Tuple[str, str]]:
        """
        Parse CME contract symbol to extract commodity and month.
        
        Examples:
        - "CLZ2024" -> ("WTI", "2024-12")
        - "NGZ2024" -> ("HH", "2024-12")
        
        Args:
            symbol: Contract symbol string (e.g., "CLZ2024", "NGZ2024")
            
        Returns:
            Tuple of (commodity, contractMonth) or None if parsing fails
        """
        # CME contract month codes
        month_codes = {
            "F": "01", "G": "02", "H": "03", "J": "04",
            "K": "05", "M": "06", "N": "07", "Q": "08",
            "U": "09", "V": "10", "X": "11", "Z": "12"
        }
        
        # Match pattern: CL or NG followed by month code and year
        match = re.match(r"^(CL|NG)([FGHJKMNQUVXZ])(\d{4})$", symbol)
        if not match:
            return None
        
        commodity_code, month_code, year = match.groups()
        commodity = "WTI" if commodity_code == "CL" else "HH"
        
        month = month_codes.get(month_code)
        if not month:
            return None
        
        contract_month = f"{year}-{month}"
        return (commodity, contract_month)
    
    def scrape_and_save(self) -> Dict[str, Dict[str, int]]:
        """
        Scrape all futures and save to database.
        Uses lib.db.save_futures_data for saving.
        
        Returns:
            Dictionary with scrape results and save statistics
        """
        from lib.db import save_futures_data
        
        scraped_data = self.scrape_all()
        
        results = {}
        for commodity, records in scraped_data.items():
            if records:
                save_result = save_futures_data(records)
                results[commodity] = {
                    "scraped": len(records),
                    "saved": save_result.get("saved", 0),
                    "skipped": save_result.get("skipped", 0),
                }
            else:
                results[commodity] = {
                    "scraped": 0,
                    "saved": 0,
                    "skipped": 0,
                }
        
        return results
    
    def __del__(self):
        """Cleanup: close driver when object is destroyed."""
        self._close_driver()

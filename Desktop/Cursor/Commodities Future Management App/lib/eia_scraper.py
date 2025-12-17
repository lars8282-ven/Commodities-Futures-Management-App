"""
EIA (U.S. Energy Information Administration) spot price scraper.
Scrapes WTI and Henry Hub spot prices from EIA websites.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from typing import List, Dict, Optional, Tuple
from lib.instant_client import get_db
import os

class EIAScraper:
    """Scraper for EIA spot prices."""
    
    WTI_URL = "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=M"
    HH_URL = "https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm"
    
    def __init__(self):
        self.db = get_db()
        self.rate_limit_seconds = float(os.getenv("SCRAPE_RATE_LIMIT_SECONDS", "2"))
        self.user_agent = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string to ISO format.
        Handles various EIA date formats.
        """
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%Y-%m",
            "%b %Y",
            "%B %Y",
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # For monthly data, use first day of month
                if fmt in ["%Y-%m", "%b %Y", "%B %Y"]:
                    return dt.strftime("%Y-%m-01")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float."""
        try:
            cleaned = price_str.replace(",", "").replace("$", "").strip()
            # Handle "NA", "-", empty strings
            if cleaned in ["NA", "-", "", "N/A"]:
                return None
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def scrape_wti(self) -> List[Dict[str, any]]:
        """Scrape WTI spot prices from EIA."""
        return self._scrape_commodity(self.WTI_URL, "WTI")
    
    def scrape_henry_hub(self) -> List[Dict[str, any]]:
        """Scrape Henry Hub spot prices from EIA."""
        return self._scrape_commodity(self.HH_URL, "HH")
    
    def _scrape_commodity(self, url: str, commodity: str) -> List[Dict[str, any]]:
        """
        Scrape spot prices from EIA page.
        
        Args:
            url: EIA data page URL
            commodity: "WTI" or "HH"
            
        Returns:
            List of spot price records
        """
        records = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # EIA typically uses tables with historical data
            # Look for tables containing price data
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                
                # Find header row to identify columns
                header_row = None
                date_col_idx = None
                price_col_idx = None
                
                for i, row in enumerate(rows):
                    cells = row.find_all(["th", "td"])
                    cell_texts = [cell.get_text(strip=True).lower() for cell in cells]
                    
                    # Look for header row with "date" and price-related columns
                    if any("date" in text or "year" in text for text in cell_texts):
                        header_row = i
                        # Find date column
                        for j, text in enumerate(cell_texts):
                            if "date" in text or "year" in text:
                                date_col_idx = j
                            # Find price column (often "price", "dollars", or commodity-specific)
                            if any(keyword in text for keyword in ["price", "dollar", "per barrel", "per mmbtu"]):
                                price_col_idx = j
                        break
                
                if header_row is None or date_col_idx is None or price_col_idx is None:
                    continue
                
                # Parse data rows
                for row in rows[header_row + 1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) <= max(date_col_idx, price_col_idx):
                        continue
                    
                    date_str = cells[date_col_idx].get_text(strip=True)
                    price_str = cells[price_col_idx].get_text(strip=True)
                    
                    # Parse date
                    date = self._parse_date(date_str)
                    if not date:
                        continue
                    
                    # Parse price
                    price = self._parse_price(price_str)
                    if price is None:
                        continue
                    
                    record = {
                        "commodity": commodity,
                        "price": price,
                        "date": date,
                        "source": "EIA",
                        "createdAt": datetime.now().isoformat(),
                    }
                    
                    records.append(record)
            
            # Rate limiting
            time.sleep(self.rate_limit_seconds)
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {commodity} from EIA: {e}")
        except Exception as e:
            print(f"Unexpected error scraping {commodity}: {e}")
        
        return records
    
    def scrape_all(self) -> Dict[str, List[Dict[str, any]]]:
        """
        Scrape both WTI and Henry Hub spot prices.
        
        Returns:
            Dictionary with "WTI" and "HH" keys containing lists of records
        """
        results = {
            "WTI": [],
            "HH": []
        }
        
        print("Scraping WTI spot prices...")
        results["WTI"] = self.scrape_wti()
        print(f"Found {len(results['WTI'])} WTI spot price records")
        
        time.sleep(self.rate_limit_seconds)
        
        print("Scraping Henry Hub spot prices...")
        results["HH"] = self.scrape_henry_hub()
        print(f"Found {len(results['HH'])} HH spot price records")
        
        return results
    
    def save_to_db(self, records: List[Dict[str, any]]) -> Tuple[int, int]:
        """
        Save scraped records to InstantDB with deduplication.
        
        Args:
            records: List of spot price records
            
        Returns:
            Tuple of (saved_count, skipped_count)
        """
        saved = 0
        skipped = 0
        
        for record in records:
            # Check for existing record
            existing = self.db.query(
                "spotPrices",
                filters={
                    "commodity": record["commodity"],
                    "date": record["date"],
                }
            )
            
            if existing:
                # Update existing record
                existing_id = existing[0].get("id")
                if existing_id:
                    updated = self.db.update("spotPrices", existing_id, {
                        "price": record["price"],
                    })
                    if updated:
                        saved += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1
            else:
                # Insert new record
                result = self.db.insert("spotPrices", record)
                if result:
                    saved += 1
                else:
                    skipped += 1
        
        return (saved, skipped)
    
    def scrape_and_save(self) -> Dict[str, Dict[str, int]]:
        """
        Scrape all spot prices and save to database.
        
        Returns:
            Dictionary with scrape results and save statistics
        """
        scraped_data = self.scrape_all()
        
        results = {}
        for commodity, records in scraped_data.items():
            saved, skipped = self.save_to_db(records)
            results[commodity] = {
                "scraped": len(records),
                "saved": saved,
                "skipped": skipped,
            }
        
        # Log scrape
        self._log_scrape(results)
        
        return results
    
    def _log_scrape(self, results: Dict[str, Dict[str, int]]):
        """Log scrape results to database."""
        total_scraped = sum(r["scraped"] for r in results.values())
        total_saved = sum(r["saved"] for r in results.values())
        
        log_entry = {
            "source": "EIA",
            "commodity": "BOTH",
            "status": "success" if total_saved > 0 else "failed",
            "recordsScraped": total_scraped,
            "scrapeDate": datetime.now().isoformat(),
            "createdAt": datetime.now().isoformat(),
        }
        
        self.db.insert("scrapeLogs", log_entry)


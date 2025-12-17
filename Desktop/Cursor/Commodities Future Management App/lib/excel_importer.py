"""
Excel file importer for backfilling historical futures and spot price data.
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from lib.instant_client import get_db
import os

class ExcelImporter:
    """Importer for Excel files containing historical price data."""
    
    def __init__(self):
        self.db = get_db()
    
    def import_futures_from_excel(self, file_path: str, commodity: str) -> Dict[str, any]:
        """
        Import futures settlement prices from Excel file.
        
        Expected Excel format:
        - Column headers: Contract, SettlementDate, SettlementPrice, Volume (optional), OpenInterest (optional)
        - Or: ContractMonth, SettlementDate, SettlementPrice, ...
        
        Args:
            file_path: Path to Excel file
            commodity: "WTI" or "HH"
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Normalize column names (case-insensitive)
            df.columns = df.columns.str.strip().str.lower()
            
            # Map common column name variations
            column_mapping = {
                "contract": ["contract", "contractsymbol", "symbol", "contract symbol"],
                "contractmonth": ["contractmonth", "contract month", "month", "expiry"],
                "settlementdate": ["settlementdate", "settlement date", "date", "trade date"],
                "settlementprice": ["settlementprice", "settlement price", "price", "settle"],
                "volume": ["volume", "vol"],
                "openinterest": ["openinterest", "open interest", "oi"],
            }
            
            # Find actual column names
            actual_columns = {}
            for standard_name, variations in column_mapping.items():
                for col in df.columns:
                    if col in variations:
                        actual_columns[standard_name] = col
                        break
            
            if "settlementdate" not in actual_columns or "settlementprice" not in actual_columns:
                return {
                    "success": False,
                    "error": "Required columns (SettlementDate, SettlementPrice) not found",
                    "imported": 0,
                    "skipped": 0,
                }
            
            records = []
            skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Extract data
                    date_str = str(row[actual_columns["settlementdate"]])
                    price = row[actual_columns["settlementprice"]]
                    
                    # Skip if missing required data
                    if pd.isna(price) or pd.isna(date_str):
                        skipped += 1
                        continue
                    
                    # Parse date
                    if isinstance(date_str, str):
                        try:
                            date_obj = pd.to_datetime(date_str)
                        except:
                            skipped += 1
                            continue
                    else:
                        date_obj = date_str
                    
                    settlement_date = date_obj.strftime("%Y-%m-%d") if hasattr(date_obj, 'strftime') else str(date_obj)
                    
                    # Parse price
                    try:
                        settlement_price = float(price)
                    except (ValueError, TypeError):
                        skipped += 1
                        continue
                    
                    # Extract contract information
                    contract_symbol = None
                    contract_month = None
                    
                    if "contract" in actual_columns:
                        contract_symbol = str(row[actual_columns["contract"]])
                        # Try to parse contract month from symbol
                        from lib.scraper import CMEScraper
                        scraper = CMEScraper()
                        contract_info = scraper._parse_contract_symbol(contract_symbol)
                        if contract_info:
                            _, contract_month = contract_info
                    
                    if "contractmonth" in actual_columns:
                        month_str = str(row[actual_columns["contractmonth"]])
                        # Try to parse contract month
                        try:
                            month_obj = pd.to_datetime(month_str)
                            contract_month = month_obj.strftime("%Y-%m")
                        except:
                            # Try YYYY-MM format
                            if len(month_str) >= 7 and month_str[4] == "-":
                                contract_month = month_str[:7]
                    
                    if not contract_month:
                        # Try to infer from date (assume front month)
                        date_obj = pd.to_datetime(settlement_date)
                        contract_month = date_obj.strftime("%Y-%m")
                    
                    # Extract optional fields
                    volume = None
                    if "volume" in actual_columns:
                        vol_val = row[actual_columns["volume"]]
                        if not pd.isna(vol_val):
                            try:
                                volume = float(vol_val)
                            except:
                                pass
                    
                    open_interest = None
                    if "openinterest" in actual_columns:
                        oi_val = row[actual_columns["openinterest"]]
                        if not pd.isna(oi_val):
                            try:
                                open_interest = float(oi_val)
                            except:
                                pass
                    
                    record = {
                        "commodity": commodity,
                        "contractMonth": contract_month,
                        "contractSymbol": contract_symbol or f"{commodity}{contract_month}",
                        "settlementPrice": settlement_price,
                        "settlementDate": settlement_date,
                        "volume": volume,
                        "openInterest": open_interest,
                        "source": "EXCEL",
                        "createdAt": datetime.now().isoformat(),
                        "updatedAt": datetime.now().isoformat(),
                    }
                    
                    records.append(record)
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    skipped += 1
                    continue
            
            # Save to database
            saved, db_skipped = self._save_futures_records(records)
            
            return {
                "success": True,
                "imported": saved,
                "skipped": skipped + db_skipped,
                "total_rows": len(df),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "imported": 0,
                "skipped": 0,
            }
    
    def import_spot_from_excel(self, file_path: str, commodity: str) -> Dict[str, any]:
        """
        Import spot prices from Excel file.
        
        Expected Excel format:
        - Column headers: Date, Price
        
        Args:
            file_path: Path to Excel file
            commodity: "WTI" or "HH"
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            
            # Find date and price columns
            date_col = None
            price_col = None
            
            for col in df.columns:
                if col in ["date", "trade date", "pricing date"]:
                    date_col = col
                elif col in ["price", "spot price", "spot", "close"]:
                    price_col = col
            
            if not date_col or not price_col:
                return {
                    "success": False,
                    "error": "Required columns (Date, Price) not found",
                    "imported": 0,
                    "skipped": 0,
                }
            
            records = []
            skipped = 0
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row[date_col])
                    price = row[price_col]
                    
                    if pd.isna(price) or pd.isna(date_str):
                        skipped += 1
                        continue
                    
                    # Parse date
                    try:
                        date_obj = pd.to_datetime(date_str)
                        date = date_obj.strftime("%Y-%m-%d")
                    except:
                        skipped += 1
                        continue
                    
                    # Parse price
                    try:
                        price_float = float(price)
                    except (ValueError, TypeError):
                        skipped += 1
                        continue
                    
                    record = {
                        "commodity": commodity,
                        "price": price_float,
                        "date": date,
                        "source": "EXCEL",
                        "createdAt": datetime.now().isoformat(),
                    }
                    
                    records.append(record)
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    skipped += 1
                    continue
            
            # Save to database
            saved, db_skipped = self._save_spot_records(records)
            
            return {
                "success": True,
                "imported": saved,
                "skipped": skipped + db_skipped,
                "total_rows": len(df),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "imported": 0,
                "skipped": 0,
            }
    
    def _save_futures_records(self, records: List[Dict[str, any]]) -> Tuple[int, int]:
        """Save futures records to database with deduplication."""
        saved = 0
        skipped = 0
        
        for record in records:
            existing = self.db.query(
                "futuresContracts",
                filters={
                    "commodity": record["commodity"],
                    "contractMonth": record["contractMonth"],
                    "settlementDate": record["settlementDate"],
                    "source": "EXCEL",
                }
            )
            
            if existing:
                skipped += 1
            else:
                result = self.db.insert("futuresContracts", record)
                if result:
                    saved += 1
                else:
                    skipped += 1
        
        return (saved, skipped)
    
    def _save_spot_records(self, records: List[Dict[str, any]]) -> Tuple[int, int]:
        """Save spot price records to database with deduplication."""
        saved = 0
        skipped = 0
        
        for record in records:
            existing = self.db.query(
                "spotPrices",
                filters={
                    "commodity": record["commodity"],
                    "date": record["date"],
                    "source": "EXCEL",
                }
            )
            
            if existing:
                skipped += 1
            else:
                result = self.db.insert("spotPrices", record)
                if result:
                    saved += 1
                else:
                    skipped += 1
        
        return (saved, skipped)


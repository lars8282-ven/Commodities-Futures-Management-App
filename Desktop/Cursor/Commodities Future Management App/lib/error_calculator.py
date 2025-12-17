"""
Error calculation engine for comparing futures settlement prices with spot prices.
Calculates both absolute and percentage errors.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from lib.instant_client import get_db
import math

class ErrorCalculator:
    """Calculator for errors between futures and spot prices."""
    
    def __init__(self):
        self.db = get_db()
    
    def calculate_errors(self, commodity: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
        """
        Calculate errors for all futures contracts matched with spot prices.
        
        Args:
            commodity: Optional filter for "WTI" or "HH"
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            Dictionary with calculation results
        """
        # Get all futures contracts
        futures_filters = {}
        if commodity:
            futures_filters["commodity"] = commodity
        if start_date:
            futures_filters["settlementDate"] = {"$gte": start_date}
        if end_date:
            if "settlementDate" in futures_filters:
                futures_filters["settlementDate"]["$lte"] = end_date
            else:
                futures_filters["settlementDate"] = {"$lte": end_date}
        
        futures_contracts = self.db.query("futuresContracts", filters=futures_filters if futures_filters else None)
        
        if not futures_contracts:
            return {
                "success": False,
                "error": "No futures contracts found",
                "calculated": 0,
                "skipped": 0,
            }
        
        calculated = 0
        skipped = 0
        errors = []
        
        for futures in futures_contracts:
            try:
                # Get matching spot price
                spot_filters = {
                    "commodity": futures["commodity"],
                    "date": futures["settlementDate"],
                }
                
                spot_prices = self.db.query("spotPrices", filters=spot_filters)
                
                if not spot_prices:
                    skipped += 1
                    continue
                
                spot_price = spot_prices[0]
                
                # Calculate errors
                futures_price = float(futures["settlementPrice"])
                spot_price_value = float(spot_price["price"])
                
                # Absolute error
                absolute_error = abs(futures_price - spot_price_value)
                
                # Percentage error (avoid division by zero)
                if spot_price_value != 0:
                    percentage_error = ((futures_price - spot_price_value) / spot_price_value) * 100
                else:
                    percentage_error = None
                
                # Calculate days to expiry (approximate from contract month)
                days_to_expiry = self._calculate_days_to_expiry(
                    futures["settlementDate"],
                    futures["contractMonth"]
                )
                
                # Check if error calculation already exists
                existing = self.db.query(
                    "errorCalculations",
                    filters={
                        "futuresContractId": futures.get("id"),
                        "spotPriceId": spot_price.get("id"),
                    }
                )
                
                error_record = {
                    "futuresContractId": futures.get("id"),
                    "spotPriceId": spot_price.get("id"),
                    "contractMonth": futures["contractMonth"],
                    "commodity": futures["commodity"],
                    "futuresPrice": futures_price,
                    "spotPrice": spot_price_value,
                    "absoluteError": absolute_error,
                    "percentageError": percentage_error,
                    "date": futures["settlementDate"],
                    "daysToExpiry": days_to_expiry,
                    "createdAt": datetime.now().isoformat(),
                }
                
                if existing:
                    # Update existing
                    existing_id = existing[0].get("id")
                    if existing_id:
                        self.db.update("errorCalculations", existing_id, error_record)
                        calculated += 1
                else:
                    # Insert new
                    result = self.db.insert("errorCalculations", error_record)
                    if result:
                        calculated += 1
                    else:
                        skipped += 1
                
                errors.append(error_record)
                
            except Exception as e:
                print(f"Error calculating error for futures contract {futures.get('id')}: {e}")
                skipped += 1
                continue
        
        return {
            "success": True,
            "calculated": calculated,
            "skipped": skipped,
            "total_futures": len(futures_contracts),
            "errors": errors,
        }
    
    def _calculate_days_to_expiry(self, settlement_date: str, contract_month: str) -> Optional[int]:
        """
        Calculate approximate days to expiry from contract month.
        
        Args:
            settlement_date: Settlement date (YYYY-MM-DD)
            contract_month: Contract month (YYYY-MM)
            
        Returns:
            Days to expiry or None if calculation fails
        """
        try:
            settle_dt = datetime.strptime(settlement_date, "%Y-%m-%d")
            
            # Contract month represents the expiry month
            # Typically futures expire on the 3rd business day before the 25th
            # For simplicity, use the last day of the contract month
            year, month = contract_month.split("-")
            if month == "12":
                expiry_year = int(year) + 1
                expiry_month = 1
            else:
                expiry_year = int(year)
                expiry_month = int(month) + 1
            
            # Use 25th of contract month as approximate expiry
            expiry_dt = datetime(int(year), int(month), 25)
            
            delta = expiry_dt - settle_dt
            return delta.days if delta.days >= 0 else None
            
        except Exception as e:
            return None
    
    def get_error_statistics(self, commodity: Optional[str] = None, contract_month: Optional[str] = None) -> Dict[str, any]:
        """
        Get statistical summary of errors.
        
        Args:
            commodity: Optional filter for "WTI" or "HH"
            contract_month: Optional filter for contract month
            
        Returns:
            Dictionary with error statistics
        """
        filters = {}
        if commodity:
            filters["commodity"] = commodity
        if contract_month:
            filters["contractMonth"] = contract_month
        
        errors = self.db.query("errorCalculations", filters=filters if filters else None)
        
        if not errors:
            return {
                "count": 0,
                "absolute_error": {},
                "percentage_error": {},
            }
        
        absolute_errors = [e["absoluteError"] for e in errors if e.get("absoluteError") is not None]
        percentage_errors = [e["percentageError"] for e in errors if e.get("percentageError") is not None]
        
        def calculate_stats(values: List[float]) -> Dict[str, float]:
            if not values:
                return {}
            
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            
            return {
                "mean": sum(values) / n,
                "median": sorted_vals[n // 2] if n > 0 else 0,
                "min": min(values),
                "max": max(values),
                "std_dev": math.sqrt(sum((x - sum(values) / n) ** 2 for x in values) / n) if n > 1 else 0,
                "p25": sorted_vals[n // 4] if n >= 4 else sorted_vals[0],
                "p75": sorted_vals[3 * n // 4] if n >= 4 else sorted_vals[-1],
                "p90": sorted_vals[9 * n // 10] if n >= 10 else sorted_vals[-1],
                "p95": sorted_vals[19 * n // 20] if n >= 20 else sorted_vals[-1],
            }
        
        return {
            "count": len(errors),
            "absolute_error": calculate_stats(absolute_errors),
            "percentage_error": calculate_stats(percentage_errors),
        }


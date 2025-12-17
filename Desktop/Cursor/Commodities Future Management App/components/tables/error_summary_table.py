"""
Error summary table component.
"""
import pandas as pd
from typing import List, Dict, Optional
from lib.error_calculator import ErrorCalculator

def create_error_summary_table(
    errors: List[Dict],
    group_by: str = "commodity",  # "commodity", "contractMonth", or "none"
    commodity: Optional[str] = None
) -> pd.DataFrame:
    """
    Create error summary statistics table.
    
    Args:
        errors: List of error calculation records
        group_by: How to group the statistics
        commodity: Optional commodity filter
        
    Returns:
        DataFrame with summary statistics
    """
    if not errors:
        return pd.DataFrame()
    
    # Filter by commodity if specified
    filtered_errors = errors
    if commodity:
        filtered_errors = [e for e in filtered_errors if e.get("commodity") == commodity]
    
    if not filtered_errors:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(filtered_errors)
    
    # Calculate statistics
    if group_by == "none":
        stats = {
            "Count": len(df),
            "Mean Absolute Error": df["absoluteError"].mean() if "absoluteError" in df.columns else None,
            "Median Absolute Error": df["absoluteError"].median() if "absoluteError" in df.columns else None,
            "Std Dev Absolute Error": df["absoluteError"].std() if "absoluteError" in df.columns else None,
            "Min Absolute Error": df["absoluteError"].min() if "absoluteError" in df.columns else None,
            "Max Absolute Error": df["absoluteError"].max() if "absoluteError" in df.columns else None,
            "Mean Percentage Error": df["percentageError"].mean() if "percentageError" in df.columns else None,
            "Median Percentage Error": df["percentageError"].median() if "percentageError" in df.columns else None,
            "Std Dev Percentage Error": df["percentageError"].std() if "percentageError" in df.columns else None,
            "Min Percentage Error": df["percentageError"].min() if "percentageError" in df.columns else None,
            "Max Percentage Error": df["percentageError"].max() if "percentageError" in df.columns else None,
        }
        
        return pd.DataFrame([stats])
    
    elif group_by == "commodity":
        grouped = df.groupby("commodity")
        
        stats_list = []
        for name, group in grouped:
            stats = {
                "Commodity": name,
                "Count": len(group),
                "Mean Absolute Error": group["absoluteError"].mean() if "absoluteError" in group.columns else None,
                "Median Absolute Error": group["absoluteError"].median() if "absoluteError" in group.columns else None,
                "Std Dev Absolute Error": group["absoluteError"].std() if "absoluteError" in group.columns else None,
                "Min Absolute Error": group["absoluteError"].min() if "absoluteError" in group.columns else None,
                "Max Absolute Error": group["absoluteError"].max() if "absoluteError" in group.columns else None,
                "Mean Percentage Error": group["percentageError"].mean() if "percentageError" in group.columns else None,
                "Median Percentage Error": group["percentageError"].median() if "percentageError" in group.columns else None,
                "Std Dev Percentage Error": group["percentageError"].std() if "percentageError" in group.columns else None,
                "Min Percentage Error": group["percentageError"].min() if "percentageError" in group.columns else None,
                "Max Percentage Error": group["percentageError"].max() if "percentageError" in group.columns else None,
            }
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)
    
    elif group_by == "contractMonth":
        grouped = df.groupby("contractMonth")
        
        stats_list = []
        for name, group in grouped:
            stats = {
                "Contract Month": name,
                "Commodity": group["commodity"].iloc[0] if "commodity" in group.columns else None,
                "Count": len(group),
                "Mean Absolute Error": group["absoluteError"].mean() if "absoluteError" in group.columns else None,
                "Median Absolute Error": group["absoluteError"].median() if "absoluteError" in group.columns else None,
                "Std Dev Absolute Error": group["absoluteError"].std() if "absoluteError" in group.columns else None,
                "Min Absolute Error": group["absoluteError"].min() if "absoluteError" in group.columns else None,
                "Max Absolute Error": group["absoluteError"].max() if "absoluteError" in group.columns else None,
                "Mean Percentage Error": group["percentageError"].mean() if "percentageError" in group.columns else None,
                "Median Percentage Error": group["percentageError"].median() if "percentageError" in group.columns else None,
                "Std Dev Percentage Error": group["percentageError"].std() if "percentageError" in group.columns else None,
                "Min Percentage Error": group["percentageError"].min() if "percentageError" in group.columns else None,
                "Max Percentage Error": group["percentageError"].max() if "percentageError" in group.columns else None,
            }
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)
    
    return pd.DataFrame()


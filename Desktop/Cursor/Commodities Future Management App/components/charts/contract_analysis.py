"""
Contract-specific analysis visualizations.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import numpy as np

def create_contract_error_heatmap(
    errors: List[Dict],
    commodity: Optional[str] = None,
    error_type: str = "absolute"  # "absolute" or "percentage"
) -> go.Figure:
    """
    Create heatmap of errors by contract month and date.
    
    Args:
        errors: List of error calculation records
        commodity: Optional commodity filter
        error_type: Type of error to display
        
    Returns:
        Plotly figure
    """
    if not errors:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Filter data
    filtered_errors = errors
    if commodity:
        filtered_errors = [e for e in filtered_errors if e.get("commodity") == commodity]
    
    if not filtered_errors:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Organize data by contract month and date
    contract_months = sorted(set(e.get("contractMonth") for e in filtered_errors))
    dates = sorted(set(e.get("date") for e in filtered_errors))
    
    # Create matrix
    matrix = []
    for contract_month in contract_months:
        row = []
        for date in dates:
            # Find error for this contract and date
            matching_errors = [
                e for e in filtered_errors
                if e.get("contractMonth") == contract_month and e.get("date") == date
            ]
            if matching_errors:
                error_value = matching_errors[0].get(
                    "absoluteError" if error_type == "absolute" else "percentageError"
                )
                row.append(error_value if error_value is not None else 0)
            else:
                row.append(None)
        matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=dates,
        y=contract_months,
        colorscale="RdYlGn_r",  # Red for high error, green for low error
        colorbar=dict(title=f"{error_type.capitalize()} Error"),
        hovertemplate="Contract: %{y}<br>Date: %{x}<br>Error: %{z:.2f}<extra></extra>",
    ))
    
    fig.update_layout(
        title=f"Error Heatmap by Contract Month{' - ' + commodity if commodity else ''}",
        xaxis_title="Date",
        yaxis_title="Contract Month",
        height=600,
    )
    
    return fig

def create_error_by_days_to_expiry(
    errors: List[Dict],
    commodity: Optional[str] = None,
    error_type: str = "absolute"
) -> go.Figure:
    """
    Create scatter plot of error by days to expiry.
    
    Args:
        errors: List of error calculation records
        commodity: Optional commodity filter
        error_type: Type of error to display
        
    Returns:
        Plotly figure
    """
    if not errors:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Filter data
    filtered_errors = errors
    if commodity:
        filtered_errors = [e for e in filtered_errors if e.get("commodity") == commodity]
    
    # Filter out records without days to expiry
    filtered_errors = [e for e in filtered_errors if e.get("daysToExpiry") is not None]
    
    if not filtered_errors:
        fig = go.Figure()
        fig.add_annotation(
            text="No data with days to expiry information",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    days_to_expiry = [e.get("daysToExpiry") for e in filtered_errors]
    error_values = [
        e.get("absoluteError" if error_type == "absolute" else "percentageError")
        for e in filtered_errors
    ]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=days_to_expiry,
            y=error_values,
            mode="markers",
            name="Error",
            marker=dict(
                size=6,
                color=error_values,
                colorscale="RdYlGn_r",
                showscale=True,
                colorbar=dict(title=f"{error_type.capitalize()} Error"),
            ),
            text=[f"Date: {e.get('date')}<br>Contract: {e.get('contractMonth')}" for e in filtered_errors],
            hovertemplate="Days to Expiry: %{x}<br>Error: %{y:.2f}<br>%{text}<extra></extra>",
        )
    )
    
    # Add trend line
    if len(days_to_expiry) > 1:
        z = np.polyfit(days_to_expiry, error_values, 1)
        p = np.poly1d(z)
        trend_x = sorted(days_to_expiry)
        trend_y = p(trend_x)
        
        fig.add_trace(
            go.Scatter(
                x=trend_x,
                y=trend_y,
                mode="lines",
                name="Trend",
                line=dict(color="red", width=2, dash="dash"),
            )
        )
    
    fig.update_layout(
        title=f"Error by Days to Expiry{' - ' + commodity if commodity else ''}",
        xaxis_title="Days to Expiry",
        yaxis_title=f"{error_type.capitalize()} Error",
        height=500,
        showlegend=True,
    )
    
    return fig


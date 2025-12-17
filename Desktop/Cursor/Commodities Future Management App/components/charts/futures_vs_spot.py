"""
Futures vs spot price comparison visualization.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional

def create_futures_vs_spot_chart(
    errors: List[Dict],
    commodity: Optional[str] = None,
    contract_month: Optional[str] = None
) -> go.Figure:
    """
    Create futures vs spot price comparison chart.
    
    Args:
        errors: List of error calculation records
        commodity: Optional commodity filter
        contract_month: Optional contract month filter
        
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
    if contract_month:
        filtered_errors = [e for e in filtered_errors if e.get("contractMonth") == contract_month]
    
    if not filtered_errors:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Sort by date
    filtered_errors.sort(key=lambda x: x.get("date", ""))
    
    dates = [e.get("date") for e in filtered_errors]
    futures_prices = [e.get("futuresPrice") for e in filtered_errors]
    spot_prices = [e.get("spotPrice") for e in filtered_errors]
    absolute_errors = [e.get("absoluteError") for e in filtered_errors]
    
    # Create figure with secondary y-axis for error
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Futures vs Spot Prices", "Absolute Error"),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )
    
    # Futures and spot prices
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=futures_prices,
            mode="lines+markers",
            name="Futures Price",
            line=dict(color="blue", width=2),
            marker=dict(size=4),
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=spot_prices,
            mode="lines+markers",
            name="Spot Price",
            line=dict(color="green", width=2),
            marker=dict(size=4),
        ),
        row=1, col=1
    )
    
    # Error bars
    fig.add_trace(
        go.Bar(
            x=dates,
            y=absolute_errors,
            name="Absolute Error",
            marker_color="red",
            opacity=0.6,
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Absolute Error ($)", row=2, col=1)
    
    fig.update_layout(
        title=f"Futures vs Spot Price Comparison{' - ' + commodity if commodity else ''}",
        height=700,
        hovermode="x unified",
        showlegend=True,
    )
    
    return fig


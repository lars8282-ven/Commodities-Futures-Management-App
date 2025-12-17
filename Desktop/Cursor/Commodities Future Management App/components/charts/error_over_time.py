"""
Error over time visualization component.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
from datetime import datetime

def create_error_over_time_chart(
    errors: List[Dict],
    show_absolute: bool = True,
    show_percentage: bool = True,
    commodity: Optional[str] = None,
    contract_month: Optional[str] = None
) -> go.Figure:
    """
    Create error over time chart.
    
    Args:
        errors: List of error calculation records
        show_absolute: Whether to show absolute error
        show_percentage: Whether to show percentage error
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
    absolute_errors = [e.get("absoluteError") for e in filtered_errors]
    percentage_errors = [e.get("percentageError") for e in filtered_errors]
    
    # Create subplots if showing both
    if show_absolute and show_percentage:
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Absolute Error", "Percentage Error"),
            vertical_spacing=0.1
        )
        
        # Absolute error
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=absolute_errors,
                mode="lines+markers",
                name="Absolute Error",
                line=dict(color="blue", width=2),
                marker=dict(size=4),
            ),
            row=1, col=1
        )
        
        # Percentage error
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=percentage_errors,
                mode="lines+markers",
                name="Percentage Error",
                line=dict(color="red", width=2),
                marker=dict(size=4),
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Absolute Error ($)", row=1, col=1)
        fig.update_yaxes(title_text="Percentage Error (%)", row=2, col=1)
        
    elif show_absolute:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=absolute_errors,
                mode="lines+markers",
                name="Absolute Error",
                line=dict(color="blue", width=2),
                marker=dict(size=4),
            )
        )
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Absolute Error ($)")
        
    else:  # show_percentage
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=percentage_errors,
                mode="lines+markers",
                name="Percentage Error",
                line=dict(color="red", width=2),
                marker=dict(size=4),
            )
        )
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Percentage Error (%)")
    
    fig.update_layout(
        title="Error Over Time",
        height=600 if (show_absolute and show_percentage) else 400,
        hovermode="x unified",
        showlegend=True,
    )
    
    return fig


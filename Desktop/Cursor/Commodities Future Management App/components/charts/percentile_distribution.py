"""
Percentile distribution visualization component.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import numpy as np

def create_percentile_distribution_chart(
    errors: List[Dict],
    error_type: str = "both",  # "absolute", "percentage", or "both"
    commodity: Optional[str] = None
) -> go.Figure:
    """
    Create percentile distribution chart for errors.
    
    Args:
        errors: List of error calculation records
        error_type: Type of error to display
        commodity: Optional commodity filter
        
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
    
    absolute_errors = [e.get("absoluteError") for e in filtered_errors if e.get("absoluteError") is not None]
    percentage_errors = [e.get("percentageError") for e in filtered_errors if e.get("percentageError") is not None]
    
    if error_type in ["absolute", "both"] and not absolute_errors:
        error_type = "percentage" if percentage_errors else None
    
    if error_type in ["percentage", "both"] and not percentage_errors:
        error_type = "absolute" if absolute_errors else None
    
    if not error_type:
        fig = go.Figure()
        fig.add_annotation(
            text="No error data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Create subplots if showing both
    if error_type == "both":
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Absolute Error Distribution", "Percentage Error Distribution"),
            horizontal_spacing=0.1
        )
        
        # Absolute error histogram
        fig.add_trace(
            go.Histogram(
                x=absolute_errors,
                nbinsx=30,
                name="Absolute Error",
                marker_color="blue",
                opacity=0.7,
            ),
            row=1, col=1
        )
        
        # Add percentile lines for absolute error
        abs_percentiles = np.percentile(absolute_errors, [25, 50, 75, 90, 95])
        for p, val in zip([25, 50, 75, 90, 95], abs_percentiles):
            fig.add_vline(
                x=val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"P{p}",
                row=1, col=1
            )
        
        # Percentage error histogram
        fig.add_trace(
            go.Histogram(
                x=percentage_errors,
                nbinsx=30,
                name="Percentage Error",
                marker_color="green",
                opacity=0.7,
            ),
            row=1, col=2
        )
        
        # Add percentile lines for percentage error
        pct_percentiles = np.percentile(percentage_errors, [25, 50, 75, 90, 95])
        for p, val in zip([25, 50, 75, 90, 95], pct_percentiles):
            fig.add_vline(
                x=val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"P{p}",
                row=1, col=2
            )
        
        fig.update_xaxes(title_text="Absolute Error ($)", row=1, col=1)
        fig.update_xaxes(title_text="Percentage Error (%)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        
    elif error_type == "absolute":
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=absolute_errors,
                nbinsx=30,
                name="Absolute Error",
                marker_color="blue",
                opacity=0.7,
            )
        )
        
        # Add percentile lines
        percentiles = np.percentile(absolute_errors, [25, 50, 75, 90, 95])
        for p, val in zip([25, 50, 75, 90, 95], percentiles):
            fig.add_vline(
                x=val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"P{p}: ${val:.2f}",
            )
        
        fig.update_xaxes(title_text="Absolute Error ($)")
        fig.update_yaxes(title_text="Frequency")
        
    else:  # percentage
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=percentage_errors,
                nbinsx=30,
                name="Percentage Error",
                marker_color="green",
                opacity=0.7,
            )
        )
        
        # Add percentile lines
        percentiles = np.percentile(percentage_errors, [25, 50, 75, 90, 95])
        for p, val in zip([25, 50, 75, 90, 95], percentiles):
            fig.add_vline(
                x=val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"P{p}: {val:.2f}%",
            )
        
        fig.update_xaxes(title_text="Percentage Error (%)")
        fig.update_yaxes(title_text="Frequency")
    
    fig.update_layout(
        title="Error Distribution with Percentiles",
        height=500,
        showlegend=False,
    )
    
    return fig


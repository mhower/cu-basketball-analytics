# modules/visualization.py
# Visualization utilities

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class VisualizationEngine:
    """Creates basketball visualizations"""
    
    @staticmethod
    def create_shot_chart(shot_data):
        """Create shot chart visualization"""
        fig = go.Figure()
        
        # Add court outline (simplified)
        fig.add_shape(type="rect",
            x0=0, y0=0, x1=50, y1=47,
            line=dict(color="black", width=2))
        
        return fig
    
    @staticmethod
    def create_performance_radar(metrics_dict):
        """Create radar chart for player performance"""
        categories = list(metrics_dict.keys())
        values = list(metrics_dict.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_timeline(data_points):
        """Create performance timeline"""
        fig = px.line(x=data_points['games'], y=data_points['values'])
        return fig

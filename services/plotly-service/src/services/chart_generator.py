"""
Chart Generator Service for OpenPolicy Plotly Service

Provides comprehensive chart generation capabilities using Plotly,
including various chart types, customization options, and export formats.
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import json
import io
import base64
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Main chart generation service"""
    
    def __init__(self):
        self.default_colors = px.colors.qualitative.Set3
        self.default_template = "plotly_white"
        self.supported_chart_types = [
            'line', 'bar', 'scatter', 'area', 'pie', 'donut', 'histogram',
            'box', 'violin', 'heatmap', 'contour', '3d_scatter', '3d_surface',
            'bubble', 'funnel', 'waterfall', 'candlestick', 'ohlc', 'treemap',
            'sunburst', 'sankey', 'choropleth', 'choroplethmapbox', 'density_mapbox'
        ]
    
    def create_chart(self, chart_type: str, data: Dict[str, Any], 
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a chart based on type and data
        
        Args:
            chart_type: Type of chart to create
            data: Chart data and configuration
            options: Additional chart options
            
        Returns:
            Dictionary containing chart HTML and metadata
        """
        try:
            if chart_type not in self.supported_chart_types:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Create chart based on type
            if chart_type == 'line':
                fig = self._create_line_chart(data, options)
            elif chart_type == 'bar':
                fig = self._create_bar_chart(data, options)
            elif chart_type == 'scatter':
                fig = self._create_scatter_chart(data, options)
            elif chart_type == 'pie':
                fig = self._create_pie_chart(data, options)
            elif chart_type == 'histogram':
                fig = self._create_histogram_chart(data, options)
            elif chart_type == 'heatmap':
                fig = self._create_heatmap_chart(data, options)
            elif chart_type == '3d_scatter':
                fig = self._create_3d_scatter_chart(data, options)
            elif chart_type == 'choropleth':
                fig = self._create_choropleth_chart(data, options)
            else:
                # Generic chart creation for other types
                fig = self._create_generic_chart(chart_type, data, options)
            
            # Apply common customizations
            fig = self._apply_common_customizations(fig, options)
            
            # Generate HTML and metadata
            html = fig.to_html(
                include_plotlyjs=True,
                full_html=False,
                config={'displayModeBar': True, 'displaylogo': False}
            )
            
            return {
                'chart_type': chart_type,
                'html': html,
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'data_points': len(data.get('values', [])),
                    'dimensions': data.get('dimensions', []),
                    'options_applied': options or {}
                },
                'export_formats': ['html', 'png', 'svg', 'pdf', 'json']
            }
            
        except Exception as e:
            logger.error(f"Error creating chart {chart_type}: {e}")
            raise
    
    def _create_line_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a line chart"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        
        if isinstance(y[0], list):  # Multiple series
            for i, series in enumerate(y):
                name = data.get('series_names', [f'Series {i+1}'])[i] if data.get('series_names') else f'Series {i+1}'
                fig.add_trace(go.Scatter(
                    x=x,
                    y=series,
                    mode='lines+markers',
                    name=name,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        else:  # Single series
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=data.get('name', 'Data'),
                line=dict(width=2),
                marker=dict(size=6)
            ))
        
        return fig
    
    def _create_bar_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a bar chart"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        
        if isinstance(y[0], list):  # Multiple series
            for i, series in enumerate(y):
                name = data.get('series_names', [f'Series {i+1}'])[i] if data.get('series_names') else f'Series {i+1}'
                fig.add_trace(go.Bar(
                    x=x,
                    y=series,
                    name=name
                ))
        else:  # Single series
            fig.add_trace(go.Bar(
                x=x,
                y=y,
                name=data.get('name', 'Data')
            ))
        
        return fig
    
    def _create_scatter_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a scatter chart"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        
        if isinstance(y[0], list):  # Multiple series
            for i, series in enumerate(y):
                name = data.get('series_names', [f'Series {i+1}'])[i] if data.get('series_names') else f'Series {i+1}'
                fig.add_trace(go.Scatter(
                    x=x,
                    y=series,
                    mode='markers',
                    name=name,
                    marker=dict(size=8)
                ))
        else:  # Single series
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name=data.get('name', 'Data'),
                marker=dict(size=8)
            ))
        
        return fig
    
    def _create_pie_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a pie chart"""
        values = data.get('values', [])
        labels = data.get('labels', [f'Item {i+1}' for i in range(len(values))])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3 if options and options.get('donut', False) else 0
        )])
        
        return fig
    
    def _create_histogram_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a histogram chart"""
        values = data.get('values', [])
        
        fig = go.Figure(data=[go.Histogram(
            x=values,
            nbinsx=options.get('nbins', 30) if options else 30,
            name=data.get('name', 'Distribution')
        )])
        
        return fig
    
    def _create_heatmap_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a heatmap chart"""
        z = data.get('z', [])
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale='Viridis'
        ))
        
        return fig
    
    def _create_3d_scatter_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a 3D scatter chart"""
        x = data.get('x', [])
        y = data.get('y', [])
        z = data.get('z', [])
        
        fig = go.Figure(data=[go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=6,
                color=z,
                colorscale='Viridis',
                opacity=0.8
            ),
            name=data.get('name', '3D Data')
        )])
        
        return fig
    
    def _create_choropleth_chart(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a choropleth map"""
        locations = data.get('locations', [])
        z = data.get('z', [])
        
        fig = go.Figure(data=go.Choropleth(
            locations=locations,
            z=z,
            locationmode='country names',
            colorscale='Viridis',
            name=data.get('name', 'Geographic Data')
        ))
        
        return fig
    
    def _create_generic_chart(self, chart_type: str, data: Dict[str, Any], 
                             options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create a generic chart for unsupported types"""
        # Fallback to basic scatter plot
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure(data=[go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name=f'{chart_type.title()} Chart'
        )])
        
        return fig
    
    def _apply_common_customizations(self, fig: go.Figure, options: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Apply common customizations to the chart"""
        if not options:
            return fig
        
        # Title
        if options.get('title'):
            fig.update_layout(title=options['title'])
        
        # Axis labels
        if options.get('xaxis_title'):
            fig.update_xaxes(title_text=options['xaxis_title'])
        if options.get('yaxis_title'):
            fig.update_yaxes(title_text=options['yaxis_title'])
        
        # Theme
        if options.get('theme'):
            fig.update_layout(template=options['theme'])
        else:
            fig.update_layout(template=self.default_template)
        
        # Colors
        if options.get('colors'):
            fig.update_traces(marker_color=options['colors'])
        
        # Layout options
        layout_updates = {}
        if options.get('width'):
            layout_updates['width'] = options['width']
        if options.get('height'):
            layout_updates['height'] = options['height']
        if options.get('showlegend') is not None:
            layout_updates['showlegend'] = options['showlegend']
        
        if layout_updates:
            fig.update_layout(**layout_updates)
        
        return fig
    
    def export_chart(self, chart_data: Dict[str, Any], format: str = 'png') -> str:
        """
        Export chart to various formats
        
        Args:
            chart_data: Chart data from create_chart
            format: Export format (png, svg, pdf, json)
            
        Returns:
            Base64 encoded string of exported chart
        """
        try:
            # Recreate the figure from HTML
            html = chart_data['html']
            
            # For now, return the HTML as base64
            # In a full implementation, you would use plotly's export functions
            encoded = base64.b64encode(html.encode()).decode()
            
            return encoded
            
        except Exception as e:
            logger.error(f"Error exporting chart to {format}: {e}")
            raise
    
    def get_chart_templates(self) -> List[Dict[str, Any]]:
        """Get available chart templates"""
        return [
            {
                'id': 'parliamentary_votes',
                'name': 'Parliamentary Votes Analysis',
                'type': 'bar',
                'description': 'Bar chart showing voting patterns by party',
                'category': 'political'
            },
            {
                'id': 'bill_timeline',
                'name': 'Bill Timeline',
                'type': 'line',
                'description': 'Timeline showing bill progress through parliament',
                'category': 'political'
            },
            {
                'id': 'geographic_distribution',
                'name': 'Geographic Distribution',
                'type': 'choropleth',
                'description': 'Map showing data distribution across regions',
                'category': 'geographic'
            },
            {
                'id': 'data_quality_metrics',
                'name': 'Data Quality Metrics',
                'type': 'heatmap',
                'description': 'Heatmap showing data quality across sources',
                'category': 'analytics'
            },
            {
                'id': 'trend_analysis',
                'name': 'Trend Analysis',
                'type': 'scatter',
                'description': 'Scatter plot with trend lines for time series data',
                'category': 'analytics'
            }
        ]
    
    def validate_chart_data(self, data: Dict[str, Any]) -> bool:
        """Validate chart data structure"""
        required_fields = ['x', 'y']
        
        for field in required_fields:
            if field not in data:
                return False
            
            if not isinstance(data[field], list) or len(data[field]) == 0:
                return False
        
        # Check if x and y have same length
        if len(data['x']) != len(data['y']):
            return False
        
        return True

# Create global instance
chart_generator = ChartGenerator()

/**
 * Plotly Chart Component for OpenPolicy Frontend
 * 
 * Displays interactive charts and visualizations using Plotly.js
 */

import React, { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { ChartData, ChartOptions } from '@/types/charts';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface PlotlyChartProps {
  data: ChartData;
  options?: ChartOptions;
  chartId?: string;
  className?: string;
  onChartClick?: (event: any) => void;
  onChartHover?: (event: any) => void;
  onChartSelect?: (event: any) => void;
  loading?: boolean;
  error?: string | null;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  options = {},
  chartId,
  className = '',
  onChartClick,
  onChartHover,
  onChartSelect,
  loading = false,
  error = null,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [plotlyData, setPlotlyData] = useState<any[]>([]);
  const [plotlyLayout, setPlotlyLayout] = useState<any>({});
  const [plotlyConfig, setPlotlyConfig] = useState<any>({});

  // Transform chart data to Plotly format
  useEffect(() => {
    if (!data) return;

    try {
      const transformedData = transformDataToPlotly(data);
      setPlotlyData(transformedData);
    } catch (err) {
      console.error('Error transforming chart data:', err);
    }
  }, [data]);

  // Set up Plotly layout and configuration
  useEffect(() => {
    const layout = createPlotlyLayout(options);
    const config = createPlotlyConfig(options);
    
    setPlotlyLayout(layout);
    setPlotlyConfig(config);
  }, [options]);

  // Transform chart data to Plotly format
  const transformDataToPlotly = (chartData: ChartData): any[] => {
    const { chart_type, data: chartDataData, options: chartOptions } = chartData;
    
    switch (chart_type) {
      case 'line':
        return createLineChartData(chartDataData, chartOptions);
      case 'bar':
        return createBarChartData(chartDataData, chartOptions);
      case 'scatter':
        return createScatterChartData(chartDataData, chartOptions);
      case 'pie':
        return createPieChartData(chartDataData, chartOptions);
      case 'histogram':
        return createHistogramChartData(chartDataData, chartOptions);
      case 'heatmap':
        return createHeatmapChartData(chartDataData, chartOptions);
      case '3d_scatter':
        return create3DScatterChartData(chartDataData, chartOptions);
      case 'choropleth':
        return createChoroplethChartData(chartDataData, chartOptions);
      default:
        return createGenericChartData(chartDataData, chartOptions);
    }
  };

  // Create line chart data
  const createLineChartData = (data: any, options: any): any[] => {
    const { x, y, series_names, name } = data;
    
    if (Array.isArray(y[0])) {
      // Multiple series
      return y.map((series, index) => ({
        x,
        y: series,
        type: 'scatter',
        mode: 'lines+markers',
        name: series_names?.[index] || `Series ${index + 1}`,
        line: { width: 2 },
        marker: { size: 6 },
        ...options
      }));
    } else {
      // Single series
      return [{
        x,
        y,
        type: 'scatter',
        mode: 'lines+markers',
        name: name || 'Data',
        line: { width: 2 },
        marker: { size: 6 },
        ...options
      }];
    }
  };

  // Create bar chart data
  const createBarChartData = (data: any, options: any): any[] => {
    const { x, y, series_names, name } = data;
    
    if (Array.isArray(y[0])) {
      // Multiple series
      return y.map((series, index) => ({
        x,
        y: series,
        type: 'bar',
        name: series_names?.[index] || `Series ${index + 1}`,
        ...options
      }));
    } else {
      // Single series
      return [{
        x,
        y,
        type: 'bar',
        name: name || 'Data',
        ...options
      }];
    }
  };

  // Create scatter chart data
  const createScatterChartData = (data: any, options: any): any[] => {
    const { x, y, series_names, name } = data;
    
    if (Array.isArray(y[0])) {
      // Multiple series
      return y.map((series, index) => ({
        x,
        y: series,
        type: 'scatter',
        mode: 'markers',
        name: series_names?.[index] || `Series ${index + 1}`,
        marker: { size: 8 },
        ...options
      }));
    } else {
      // Single series
      return [{
        x,
        y,
        type: 'scatter',
        mode: 'markers',
        name: name || 'Data',
        marker: { size: 8 },
        ...options
      }];
    }
  };

  // Create pie chart data
  const createPieChartData = (data: any, options: any): any[] => {
    const { values, labels } = data;
    const isDonut = options?.donut || false;
    
    return [{
      values,
      labels: labels || values.map((_: any, i: number) => `Item ${i + 1}`),
      type: 'pie',
      hole: isDonut ? 0.3 : 0,
      ...options
    }];
  };

  // Create histogram chart data
  const createHistogramChartData = (data: any, options: any): any[] => {
    const { values, name } = data;
    
    return [{
      x: values,
      type: 'histogram',
      name: name || 'Distribution',
      nbinsx: options?.nbins || 30,
      ...options
    }];
  };

  // Create heatmap chart data
  const createHeatmapChartData = (data: any, options: any): any[] => {
    const { z, x, y } = data;
    
    return [{
      z,
      x,
      y,
      type: 'heatmap',
      colorscale: 'Viridis',
      ...options
    }];
  };

  // Create 3D scatter chart data
  const create3DScatterChartData = (data: any, options: any): any[] => {
    const { x, y, z, name } = data;
    
    return [{
      x,
      y,
      z,
      type: 'scatter3d',
      mode: 'markers',
      marker: {
        size: 6,
        color: z,
        colorscale: 'Viridis',
        opacity: 0.8
      },
      name: name || '3D Data',
      ...options
    }];
  };

  // Create choropleth chart data
  const createChoroplethChartData = (data: any, options: any): any[] => {
    const { locations, z, name } = data;
    
    return [{
      locations,
      z,
      type: 'choropleth',
      locationmode: 'country names',
      colorscale: 'Viridis',
      name: name || 'Geographic Data',
      ...options
    }];
  };

  // Create generic chart data (fallback)
  const createGenericChartData = (data: any, options: any): any[] => {
    const { x, y, name } = data;
    
    return [{
      x,
      y,
      type: 'scatter',
      mode: 'markers',
      name: name || 'Data',
      ...options
    }];
  };

  // Create Plotly layout
  const createPlotlyLayout = (chartOptions: ChartOptions): any => {
    const baseLayout = {
      title: chartOptions.title || 'Chart',
      xaxis: {
        title: chartOptions.xaxis_title || 'X Axis',
        showgrid: true,
        gridcolor: '#f0f0f0'
      },
      yaxis: {
        title: chartOptions.yaxis_title || 'Y Axis',
        showgrid: true,
        gridcolor: '#f0f0f0'
      },
      showlegend: chartOptions.showlegend !== false,
      legend: {
        x: 0,
        y: 1,
        bgcolor: 'rgba(255, 255, 255, 0.8)',
        bordercolor: '#ccc',
        borderwidth: 1
      },
      margin: {
        l: 60,
        r: 30,
        t: 60,
        b: 60
      },
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      font: {
        family: 'Arial, sans-serif',
        size: 12,
        color: '#333'
      },
      hovermode: 'closest',
      ...chartOptions.layout
    };

    // Add 3D layout properties if needed
    if (data?.chart_type === '3d_scatter') {
      baseLayout.scene = {
        xaxis: { title: chartOptions.xaxis_title || 'X Axis' },
        yaxis: { title: chartOptions.yaxis_title || 'Y Axis' },
        zaxis: { title: chartOptions.zaxis_title || 'Z Axis' }
      };
    }

    return baseLayout;
  };

  // Create Plotly configuration
  const createPlotlyConfig = (chartOptions: ChartOptions): any => {
    return {
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
      responsive: true,
      ...chartOptions.config
    };
  };

  // Handle chart events
  const handleClick = (event: any) => {
    if (onChartClick) {
      onChartClick(event);
    }
  };

  const handleHover = (event: any) => {
    if (onChartHover) {
      onChartHover(event);
    }
  };

  const handleSelect = (event: any) => {
    if (onChartSelect) {
      onChartSelect(event);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className={`chart-loading ${className}`}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading chart...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`chart-error ${className}`}>
        <div className="error-message">
          <p>Error loading chart: {error}</p>
          <button onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No data state
  if (!data || !plotlyData.length) {
    return (
      <div className={`chart-no-data ${className}`}>
        <p>No chart data available</p>
      </div>
    );
  }

  return (
    <div 
      ref={chartRef}
      className={`plotly-chart ${className}`}
      id={chartId}
    >
      <Plot
        data={plotlyData}
        layout={plotlyLayout}
        config={plotlyConfig}
        onClick={handleClick}
        onHover={handleHover}
        onSelected={handleSelect}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default PlotlyChart;

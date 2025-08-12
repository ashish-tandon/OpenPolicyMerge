/**
 * Chart Types and Interfaces for OpenPolicy Frontend
 * 
 * Defines the structure for chart data, options, and configuration
 */

export interface ChartData {
  chart_type: ChartType;
  data: ChartDataContent;
  options?: ChartOptions;
  metadata?: ChartMetadata;
}

export interface ChartDataContent {
  x?: any[];
  y?: any[];
  z?: any[];
  values?: number[];
  labels?: string[];
  series_names?: string[];
  name?: string;
  locations?: string[];
}

export interface ChartOptions {
  title?: string;
  xaxis_title?: string;
  yaxis_title?: string;
  zaxis_title?: string;
  theme?: string;
  colors?: string[];
  width?: number;
  height?: number;
  showlegend?: boolean;
  donut?: boolean;
  nbins?: number;
  layout?: any;
  config?: any;
}

export interface ChartMetadata {
  created_at: string;
  data_points: number;
  dimensions: string[];
  options_applied: any;
}

export type ChartType = 
  | 'line'
  | 'bar'
  | 'scatter'
  | 'area'
  | 'pie'
  | 'donut'
  | 'histogram'
  | 'box'
  | 'violin'
  | 'heatmap'
  | 'contour'
  | '3d_scatter'
  | '3d_surface'
  | 'bubble'
  | 'funnel'
  | 'waterfall'
  | 'candlestick'
  | 'ohlc'
  | 'treemap'
  | 'sunburst'
  | 'sankey'
  | 'choropleth'
  | 'choroplethmapbox'
  | 'density_mapbox';

export interface ChartTemplate {
  id: string;
  name: string;
  type: ChartType;
  description: string;
  category: ChartCategory;
  defaultOptions?: ChartOptions;
  sampleData?: ChartDataContent;
}

export type ChartCategory = 
  | 'political'
  | 'geographic'
  | 'analytics'
  | 'financial'
  | 'statistical'
  | 'custom';

export interface ChartExportOptions {
  format: 'png' | 'svg' | 'pdf' | 'html' | 'json';
  width?: number;
  height?: number;
  scale?: number;
  filename?: string;
}

export interface ChartInteractionEvent {
  type: 'click' | 'hover' | 'select' | 'zoom' | 'pan';
  data: any;
  point?: any;
  curveNumber?: number;
  pointNumber?: number;
  x?: any;
  y?: any;
  z?: any;
}

export interface ChartPerformanceMetrics {
  renderTime: number;
  dataSize: number;
  updateTime: number;
  memoryUsage?: number;
}

export interface ChartAccessibility {
  altText?: string;
  ariaLabel?: string;
  keyboardNavigation?: boolean;
  screenReaderSupport?: boolean;
}

export interface ChartResponsiveConfig {
  breakpoints: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
  layouts: {
    [key: string]: any;
  };
}

export interface ChartTheme {
  name: string;
  colors: {
    primary: string[];
    secondary: string[];
    accent: string[];
    background: string;
    text: string;
    grid: string;
  };
  fonts: {
    family: string;
    sizes: {
      title: number;
      axis: number;
      legend: number;
      tick: number;
    };
  };
  spacing: {
    margin: number;
    padding: number;
    gap: number;
  };
}

export interface ChartAnimation {
  enabled: boolean;
  duration: number;
  easing: 'linear' | 'easeIn' | 'easeOut' | 'easeInOut';
  delay?: number;
}

export interface ChartTooltip {
  enabled: boolean;
  mode: 'closest' | 'x' | 'y' | 'xy';
  formatter?: (data: any) => string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  backgroundColor?: string;
  borderColor?: string;
  textColor?: string;
}

export interface ChartLegend {
  enabled: boolean;
  position: 'top' | 'bottom' | 'left' | 'right';
  orientation: 'horizontal' | 'vertical';
  backgroundColor?: string;
  borderColor?: string;
  borderWidth?: number;
  fontColor?: string;
  fontSize?: number;
}

export interface ChartAxis {
  title: string;
  type: 'linear' | 'log' | 'date' | 'category';
  range?: [number, number];
  tickMode?: 'auto' | 'linear' | 'array';
  tickValues?: any[];
  tickFormat?: string;
  gridColor?: string;
  gridWidth?: number;
  showGrid?: boolean;
  zeroline?: boolean;
  zerolineColor?: string;
  zerolineWidth?: number;
}

export interface ChartGrid {
  enabled: boolean;
  color: string;
  width: number;
  style: 'solid' | 'dashed' | 'dotted';
  alpha: number;
}

export interface ChartWatermark {
  enabled: boolean;
  text: string;
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
  fontSize: number;
  fontColor: string;
  alpha: number;
  rotation?: number;
}

export interface ChartExportResult {
  success: boolean;
  data?: string | Blob;
  filename?: string;
  format: string;
  size?: number;
  error?: string;
}

export interface ChartUpdateOptions {
  animate?: boolean;
  transition?: {
    duration: number;
    easing: string;
  };
  redraw?: boolean;
  relayout?: boolean;
}

export interface ChartResizeOptions {
  width?: number;
  height?: number;
  maintainAspectRatio?: boolean;
  responsive?: boolean;
}

export interface ChartPrintOptions {
  format: 'A4' | 'Letter' | 'Legal';
  orientation: 'portrait' | 'landscape';
  margin: number;
  scale: number;
  includeBackground?: boolean;
}

export interface ChartShareOptions {
  platforms: ('email' | 'social' | 'link' | 'embed')[];
  title?: string;
  description?: string;
  image?: string;
  url?: string;
}

export interface ChartAnalytics {
  viewCount: number;
  interactionCount: number;
  shareCount: number;
  exportCount: number;
  averageViewTime: number;
  lastViewed: string;
  createdBy: string;
  tags: string[];
}

export interface ChartValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}

export interface ChartAccessControl {
  public: boolean;
  allowedUsers: string[];
  allowedRoles: string[];
  permissions: {
    view: boolean;
    edit: boolean;
    delete: boolean;
    share: boolean;
    export: boolean;
  };
}

export interface ChartVersion {
  version: string;
  changes: string[];
  createdBy: string;
  createdAt: string;
  isCurrent: boolean;
}

export interface ChartCollaboration {
  collaborators: string[];
  comments: ChartComment[];
  suggestions: ChartSuggestion[];
  approvalStatus: 'pending' | 'approved' | 'rejected';
  approvedBy?: string;
  approvedAt?: string;
}

export interface ChartComment {
  id: string;
  author: string;
  text: string;
  timestamp: string;
  replies?: ChartComment[];
}

export interface ChartSuggestion {
  id: string;
  author: string;
  type: 'layout' | 'data' | 'style' | 'interaction';
  description: string;
  status: 'open' | 'in-progress' | 'implemented' | 'rejected';
  timestamp: string;
}

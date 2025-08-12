/**
 * Dashboard Page for OpenPolicy Frontend
 * 
 * Displays comprehensive overview with charts, metrics, and service status
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ChartBarIcon, 
  GlobeAltIcon, 
  DocumentTextIcon, 
  UserGroupIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { apiGateway } from '@/lib/api/gateway';
import PlotlyChart from '@/components/charts/PlotlyChart';
import { ChartData, ChartOptions, ServiceStatus } from '@/types/charts';

interface DashboardMetrics {
  totalBills: number;
  totalMembers: number;
  totalCommittees: number;
  activeETLJobs: number;
  dataQualityScore: number;
  lastUpdate: string;
}

interface ServiceHealth {
  name: string;
  status: string;
  responseTime: number | null;
  lastSeen: string | null;
}

const Dashboard: React.FC = () => {
  const [selectedChartType, setSelectedChartType] = useState<string>('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('7d');

  // Fetch dashboard metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async (): Promise<DashboardMetrics> => {
      const [bills, members, committees, etlJobs, qualityMetrics] = await Promise.all([
        apiGateway.getBills({ limit: 1 }),
        apiGateway.getMembers({ limit: 1 }),
        apiGateway.getCommittees({ limit: 1 }),
        apiGateway.getETLJobs({ status: 'running' }),
        apiGateway.getDataQualityMetrics()
      ]);

      return {
        totalBills: bills.total || 0,
        totalMembers: members.total || 0,
        totalCommittees: committees.total || 0,
        activeETLJobs: etlJobs.length || 0,
        dataQualityScore: qualityMetrics.average_score || 0,
        lastUpdate: new Date().toISOString()
      };
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch service health status
  const { data: serviceHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['service-health'],
    queryFn: apiGateway.getAllServiceStatuses,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch charts
  const { data: charts, isLoading: chartsLoading } = useQuery({
    queryKey: ['dashboard-charts', selectedChartType, selectedTimeRange],
    queryFn: () => apiGateway.getCharts({ 
      chart_type: selectedChartType === 'all' ? undefined : selectedChartType,
      limit: 6 
    }),
  });

  // Sample chart data for demonstration
  const sampleCharts: ChartData[] = [
    {
      chart_type: 'bar',
      data: {
        x: ['Conservative', 'Liberal', 'NDP', 'Bloc', 'Green'],
        y: [119, 157, 25, 32, 2],
        name: 'Parliamentary Seats by Party'
      },
      options: {
        title: '2021 Canadian Federal Election Results',
        xaxis_title: 'Political Party',
        yaxis_title: 'Number of Seats',
        theme: 'plotly_white'
      },
      metadata: {
        created_at: new Date().toISOString(),
        data_points: 5,
        dimensions: ['party', 'seats'],
        options_applied: {}
      }
    },
    {
      chart_type: 'line',
      data: {
        x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        y: [12, 19, 15, 25, 22, 30],
        name: 'Bills Introduced by Month'
      },
      options: {
        title: 'Legislative Activity Trends',
        xaxis_title: 'Month',
        yaxis_title: 'Number of Bills',
        theme: 'plotly_white'
      },
      metadata: {
        created_at: new Date().toISOString(),
        data_points: 6,
        dimensions: ['month', 'bills'],
        options_applied: {}
      }
    },
    {
      chart_type: 'pie',
      data: {
        values: [45, 30, 15, 10],
        labels: ['Passed', 'In Progress', 'Under Review', 'Rejected'],
        name: 'Bill Status Distribution'
      },
      options: {
        title: 'Current Bill Status',
        theme: 'plotly_white'
      },
      metadata: {
        created_at: new Date().toISOString(),
        data_points: 4,
        dimensions: ['status', 'count'],
        options_applied: {}
      }
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'unhealthy':
      case 'down':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
      case 'down':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (metricsLoading || healthLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">OpenPolicy Dashboard</h1>
            <p className="mt-2 text-gray-600">
              Comprehensive overview of parliamentary data, civic information, and system health
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Bills</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics?.totalBills.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Members</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics?.totalMembers.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CogIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active ETL Jobs</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics?.activeETLJobs || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Data Quality Score</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics?.dataQualityScore ? `${Math.round(metrics.dataQualityScore * 100)}%` : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Service Health */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Service Health</h3>
                <p className="text-sm text-gray-500">Real-time status of all services</p>
              </div>
              <div className="p-6">
                {serviceHealth?.map((service) => (
                  <div key={service.name} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-center">
                      {getStatusIcon(service.status)}
                      <span className="ml-3 text-sm font-medium text-gray-900">
                        {service.name.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(service.status)}`}>
                      {service.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Data Visualizations</h3>
                    <p className="text-sm text-gray-500">Interactive charts and analytics</p>
                  </div>
                  <div className="flex space-x-2">
                    <select
                      value={selectedChartType}
                      onChange={(e) => setSelectedChartType(e.target.value)}
                      className="text-sm border border-gray-300 rounded-md px-3 py-1"
                    >
                      <option value="all">All Types</option>
                      <option value="bar">Bar Charts</option>
                      <option value="line">Line Charts</option>
                      <option value="pie">Pie Charts</option>
                      <option value="scatter">Scatter Plots</option>
                    </select>
                    <select
                      value={selectedTimeRange}
                      onChange={(e) => setSelectedTimeRange(e.target.value)}
                      className="text-sm border border-gray-300 rounded-md px-3 py-1"
                    >
                      <option value="7d">Last 7 Days</option>
                      <option value="30d">Last 30 Days</option>
                      <option value="90d">Last 90 Days</option>
                      <option value="1y">Last Year</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="p-6">
                {chartsLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Loading charts...</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {sampleCharts.map((chart, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="h-64">
                          <PlotlyChart
                            data={chart}
                            options={chart.options}
                            chartId={`chart-${index}`}
                            className="w-full h-full"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
              <p className="text-sm text-gray-500">Latest updates and changes</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      New bill C-123 introduced by Member Smith
                    </p>
                    <p className="text-sm text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-blue-400 rounded-full"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      ETL job completed successfully - 1,234 records processed
                    </p>
                    <p className="text-sm text-gray-500">4 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-yellow-400 rounded-full"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      Data quality metrics updated for parliamentary sources
                    </p>
                    <p className="text-sm text-gray-500">6 hours ago</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Last Update */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Last updated: {metrics?.lastUpdate ? new Date(metrics.lastUpdate).toLocaleString() : 'Never'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

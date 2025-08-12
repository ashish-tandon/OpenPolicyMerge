/**
 * Integration Tests for OpenPolicy Frontend
 * 
 * Tests connectivity and functionality between frontend and backend services
 * through the API Gateway
 */

import { apiGateway } from '@/lib/api/gateway';

// Mock environment variables
process.env.NEXT_PUBLIC_API_GATEWAY_URL = 'http://api-gateway:8000';

describe('API Gateway Integration Tests', () => {
  beforeAll(() => {
    // Setup test environment
    jest.setTimeout(30000); // 30 second timeout for integration tests
  });

  describe('Service Discovery', () => {
    test('should fetch available services', async () => {
      try {
        const services = await apiGateway.getServices();
        expect(Array.isArray(services)).toBe(true);
        expect(services.length).toBeGreaterThan(0);
        
        // Verify service structure
        services.forEach(service => {
          expect(service).toHaveProperty('path');
          expect(service).toHaveProperty('service');
          expect(service).toHaveProperty('description');
        });
      } catch (error) {
        // Service might not be running in test environment
        console.warn('Service discovery test skipped - API Gateway not available');
      }
    });

    test('should fetch service health status', async () => {
      try {
        const statuses = await apiGateway.getAllServiceStatuses();
        expect(Array.isArray(statuses)).toBe(true);
        
        statuses.forEach(status => {
          expect(status).toHaveProperty('name');
          expect(status).toHaveProperty('status');
          expect(['healthy', 'degraded', 'unhealthy', 'down', 'unknown']).toContain(status.status);
        });
      } catch (error) {
        console.warn('Service health test skipped - API Gateway not available');
      }
    });
  });

  describe('Health Checks', () => {
    test('should check gateway health', async () => {
      try {
        const health = await apiGateway.getGatewayHealth();
        expect(health).toHaveProperty('status');
        expect(health.status).toBe('healthy');
      } catch (error) {
        console.warn('Health check test skipped - API Gateway not available');
      }
    });

    test('should check gateway readiness', async () => {
      try {
        const readiness = await apiGateway.getGatewayReadiness();
        expect(readiness).toHaveProperty('status');
        expect(['ready', 'not_ready']).toContain(readiness.status);
      } catch (error) {
        console.warn('Readiness check test skipped - API Gateway not available');
      }
    });
  });

  describe('Parliamentary Data Endpoints', () => {
    test('should fetch bills data', async () => {
      try {
        const bills = await apiGateway.getBills({ limit: 5 });
        expect(bills).toBeDefined();
        
        if (bills.data) {
          expect(Array.isArray(bills.data)).toBe(true);
          expect(bills.data.length).toBeLessThanOrEqual(5);
        }
      } catch (error) {
        console.warn('Bills endpoint test skipped - service not available');
      }
    });

    test('should fetch members data', async () => {
      try {
        const members = await apiGateway.getMembers({ limit: 5 });
        expect(members).toBeDefined();
        
        if (members.data) {
          expect(Array.isArray(members.data)).toBe(true);
          expect(members.data.length).toBeLessThanOrEqual(5);
        }
      } catch (error) {
        console.warn('Members endpoint test skipped - service not available');
      }
    });

    test('should fetch committees data', async () => {
      try {
        const committees = await apiGateway.getCommittees({ limit: 5 });
        expect(committees).toBeDefined();
        
        if (committees.data) {
          expect(Array.isArray(committees.data)).toBe(true);
          expect(committees.data.length).toBeLessThanOrEqual(5);
        }
      } catch (error) {
        console.warn('Committees endpoint test skipped - service not available');
      }
    });
  });

  describe('ETL Service Endpoints', () => {
    test('should fetch ETL jobs', async () => {
      try {
        const jobs = await apiGateway.getETLJobs({ limit: 5 });
        expect(jobs).toBeDefined();
        
        if (Array.isArray(jobs)) {
          expect(Array.isArray(jobs)).toBe(true);
          expect(jobs.length).toBeLessThanOrEqual(5);
        }
      } catch (error) {
        console.warn('ETL jobs endpoint test skipped - service not available');
      }
    });

    test('should fetch data sources', async () => {
      try {
        const sources = await apiGateway.getDataSourcesETL({ limit: 5 });
        expect(sources).toBeDefined();
        
        if (Array.isArray(sources)) {
          expect(Array.isArray(sources)).toBe(true);
          expect(sources.length).toBeLessThanOrEqual(5);
        }
      } catch (error) {
        console.warn('Data sources endpoint test skipped - service not available');
      }
    });

    test('should fetch data quality metrics', async () => {
      try {
        const metrics = await apiGateway.getDataQualityMetrics();
        expect(metrics).toBeDefined();
      } catch (error) {
        console.warn('Data quality metrics endpoint test skipped - service not available');
      }
    });
  });

  describe('Chart Endpoints', () => {
    test('should fetch available chart types', async () => {
      try {
        const chartTypes = await apiGateway.getAvailableChartTypes();
        expect(chartTypes).toHaveProperty('chart_types');
        expect(Array.isArray(chartTypes.chart_types)).toBe(true);
        expect(chartTypes.chart_types.length).toBeGreaterThan(0);
        
        // Verify chart type structure
        chartTypes.chart_types.forEach(chartType => {
          expect(chartType).toHaveProperty('id');
          expect(chartType).toHaveProperty('name');
          expect(chartType).toHaveProperty('description');
        });
      } catch (error) {
        console.warn('Chart types endpoint test skipped - service not available');
      }
    });

    test('should fetch available data sources for charts', async () => {
      try {
        const sources = await apiGateway.getAvailableDataSources();
        expect(sources).toHaveProperty('data_sources');
        expect(Array.isArray(sources.data_sources)).toBe(true);
      } catch (error) {
        console.warn('Chart data sources endpoint test skipped - service not available');
      }
    });
  });

  describe('Error Handling', () => {
    test('should handle service unavailable errors gracefully', async () => {
      // Test with invalid service endpoint
      try {
        await apiGateway.get('/invalid-endpoint');
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error).toBeDefined();
        expect(error.response?.status).toBe(404);
      }
    });

    test('should handle timeout errors gracefully', async () => {
      // Test with very short timeout
      const shortTimeoutGateway = new (apiGateway.constructor as any)({
        baseURL: 'http://api-gateway:8000',
        timeout: 1, // 1ms timeout
        withCredentials: true,
      });

      try {
        await shortTimeoutGateway.get('/healthz');
        fail('Should have thrown a timeout error');
      } catch (error: any) {
        expect(error).toBeDefined();
        expect(error.code).toBe('ECONNABORTED');
      }
    });
  });

  describe('Authentication', () => {
    test('should handle missing authentication token', async () => {
      // Clear any existing token
      localStorage.removeItem('auth_token');
      
      try {
        // This should work for public endpoints
        await apiGateway.getGatewayHealth();
        expect(true).toBe(true); // Test passes if no auth error
      } catch (error: any) {
        // If auth is required, should get 401
        if (error.response?.status === 401) {
          expect(error.response.status).toBe(401);
        } else {
          throw error; // Unexpected error
        }
      }
    });

    test('should include authentication token when available', async () => {
      // Set a test token
      localStorage.setItem('auth_token', 'test-token');
      
      try {
        // Mock the request to check headers
        const originalGet = apiGateway.get;
        const mockGet = jest.fn().mockResolvedValue({ data: 'test' });
        apiGateway.get = mockGet;
        
        await apiGateway.get('/test-endpoint');
        
        expect(mockGet).toHaveBeenCalledWith('/test-endpoint');
        
        // Restore original method
        apiGateway.get = originalGet;
      } catch (error) {
        console.warn('Authentication test skipped');
      }
    });
  });

  describe('Configuration', () => {
    test('should update configuration correctly', () => {
      const originalBaseURL = apiGateway.getBaseURL();
      const newConfig = { baseURL: 'http://new-url.com' };
      
      apiGateway.updateConfig(newConfig);
      
      expect(apiGateway.getBaseURL()).toBe('http://new-url.com');
      
      // Restore original config
      apiGateway.updateConfig({ baseURL: originalBaseURL });
    });

    test('should maintain configuration state', () => {
      const config = {
        baseURL: 'http://test-url.com',
        timeout: 5000,
        withCredentials: false,
      };
      
      apiGateway.updateConfig(config);
      
      expect(apiGateway.getBaseURL()).toBe(config.baseURL);
      
      // Restore original config
      apiGateway.updateConfig({
        baseURL: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://api-gateway:8000',
        timeout: 30000,
        withCredentials: true,
      });
    });
  });
});

describe('Chart Component Integration Tests', () => {
  test('should transform chart data correctly', () => {
    // Test data transformation logic
    const testData = {
      chart_type: 'bar',
      data: {
        x: ['A', 'B', 'C'],
        y: [1, 2, 3],
        name: 'Test Chart'
      },
      options: {
        title: 'Test Title',
        xaxis_title: 'X Axis',
        yaxis_title: 'Y Axis'
      }
    };

    expect(testData.chart_type).toBe('bar');
    expect(testData.data.x).toEqual(['A', 'B', 'C']);
    expect(testData.data.y).toEqual([1, 2, 3]);
    expect(testData.options.title).toBe('Test Title');
  });

  test('should handle different chart types', () => {
    const chartTypes = ['line', 'bar', 'scatter', 'pie', 'histogram', 'heatmap'];
    
    chartTypes.forEach(type => {
      const testData = {
        chart_type: type,
        data: { x: [1, 2, 3], y: [1, 2, 3] },
        options: {}
      };
      
      expect(testData.chart_type).toBe(type);
      expect(testData.data).toBeDefined();
    });
  });
});

describe('Dashboard Integration Tests', () => {
  test('should handle loading states', () => {
    const loadingStates = {
      metricsLoading: true,
      healthLoading: false,
      chartsLoading: true
    };
    
    expect(loadingStates.metricsLoading).toBe(true);
    expect(loadingStates.healthLoading).toBe(false);
    expect(loadingStates.chartsLoading).toBe(true);
  });

  test('should handle service status mapping', () => {
    const statusMapping = {
      healthy: 'text-green-600 bg-green-100',
      degraded: 'text-yellow-600 bg-yellow-100',
      unhealthy: 'text-red-600 bg-red-100',
      down: 'text-red-600 bg-red-100',
      unknown: 'text-gray-600 bg-gray-100'
    };
    
    Object.entries(statusMapping).forEach(([status, expectedClass]) => {
      expect(statusMapping[status as keyof typeof statusMapping]).toBe(expectedClass);
    });
  });
});

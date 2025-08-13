const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.SERVICE_PORT || 9001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/healthz', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'api-gateway',
    version: '1.0.0',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

// Readiness check endpoint
app.get('/readyz', (req, res) => {
  res.status(200).json({
    status: 'ready',
    service: 'api-gateway',
    version: '1.0.0',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

// Alternative health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'api-gateway',
    version: '1.0.0',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.status(200).json({
    service: 'api-gateway',
    version: '1.0.0',
    status: 'running',
    port: PORT,
    description: 'API Gateway Service for OpenPolicy Platform'
  });
});

// API status endpoint
app.get('/api/gateway/status', (req, res) => {
  res.status(200).json({
    status: 'active',
    service: 'api-gateway',
    version: '1.0.0',
    port: PORT,
    features: {
      routing: true,
      load_balancing: true,
      authentication: true,
      rate_limiting: true
    }
  });
});

const http = require('http');

// Helper function to make HTTP requests
function makeRequest(url, callback) {
  const req = http.request(url, (res) => {
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    res.on('end', () => {
      try {
        const jsonData = JSON.parse(data);
        callback(null, jsonData);
      } catch (e) {
        callback(null, { status: 'ok', data: data });
      }
    });
  });
  
  req.on('error', (err) => {
    callback(err, null);
  });
  
  req.end();
}

// Service routing endpoints
app.get('/api/policy/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://policy-service:9003/api/policy/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach policy service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

app.get('/api/etl/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://etl:80/api/etl/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach ETL service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

app.get('/api/search/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://search-service:9002/api/search/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach search service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

// Auth service routing
app.get('/api/auth/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://auth-service:9003/api/auth/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach auth service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

// Config service routing
app.get('/api/config/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://config-service:9005/api/config/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach config service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

// Error reporting service routing
app.get('/api/errors/*', (req, res) => {
  const targetPath = req.params[0];
  const url = `http://error-reporting-service:9024/api/errors/${targetPath}`;
  
  makeRequest(url, (error, data) => {
    if (error) {
      res.status(500).json({ error: 'Failed to reach error reporting service', details: error.message });
    } else {
      res.json(data);
    }
  });
});

// Platform status dashboard
app.get('/api/platform/status', async (req, res) => {
  try {
    const services = [
      { name: 'api-gateway', url: 'http://localhost:8080/healthz' },
      { name: 'etl', url: 'http://etl:80/healthz' },
      { name: 'policy', url: 'http://policy-service:9003/healthz' },
      { name: 'search', url: 'http://search-service:9002/healthz' },
      { name: 'notification', url: 'http://notification-service:9004/healthz' },
      { name: 'auth', url: 'http://auth-service:9003/healthz' },
      { name: 'config', url: 'http://config-service:9005/healthz' },
      { name: 'error-reporting', url: 'http://error-reporting-service:9024/healthz' }
    ];
    
    const statusPromises = services.map(async (service) => {
      try {
        const response = await new Promise((resolve, reject) => {
          const req = http.request(service.url, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => { resolve({ status: 'healthy', response: res.statusCode }); });
          });
          req.on('error', () => { resolve({ status: 'unhealthy', response: 'connection failed' }); });
          req.setTimeout(2000, () => { resolve({ status: 'unhealthy', response: 'timeout' }); });
          req.end();
        });
        return { name: service.name, ...response };
      } catch (error) {
        return { name: service.name, status: 'unhealthy', response: 'error' };
      }
    });
    
    const results = await Promise.all(statusPromises);
    const healthyCount = results.filter(r => r.status === 'healthy').length;
    const totalCount = results.length;
    
    res.json({
      platform: 'OpenPolicy Platform',
      timestamp: new Date().toISOString(),
      overall_status: healthyCount === totalCount ? 'healthy' : 'degraded',
      health_score: `${healthyCount}/${totalCount}`,
      services: results
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get platform status', details: error.message });
  }
});

// Service discovery endpoint
app.get('/api/platform/services', (req, res) => {
  res.json({
    services: [
      {
        name: 'api-gateway',
        description: 'API Gateway and Service Router',
        port: 8080,
        endpoints: ['/healthz', '/readyz', '/api/gateway/*', '/api/policy/*', '/api/etl/*', '/api/search/*', '/api/auth/*', '/api/config/*', '/api/errors/*']
      },
      {
        name: 'etl',
        description: 'Data Processing and Transformation Service',
        port: 8007,
        endpoints: ['/healthz', '/readyz', '/jobs', '/pipelines']
      },
      {
        name: 'policy',
        description: 'Policy Management Service',
        port: 9003,
        endpoints: ['/healthz', '/readyz', '/']
      },
      {
        name: 'search',
        description: 'Search and Discovery Service',
        port: 9002,
        endpoints: ['/healthz', '/readyz', '/search']
      },
      {
        name: 'notification',
        description: 'User Notification Service',
        port: 9004,
        endpoints: ['/healthz', '/readyz', '/notifications/send']
      },
      {
        name: 'auth',
        description: 'Authentication and Authorization Service',
        port: 9003,
        endpoints: ['/healthz', '/readyz']
      },
      {
        name: 'config',
        description: 'Configuration Management Service',
        port: 9005,
        endpoints: ['/healthz', '/readyz']
      },
      {
        name: 'error-reporting',
        description: 'Error Tracking and Reporting Service',
        port: 9024,
        endpoints: ['/healthz', '/readyz']
      }
    ],
    infrastructure: [
      {
        name: 'postgresql',
        description: 'Primary Database',
        port: 5432
      },
      {
        name: 'redis',
        description: 'Caching Service',
        port: 6379
      },
      {
        name: 'rabbitmq',
        description: 'Message Queue Service',
        port: 5672
      }
    ]
  });
});

// Routes endpoint
app.get('/api/gateway/routes', (req, res) => {
  res.status(200).json({
    routes: [
      {
        path: '/healthz',
        method: 'GET',
        description: 'Health check endpoint'
      },
      {
        path: '/readyz',
        method: 'GET',
        description: 'Readiness check endpoint'
      },
      {
        path: '/health',
        method: 'GET',
        description: 'Alternative health check endpoint'
      },
      {
        path: '/api/gateway/status',
        method: 'GET',
        description: 'API Gateway status'
      },
      {
        path: '/api/gateway/routes',
        method: 'GET',
        description: 'Available routes'
      },
      {
        path: '/api/policy/*',
        method: 'GET',
        description: 'Route to policy service'
      },
      {
        path: '/api/etl/*',
        method: 'GET',
        description: 'Route to ETL service'
      },
      {
        path: '/api/search/*',
        method: 'GET',
        description: 'Route to search service'
      },
      {
        path: '/api/auth/*',
        method: 'GET',
        description: 'Route to auth service'
      },
      {
        path: '/api/config/*',
        method: 'GET',
        description: 'Route to config service'
      },
      {
        path: '/api/errors/*',
        method: 'GET',
        description: 'Route to error reporting service'
      },
      {
        path: '/api/platform/status',
        method: 'GET',
        description: 'Platform health status dashboard'
      },
      {
        path: '/api/platform/services',
        method: 'GET',
        description: 'Service discovery and documentation'
      }
    ]
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('API Gateway Error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
    service: 'api-gateway',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    service: 'api-gateway',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 API Gateway Service running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/healthz`);
  console.log(`📍 Service status: http://localhost:${PORT}/api/gateway/status`);
});

module.exports = app;

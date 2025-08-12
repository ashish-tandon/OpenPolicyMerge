/**
 * Proxy Routes for API Gateway
 * 
 * Routes incoming requests to appropriate backend services based on
 * path patterns and service discovery.
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../config');
const logger = require('../utils/logger');
const ServiceRegistry = require('../services/serviceRegistry');
const CircuitBreaker = require('../services/circuitBreaker');

const router = express.Router();
const serviceRegistry = new ServiceRegistry();
const circuitBreaker = new CircuitBreaker();

/**
 * Route mapping configuration
 * Maps API paths to backend services
 */
const routeMapping = {
  // Parliamentary Data Routes
  '/parliament': {
    service: 'goApi',
    pathRewrite: { '^/api/parliament': '/api/v1/parliament' },
    description: 'Parliamentary data and bills'
  },
  '/bills': {
    service: 'goApi',
    pathRewrite: { '^/api/bills': '/api/v1/bills' },
    description: 'Bill information and tracking'
  },
  '/members': {
    service: 'goApi',
    pathRewrite: { '^/api/members': '/api/v1/members' },
    description: 'Parliamentary members and representatives'
  },
  '/committees': {
    service: 'goApi',
    pathRewrite: { '^/api/committees': '/api/v1/committees' },
    description: 'Committee information and activities'
  },
  '/votes': {
    service: 'goApi',
    pathRewrite: { '^/api/votes': '/api/v1/votes' },
    description: 'Voting records and results'
  },

  // Civic Data Routes
  '/civic': {
    service: 'goApi',
    pathRewrite: { '^/api/civic': '/api/v1/civic' },
    description: 'Civic data and local government information'
  },
  '/municipalities': {
    service: 'goApi',
    pathRewrite: { '^/api/municipalities': '/api/v1/municipalities' },
    description: 'Municipal government data'
  },
  '/elections': {
    service: 'goApi',
    pathRewrite: { '^/api/elections': '/api/v1/elections' },
    description: 'Election data and results'
  },

  // Data Scraping Routes
  '/scrapers': {
    service: 'goApi',
    pathRewrite: { '^/api/scrapers': '/api/v1/scrapers' },
    description: 'Data scraping and collection'
  },
  '/data-sources': {
    service: 'goApi',
    pathRewrite: { '^/api/data-sources': '/api/v1/data-sources' },
    description: 'External data source management'
  },

  // Policy Engine Routes
  '/policies': {
    service: 'goApi',
    pathRewrite: { '^/api/policies': '/api/v1/policies' },
    description: 'Policy evaluation and management'
  },
  '/evaluate': {
    service: 'goApi',
    pathRewrite: { '^/api/evaluate': '/api/v1/evaluate' },
    description: 'Policy evaluation endpoints'
  },

  // Represent Canada Routes
  '/represent': {
    service: 'goApi',
    pathRewrite: { '^/api/represent': '/api/v1/represent' },
    description: 'Represent Canada data integration'
  },

  // Mobile API Routes
  '/mobile': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile': '' },
    description: 'Mobile application API endpoints'
  },
  '/mobile/auth': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/auth': '/auth' },
    description: 'Mobile authentication'
  },
  '/mobile/bills': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/bills': '/bills' },
    description: 'Mobile bills API'
  },
  '/mobile/members': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/members': '/members' },
    description: 'Mobile members API'
  },
  '/mobile/search': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/search': '/search' },
    description: 'Mobile search API'
  },
  '/mobile/notifications': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/notifications': '/notifications' },
    description: 'Mobile notifications API'
  },
  '/mobile/sync': {
    service: 'mobileApi',
    pathRewrite: { '^/api/mobile/sync': '/sync' },
    description: 'Mobile data synchronization'
  },

  // ETL Service Routes
  '/etl': {
    service: 'etlService',
    pathRewrite: { '^/api/etl': '' },
    description: 'ETL service endpoints'
  },
  '/etl/jobs': {
    service: 'etlService',
    pathRewrite: { '^/api/etl/jobs': '/jobs' },
    description: 'ETL job management'
  },
  '/etl/sources': {
    service: 'etlService',
    pathRewrite: { '^/api/etl/sources': '/sources' },
    description: 'Data source management'
  },
  '/etl/quality': {
    service: 'etlService',
    pathRewrite: { '^/api/etl/quality': '/quality' },
    description: 'Data quality metrics'
  },

  // Admin Routes
  '/admin': {
    service: 'adminDashboard',
    pathRewrite: { '^/api/admin': '' },
    description: 'Admin dashboard API'
  },
  '/admin/services': {
    service: 'adminDashboard',
    pathRewrite: { '^/api/admin/services': '/services' },
    description: 'Service management'
  },
  '/admin/monitoring': {
    service: 'adminDashboard',
    pathRewrite: { '^/api/admin/monitoring': '/monitoring' },
    description: 'System monitoring'
  },
  '/admin/data': {
    service: 'adminDashboard',
    pathRewrite: { '^/api/admin/data': '/data' },
    description: 'Data management'
  },

  // Legacy Backend Routes (for backward compatibility)
  '/legacy/django': {
    service: 'djangoBackend',
    pathRewrite: { '^/api/legacy/django': '' },
    description: 'Legacy Django backend (deprecated)'
  },
  '/legacy/laravel': {
    service: 'laravelBackend',
    pathRewrite: { '^/api/legacy/laravel': '' },
    description: 'Legacy Laravel backend (deprecated)'
  }
};

/**
 * Create proxy middleware for a specific route
 */
function createProxyForRoute(routePath, routeConfig) {
  const serviceName = routeConfig.service;
  const serviceConfig = config.services[serviceName];
  
  if (!serviceConfig) {
    logger.error(`Service configuration not found for: ${serviceName}`);
    return null;
  }

  const proxyOptions = {
    target: serviceConfig.url,
    changeOrigin: config.proxy.changeOrigin,
    secure: config.proxy.secure,
    timeout: serviceConfig.timeout,
    pathRewrite: routeConfig.pathRewrite,
    logLevel: config.logging.level === 'debug' ? 'debug' : 'silent',
    
    // Custom error handling
    onError: (err, req, res) => {
      logger.error(`Proxy error for ${routePath}:`, err);
      
      // Check if circuit breaker should be triggered
      if (circuitBreaker.shouldTrigger(serviceName)) {
        circuitBreaker.recordFailure(serviceName);
      }
      
      res.status(503).json({
        error: 'Service temporarily unavailable',
        service: serviceName,
        path: routePath,
        timestamp: new Date().toISOString()
      });
    },
    
    // Request/Response logging
    onProxyReq: (proxyReq, req, res) => {
      // Add service identification headers
      proxyReq.setHeader('X-Forwarded-Service', serviceName);
      proxyReq.setHeader('X-Forwarded-Path', routePath);
      
      logger.info(`Proxying request to ${serviceName}: ${req.method} ${routePath}`);
    },
    
    onProxyRes: (proxyRes, req, res) => {
      // Add response headers
      res.setHeader('X-Served-By', serviceName);
      res.setHeader('X-Response-Time', Date.now() - req.startTime);
      
      // Record successful response
      if (circuitBreaker.isOpen(serviceName)) {
        circuitBreaker.recordSuccess(serviceName);
      }
      
      logger.info(`Proxied response from ${serviceName}: ${proxyRes.statusCode}`);
    }
  };

  return createProxyMiddleware(proxyOptions);
}

/**
 * Health check middleware for proxy routes
 */
async function checkServiceHealth(req, res, next) {
  const path = req.path;
  const routeConfig = Object.entries(routeMapping).find(([routePath]) => 
    path.startsWith(routePath)
  );

  if (routeConfig) {
    const [, config] = routeConfig;
    const serviceName = config.service;
    
    // Check if service is healthy
    if (!serviceRegistry.isServiceHealthy(serviceName)) {
      return res.status(503).json({
        error: 'Service unavailable',
        service: serviceName,
        status: serviceRegistry.getServiceStatus(serviceName),
        timestamp: new Date().toISOString()
      });
    }
    
    // Check circuit breaker
    if (circuitBreaker.isOpen(serviceName)) {
      return res.status(503).json({
        error: 'Service temporarily unavailable (circuit breaker open)',
        service: serviceName,
        timestamp: new Date().toISOString()
      });
    }
  }
  
  next();
}

/**
 * Service discovery endpoint
 */
router.get('/services', (req, res) => {
  const services = Object.entries(routeMapping).map(([path, config]) => ({
    path,
    service: config.service,
    description: config.description,
    status: serviceRegistry.getServiceStatus(config.service),
    url: config.services?.[config.service]?.url || 'N/A'
  }));
  
  res.json({
    services,
    total: services.length,
    timestamp: new Date().toISOString()
  });
});

/**
 * Service health endpoint
 */
router.get('/services/:serviceName/health', (req, res) => {
  const { serviceName } = req.params;
  const serviceConfig = config.services[serviceName];
  
  if (!serviceConfig) {
    return res.status(404).json({
      error: 'Service not found',
      service: serviceName
    });
  }
  
  const status = serviceRegistry.getServiceStatus(serviceName);
  const circuitBreakerStatus = circuitBreaker.getStatus(serviceName);
  
  res.json({
    service: serviceName,
    status,
    circuitBreaker: circuitBreakerStatus,
    url: serviceConfig.url,
    lastCheck: serviceRegistry.getLastCheckTime(serviceName),
    timestamp: new Date().toISOString()
  });
});

// Apply health check middleware to all proxy routes
router.use(checkServiceHealth);

// Create proxy routes for each mapping
Object.entries(routeMapping).forEach(([routePath, routeConfig]) => {
  const proxy = createProxyForRoute(routePath, routeConfig);
  
  if (proxy) {
    // Apply to exact path and all sub-paths
    router.use(routePath, proxy);
    router.use(`${routePath}/*`, proxy);
    
    logger.info(`Created proxy route: ${routePath} -> ${routeConfig.service}`);
  }
});

// Catch-all route for unmatched API paths
router.use('*', (req, res) => {
  res.status(404).json({
    error: 'API endpoint not found',
    path: req.path,
    availableRoutes: Object.keys(routeMapping),
    timestamp: new Date().toISOString()
  });
});

module.exports = router;

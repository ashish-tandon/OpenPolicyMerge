// API Gateway Configuration with Service Discovery
// This file configures the API Gateway to route traffic to all OpenPolicy services

const config = {
  // Server Configuration
  server: {
    port: process.env.GATEWAY_PORT || 9009,
    host: process.env.GATEWAY_HOST || '0.0.0.0',
    environment: process.env.ENVIRONMENT || 'development',
    logLevel: process.env.LOG_LEVEL || 'info'
  },

  // Service Discovery Configuration
  services: {
    // Core Services
    policy: {
      name: 'Policy Service',
      url: process.env.POLICY_SERVICE_URL || 'http://localhost:9001',
      healthEndpoint: '/healthz',
      routes: ['/api/policy/*', '/api/policies/*']
    },
    
    search: {
      name: 'Search Service',
      url: process.env.SEARCH_SERVICE_URL || 'http://localhost:9002',
      healthEndpoint: '/healthz',
      routes: ['/api/search/*', '/api/query/*']
    },
    
    auth: {
      name: 'Auth Service',
      url: process.env.AUTH_SERVICE_URL || 'http://localhost:9003',
      healthEndpoint: '/healthz',
      routes: ['/api/auth/*', '/api/users/*', '/api/login', '/api/register']
    },
    
    notification: {
      name: 'Notification Service',
      url: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:9004',
      healthEndpoint: '/healthz',
      routes: ['/api/notifications/*', '/api/email/*', '/api/sms/*']
    },
    
    config: {
      name: 'Config Service',
      url: process.env.CONFIG_SERVICE_URL || 'http://localhost:9005',
      healthEndpoint: '/healthz',
      routes: ['/api/config/*', '/api/settings/*']
    },
    
    health: {
      name: 'Health Service',
      url: process.env.HEALTH_SERVICE_URL || 'http://localhost:9006',
      healthEndpoint: '/healthz',
      routes: ['/api/health/*', '/api/status/*']
    },
    
    etl: {
      name: 'ETL Service',
      url: process.env.ETL_SERVICE_URL || 'http://localhost:9007',
      healthEndpoint: '/healthz',
      routes: ['/api/etl/*', '/api/data/*', '/api/process/*']
    },
    
    scraper: {
      name: 'Scraper Service',
      url: process.env.SCRAPER_SERVICE_URL || 'http://localhost:9008',
      healthEndpoint: '/healthz',
      routes: ['/api/scraper/*', '/api/scrape/*', '/api/jurisdictions/*']
    },
    
    monitoring: {
      name: 'Monitoring Service',
      url: process.env.MONITORING_SERVICE_URL || 'http://localhost:9010',
      healthEndpoint: '/healthz',
      routes: ['/api/monitoring/*', '/api/metrics/*', '/api/alerts/*']
    },
    
    plotly: {
      name: 'Plotly Service',
      url: process.env.PLOTLY_SERVICE_URL || 'http://localhost:9011',
      healthEndpoint: '/healthz',
      routes: ['/api/plotly/*', '/api/charts/*', '/api/visualizations/*']
    },
    
    mcp: {
      name: 'MCP Service',
      url: process.env.MCP_SERVICE_URL || 'http://localhost:9012',
      healthEndpoint: '/healthz',
      routes: ['/api/mcp/*', '/api/model/*', '/api/context/*']
    }
  },

  // Frontend Services
  frontend: {
    web: {
      name: 'Web Frontend',
      url: process.env.WEB_FRONTEND_URL || 'http://localhost:3000',
      healthEndpoint: '/',
      routes: ['/web/*', '/frontend/*']
    },
    
    mobile: {
      name: 'Mobile API',
      url: process.env.MOBILE_API_URL || 'http://localhost:8081',
      healthEndpoint: '/',
      routes: ['/mobile/*', '/app/*']
    },
    
    admin: {
      name: 'Admin Dashboard',
      url: process.env.ADMIN_DASHBOARD_URL || 'http://localhost:3001',
      healthEndpoint: '/',
      routes: ['/admin/*', '/dashboard/*']
    }
  },

  // Security Configuration
  security: {
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
    corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['*']
  },

  // Database Configuration
  database: {
    postgres: {
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT) || 5432,
      username: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'password',
      database: process.env.DB_NAME || 'openpolicy'
    },
    
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379/1'
    }
  },

  // Monitoring Configuration
  monitoring: {
    prometheus: {
      enabled: process.env.PROMETHEUS_ENABLED === 'true',
      port: parseInt(process.env.PROMETHEUS_PORT) || 9090
    },
    
    healthCheck: {
      interval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000,
      timeout: parseInt(process.env.HEALTH_CHECK_TIMEOUT) || 5000
    }
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
    output: process.env.LOG_OUTPUT || 'stdout'
  }
};

module.exports = config;

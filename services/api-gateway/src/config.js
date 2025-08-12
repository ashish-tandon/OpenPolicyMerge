/**
 * Configuration for the OpenPolicy API Gateway
 */

const config = {
  // Server Configuration
  server: {
    port: process.env.GATEWAY_PORT || 8000,
    host: process.env.GATEWAY_HOST || '0.0.0.0',
    environment: process.env.NODE_ENV || 'development',
    cors: {
      origin: process.env.CORS_ORIGIN?.split(',') || ['*'],
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'X-Request-ID']
    }
  },

  // Authentication & Security
  auth: {
    jwtSecret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 12,
    rateLimit: {
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false
    }
  },

  // Service Discovery & Routing
  services: {
    // Main Web Application
    webApp: {
      name: 'web-app',
      url: process.env.WEB_APP_URL || 'http://localhost:8001',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // Admin Dashboard
    adminDashboard: {
      name: 'admin-dashboard',
      url: process.env.ADMIN_DASHBOARD_URL || 'http://localhost:8002',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // Mobile API Service
    mobileApi: {
      name: 'mobile-api',
      url: process.env.MOBILE_API_URL || 'http://localhost:8002',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // ETL Service
    etlService: {
      name: 'etl-service',
      url: process.env.ETL_SERVICE_URL || 'http://localhost:8003',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // Go API Server
    goApi: {
      name: 'go-api',
      url: process.env.GO_API_URL || 'http://localhost:8080',
      healthCheck: '/api/v1/health',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // Legacy Django Backend
    djangoBackend: {
      name: 'django-backend',
      url: process.env.DJANGO_BACKEND_URL || 'http://localhost:8001',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    },

    // Legacy Laravel Backend
    laravelBackend: {
      name: 'laravel-backend',
      url: process.env.LARAVEL_BACKEND_URL || 'http://localhost:8002',
      healthCheck: '/healthz',
      timeout: 30000,
      circuitBreaker: {
        failureThreshold: 5,
        recoveryTimeout: 60000,
        expectedStatus: [200, 201, 204]
      }
    }
  },

  // Database Configuration
  database: {
    mongodb: {
      uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/openpolicy_gateway',
      options: {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000
      }
    },
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT) || 6379,
      password: process.env.REDIS_PASSWORD || null,
      db: parseInt(process.env.REDIS_DB) || 0,
      maxRetriesPerRequest: 3,
      retryDelayOnFailover: 100
    }
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
    transports: ['console', 'file'],
    file: {
      filename: process.env.LOG_FILE || 'logs/api-gateway.log',
      maxSize: process.env.LOG_MAX_SIZE || '10m',
      maxFiles: parseInt(process.env.LOG_MAX_FILES) || 5
    }
  },

  // Monitoring Configuration
  monitoring: {
    enabled: process.env.MONITORING_ENABLED !== 'false',
    prometheus: {
      enabled: process.env.PROMETHEUS_ENABLED !== 'false',
      port: parseInt(process.env.PROMETHEUS_PORT) || 9090
    },
    healthCheck: {
      interval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000, // 30 seconds
      timeout: parseInt(process.env.HEALTH_CHECK_TIMEOUT) || 10000   // 10 seconds
    }
  },

  // API Documentation
  swagger: {
    enabled: process.env.SWAGGER_ENABLED !== 'false',
    title: 'OpenPolicy API Gateway',
    version: '1.0.0',
    description: 'Unified API Gateway for OpenPolicy Platform',
    contact: {
      name: 'OpenPolicy Team',
      email: 'team@openpolicy.com'
    }
  },

  // Feature Flags
  features: {
    authentication: process.env.FEATURE_AUTH !== 'false',
    rateLimiting: process.env.FEATURE_RATE_LIMITING !== 'false',
    circuitBreaker: process.env.FEATURE_CIRCUIT_BREAKER !== 'false',
    caching: process.env.FEATURE_CACHING !== 'false',
    monitoring: process.env.FEATURE_MONITORING !== 'false',
    logging: process.env.FEATURE_LOGGING !== 'false'
  },

  // Cache Configuration
  cache: {
    ttl: parseInt(process.env.CACHE_TTL) || 300, // 5 minutes
    checkPeriod: parseInt(process.env.CACHE_CHECK_PERIOD) || 600, // 10 minutes
    maxKeys: parseInt(process.env.CACHE_MAX_KEYS) || 1000
  },

  // Proxy Configuration
  proxy: {
    timeout: parseInt(process.env.PROXY_TIMEOUT) || 30000,
    followRedirects: process.env.PROXY_FOLLOW_REDIRECTS !== 'false',
    changeOrigin: process.env.PROXY_CHANGE_ORIGIN !== 'false',
    secure: process.env.PROXY_SECURE !== 'false'
  }
};

// Environment-specific overrides
if (config.server.environment === 'production') {
  config.auth.jwtSecret = process.env.JWT_SECRET;
  config.logging.level = 'warn';
  config.features.swagger = false;
} else if (config.server.environment === 'test') {
  config.database.mongodb.uri = process.env.TEST_MONGODB_URI || 'mongodb://localhost:27017/openpolicy_gateway_test';
  config.database.redis.db = parseInt(process.env.TEST_REDIS_DB) || 1;
}

module.exports = config;

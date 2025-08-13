/**
 * Configuration for Mobile API Service
 */

const config = {
  // Service identification
  service: {
    name: process.env.SERVICE_NAME || 'mobile-api',
    version: process.env.SERVICE_VERSION || '1.0.0',
    port: parseInt(process.env.SERVICE_PORT) || 9020
  },

  // Server configuration
  server: {
    host: process.env.HOST || '0.0.0.0',
    port: parseInt(process.env.SERVICE_PORT) || 9020,
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      credentials: true
    }
  },

  // Database configuration
  database: {
    url: process.env.DATABASE_URL || 'postgresql://user:pass@localhost/db',
    poolSize: parseInt(process.env.DB_POOL_SIZE) || 10,
    maxOverflow: parseInt(process.env.DB_MAX_OVERFLOW) || 20
  },

  // Cache configuration
  cache: {
    url: process.env.CACHE_URL || 'redis://localhost:6379',
    ttl: parseInt(process.env.CACHE_TTL) || 3600
  },

  // Authentication
  auth: {
    enabled: process.env.ENABLE_AUTH === 'true',
    secret: process.env.JWT_SECRET || 'your-secret-key',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d'
  },

  // External service dependencies
  services: {
    apiGateway: process.env.API_GATEWAY_URL || 'http://localhost:9001',
    authService: process.env.AUTH_SERVICE_URL || 'http://localhost:9003',
    policyService: process.env.POLICY_SERVICE_URL || 'http://localhost:9001',
    searchService: process.env.SEARCH_SERVICE_URL || 'http://localhost:9002',
    etlService: process.env.ETL_SERVICE_URL || 'http://localhost:9007'
  },

  // Mobile-specific features
  mobile: {
    enablePushNotifications: process.env.ENABLE_PUSH_NOTIFICATIONS === 'true',
    enableOfflineMode: process.env.ENABLE_OFFLINE_MODE === 'true',
    maxOfflineData: parseInt(process.env.MAX_OFFLINE_DATA) || 100 * 1024 * 1024, // 100MB
    syncInterval: parseInt(process.env.SYNC_INTERVAL) || 300000 // 5 minutes
  },

  // API rate limiting
  rateLimit: {
    enabled: process.env.ENABLE_RATE_LIMITING === 'true',
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100 // requests per window
  },

  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'combined'
  },

  // Health check
  healthCheck: {
    interval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000, // 30 seconds
    timeout: parseInt(process.env.HEALTH_CHECK_TIMEOUT) || 5000 // 5 seconds
  },

  // Performance
  performance: {
    enableCompression: process.env.ENABLE_COMPRESSION === 'true',
    enableCaching: process.env.ENABLE_CACHING === 'true',
    maxPayloadSize: parseInt(process.env.MAX_PAYLOAD_SIZE) || 10 * 1024 * 1024 // 10MB
  },

  // Security
  security: {
    enableHelmet: process.env.ENABLE_HELMET === 'true',
    enableHsts: process.env.ENABLE_HSTS === 'true',
    enableXssProtection: process.env.ENABLE_XSS_PROTECTION === 'true'
  },

  // Monitoring
  monitoring: {
    enableMetrics: process.env.ENABLE_METRICS === 'true',
    enableTracing: process.env.ENABLE_TRACING === 'true',
    enableProfiling: process.env.ENABLE_PROFILING === 'true'
  }
};

module.exports = config;

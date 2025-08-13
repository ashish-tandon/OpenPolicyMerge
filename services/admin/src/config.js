/**
 * Configuration for Admin Dashboard Service
 */

const config = {
  // Service identification
  service: {
    name: process.env.SERVICE_NAME || 'admin-dashboard',
    version: process.env.SERVICE_VERSION || '1.0.0',
    port: parseInt(process.env.SERVICE_PORT) || 9021
  },

  // Server configuration
  server: {
    host: process.env.HOST || '0.0.0.0',
    port: parseInt(process.env.SERVICE_PORT) || 9021,
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

  // Authentication & Authorization
  auth: {
    enabled: process.env.ENABLE_AUTH === 'true',
    secret: process.env.JWT_SECRET || 'your-secret-key',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
    adminRole: process.env.ADMIN_ROLE || 'admin',
    superAdminRole: process.env.SUPER_ADMIN_ROLE || 'super_admin'
  },

  // External service dependencies
  services: {
    apiGateway: process.env.API_GATEWAY_URL || 'http://localhost:9001',
    authService: process.env.AUTH_SERVICE_URL || 'http://localhost:9003',
    policyService: process.env.POLICY_SERVICE_URL || 'http://localhost:9001',
    searchService: process.env.SEARCH_SERVICE_URL || 'http://localhost:9002',
    etlService: process.env.ETL_SERVICE_URL || 'http://localhost:9007',
    monitoringService: process.env.MONITORING_SERVICE_URL || 'http://localhost:9010',
    analyticsService: process.env.ANALYTICS_SERVICE_URL || 'http://localhost:9013'
  },

  // Admin features
  admin: {
    enableUserManagement: process.env.ENABLE_USER_MANAGEMENT === 'true',
    enableServiceManagement: process.env.ENABLE_SERVICE_MANAGEMENT === 'true',
    enableSystemMonitoring: process.env.ENABLE_SYSTEM_MONITORING === 'true',
    enableAuditLogs: process.env.ENABLE_AUDIT_LOGS === 'true',
    enableBackupRestore: process.env.ENABLE_BACKUP_RESTORE === 'true'
  },

  // Dashboard configuration
  dashboard: {
    refreshInterval: parseInt(process.env.DASHBOARD_REFRESH_INTERVAL) || 30000, // 30 seconds
    maxWidgets: parseInt(process.env.MAX_WIDGETS) || 20,
    enableRealTimeUpdates: process.env.ENABLE_REAL_TIME_UPDATES === 'true',
    enableCustomDashboards: process.env.ENABLE_CUSTOM_DASHBOARDS === 'true'
  },

  // Security settings
  security: {
    enable2FA: process.env.ENABLE_2FA === 'true',
    enableIPWhitelist: process.env.ENABLE_IP_WHITELIST === 'true',
    allowedIPs: process.env.ALLOWED_IPS ? process.env.ALLOWED_IPS.split(',') : [],
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 3600000, // 1 hour
    maxLoginAttempts: parseInt(process.env.MAX_LOGIN_ATTEMPTS) || 5
  },

  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'combined',
    enableAuditLog: process.env.ENABLE_AUDIT_LOG === 'true',
    logRetentionDays: parseInt(process.env.LOG_RETENTION_DAYS) || 90
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

  // Monitoring
  monitoring: {
    enableMetrics: process.env.ENABLE_METRICS === 'true',
    enableTracing: process.env.ENABLE_TRACING === 'true',
    enableProfiling: process.env.ENABLE_PROFILING === 'true',
    enableAlerting: process.env.ENABLE_ALERTING === 'true'
  }
};

module.exports = config;

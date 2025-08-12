/**
 * OpenPolicy API Gateway - Main Server
 * 
 * This service acts as a unified entry point for all OpenPolicy platform APIs,
 * providing routing, authentication, rate limiting, and monitoring.
 */

require('express-async-errors');
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

// Import configuration and utilities
const config = require('./config');
const logger = require('./utils/logger');
const { connectDatabase } = require('./database/connection');
const { connectCache } = require('./database/cache');

// Import middleware
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');
const { authenticateToken, optionalAuth } = require('./middleware/auth');
const { healthCheck } = require('./middleware/healthCheck');
const { metricsMiddleware } = require('./middleware/monitoring');

// Import routes
const authRoutes = require('./routes/auth');
const proxyRoutes = require('./routes/proxy');
const healthRoutes = require('./routes/health');
const metricsRoutes = require('./routes/metrics');
const adminRoutes = require('./routes/admin');

// Import service discovery
const ServiceRegistry = require('./services/serviceRegistry');
const CircuitBreaker = require('./services/circuitBreaker');

class ApiGateway {
  constructor() {
    this.app = express();
    this.server = null;
    this.serviceRegistry = new ServiceRegistry();
    this.circuitBreaker = new CircuitBreaker();
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupErrorHandling();
    this.setupSwagger();
  }

  async initialize() {
    try {
      // Connect to databases
      await connectDatabase();
      await connectCache();
      
      // Initialize service registry
      await this.serviceRegistry.initialize();
      
      // Start health monitoring
      this.startHealthMonitoring();
      
      logger.info('API Gateway initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize API Gateway:', error);
      throw error;
    }
  }

  setupMiddleware() {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"],
        },
      },
      crossOriginEmbedderPolicy: false
    }));

    // CORS configuration
    this.app.use(cors(config.server.cors));

    // Request parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Compression
    this.app.use(compression());

    // Logging
    if (config.features.logging) {
      this.app.use(morgan('combined', {
        stream: { write: (message) => logger.info(message.trim()) }
      }));
    }

    // Rate limiting
    if (config.features.rateLimiting) {
      this.app.use(rateLimit(config.auth.rateLimit));
    }

    // Request ID and timing
    this.app.use((req, res, next) => {
      req.id = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      req.startTime = Date.now();
      res.setHeader('X-Request-ID', req.id);
      next();
    });

    // Monitoring middleware
    if (config.features.monitoring) {
      this.app.use(metricsMiddleware);
    }
  }

  setupRoutes() {
    // Health check routes (no auth required)
    this.app.use('/healthz', healthRoutes);
    this.app.use('/readyz', healthRoutes);
    this.app.use('/livez', healthRoutes);

    // Metrics endpoint (no auth required)
    if (config.features.monitoring) {
      this.app.use('/metrics', metricsRoutes);
    }

    // Authentication routes
    if (config.features.authentication) {
      this.app.use('/auth', authRoutes);
    }

    // Admin routes (require admin authentication)
    if (config.features.authentication) {
      this.app.use('/admin', authenticateToken, adminRoutes);
    }

    // Proxy routes for service routing
    this.app.use('/api', proxyRoutes);

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        service: 'OpenPolicy API Gateway',
        version: '1.0.0',
        status: 'operational',
        timestamp: new Date().toISOString(),
        endpoints: {
          health: '/healthz',
          metrics: '/metrics',
          auth: '/auth',
          admin: '/admin',
          api: '/api',
          docs: '/docs'
        },
        services: Object.keys(config.services).map(key => ({
          name: config.services[key].name,
          status: this.serviceRegistry.getServiceStatus(key)
        }))
      });
    });
  }

  setupSwagger() {
    if (config.swagger.enabled) {
      const swaggerOptions = {
        definition: {
          openapi: '3.0.0',
          info: {
            title: config.swagger.title,
            version: config.swagger.version,
            description: config.swagger.description,
            contact: config.swagger.contact
          },
          servers: [
            {
              url: `http://localhost:${config.server.port}`,
              description: 'Development server'
            }
          ],
          components: {
            securitySchemes: {
              bearerAuth: {
                type: 'http',
                scheme: 'bearer',
                bearerFormat: 'JWT'
              }
            }
          }
        },
        apis: ['./src/routes/*.js', './src/models/*.js']
      };

      const specs = swaggerJsdoc(swaggerOptions);
      this.app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs));
    }
  }

  setupErrorHandling() {
    // 404 handler
    this.app.use(notFoundHandler);
    
    // Global error handler
    this.app.use(errorHandler);
  }

  startHealthMonitoring() {
    if (config.features.monitoring) {
      setInterval(async () => {
        try {
          await this.serviceRegistry.checkAllServices();
        } catch (error) {
          logger.error('Health monitoring error:', error);
        }
      }, config.monitoring.healthCheck.interval);
    }
  }

  async start() {
    try {
      await this.initialize();
      
      this.server = this.app.listen(config.server.port, config.server.host, () => {
        logger.info(`API Gateway started on ${config.server.host}:${config.server.port}`);
        logger.info(`Environment: ${config.server.environment}`);
        logger.info(`Documentation: http://${config.server.host}:${config.server.port}/docs`);
      });

      // Graceful shutdown
      process.on('SIGTERM', () => this.gracefulShutdown());
      process.on('SIGINT', () => this.gracefulShutdown());

    } catch (error) {
      logger.error('Failed to start API Gateway:', error);
      process.exit(1);
    }
  }

  async gracefulShutdown() {
    logger.info('Received shutdown signal, starting graceful shutdown...');
    
    if (this.server) {
      this.server.close(() => {
        logger.info('HTTP server closed');
        process.exit(0);
      });

      // Force close after 30 seconds
      setTimeout(() => {
        logger.error('Could not close connections in time, forcefully shutting down');
        process.exit(1);
      }, 30000);
    }
  }
}

// Start the server if this file is run directly
if (require.main === module) {
  const gateway = new ApiGateway();
  gateway.start().catch((error) => {
    logger.error('Failed to start API Gateway:', error);
    process.exit(1);
  });
}

module.exports = ApiGateway;

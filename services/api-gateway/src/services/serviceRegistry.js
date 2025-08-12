/**
 * Service Registry for API Gateway
 * 
 * Manages service discovery, health monitoring, and status tracking
 * for all backend services in the OpenPolicy platform.
 */

const axios = require('axios');
const config = require('../config');
const logger = require('../utils/logger');

class ServiceRegistry {
  constructor() {
    this.services = new Map();
    this.healthChecks = new Map();
    this.lastCheckTimes = new Map();
    this.healthCheckInterval = null;
    
    this.initializeServices();
  }

  /**
   * Initialize all services from configuration
   */
  initializeServices() {
    Object.entries(config.services).forEach(([key, serviceConfig]) => {
      this.services.set(key, {
        ...serviceConfig,
        status: 'unknown',
        lastSeen: null,
        responseTime: null,
        errorCount: 0,
        successCount: 0,
        uptime: 0
      });
      
      this.lastCheckTimes.set(key, null);
      logger.info(`Registered service: ${key} -> ${serviceConfig.url}`);
    });
  }

  /**
   * Initialize the service registry
   */
  async initialize() {
    logger.info('Initializing Service Registry...');
    
    // Perform initial health check for all services
    await this.checkAllServices();
    
    // Start periodic health monitoring
    this.startHealthMonitoring();
    
    logger.info('Service Registry initialized successfully');
  }

  /**
   * Start periodic health monitoring
   */
  startHealthMonitoring() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(async () => {
      try {
        await this.checkAllServices();
      } catch (error) {
        logger.error('Health monitoring error:', error);
      }
    }, config.monitoring.healthCheck.interval);

    logger.info(`Health monitoring started with ${config.monitoring.healthCheck.interval}ms interval`);
  }

  /**
   * Check health of all services
   */
  async checkAllServices() {
    const promises = Array.from(this.services.keys()).map(serviceName => 
      this.checkServiceHealth(serviceName)
    );

    try {
      await Promise.allSettled(promises);
      logger.debug('Completed health check for all services');
    } catch (error) {
      logger.error('Error during bulk health check:', error);
    }
  }

  /**
   * Check health of a specific service
   */
  async checkServiceHealth(serviceName) {
    const service = this.services.get(serviceName);
    if (!service) {
      logger.warn(`Service not found in registry: ${serviceName}`);
      return false;
    }

    const startTime = Date.now();
    let isHealthy = false;
    let responseTime = null;
    let error = null;

    try {
      const response = await axios.get(`${service.url}${service.healthCheck}`, {
        timeout: config.monitoring.healthCheck.timeout,
        validateStatus: (status) => status < 500 // Consider 4xx as healthy (service is responding)
      });

      responseTime = Date.now() - startTime;
      isHealthy = response.status < 500;
      
      if (isHealthy) {
        service.successCount++;
        service.errorCount = Math.max(0, service.errorCount - 1); // Gradually reduce error count
      } else {
        service.errorCount++;
        error = `HTTP ${response.status}`;
      }

    } catch (err) {
      responseTime = Date.now() - startTime;
      service.errorCount++;
      error = err.message;
      
      if (err.code === 'ECONNREFUSED') {
        error = 'Connection refused';
      } else if (err.code === 'ETIMEDOUT') {
        error = 'Request timeout';
      } else if (err.code === 'ENOTFOUND') {
        error = 'Service not found';
      }
    }

    // Update service status
    const previousStatus = service.status;
    service.status = this.determineServiceStatus(service, isHealthy);
    service.lastSeen = isHealthy ? new Date() : service.lastSeen;
    service.responseTime = responseTime;
    service.uptime = isHealthy ? (service.uptime || 0) + 1 : service.uptime || 0;

    // Update last check time
    this.lastCheckTimes.set(serviceName, new Date());

    // Log status changes
    if (previousStatus !== service.status) {
      logger.info(`Service ${serviceName} status changed: ${previousStatus} -> ${service.status}`);
    }

    // Log errors
    if (error && !isHealthy) {
      logger.warn(`Service ${serviceName} health check failed: ${error}`);
    }

    return isHealthy;
  }

  /**
   * Determine service status based on health check results
   */
  determineServiceStatus(service, isHealthy) {
    if (isHealthy) {
      if (service.errorCount === 0) {
        return 'healthy';
      } else if (service.errorCount <= 2) {
        return 'degraded';
      } else {
        return 'unhealthy';
      }
    } else {
      if (service.errorCount >= 5) {
        return 'down';
      } else if (service.errorCount >= 3) {
        return 'unhealthy';
      } else {
        return 'degraded';
      }
    }
  }

  /**
   * Get service status
   */
  getServiceStatus(serviceName) {
    const service = this.services.get(serviceName);
    return service ? service.status : 'unknown';
  }

  /**
   * Get service information
   */
  getServiceInfo(serviceName) {
    const service = this.services.get(serviceName);
    if (!service) return null;

    return {
      name: service.name,
      url: service.url,
      status: service.status,
      lastSeen: service.lastSeen,
      responseTime: service.responseTime,
      errorCount: service.errorCount,
      successCount: service.successCount,
      uptime: service.uptime,
      lastCheck: this.lastCheckTimes.get(serviceName)
    };
  }

  /**
   * Get all services information
   */
  getAllServices() {
    const services = [];
    
    for (const [key, service] of this.services) {
      services.push({
        key,
        ...this.getServiceInfo(key)
      });
    }
    
    return services;
  }

  /**
   * Check if a service is healthy
   */
  isServiceHealthy(serviceName) {
    const status = this.getServiceStatus(serviceName);
    return status === 'healthy' || status === 'degraded';
  }

  /**
   * Get last check time for a service
   */
  getLastCheckTime(serviceName) {
    return this.lastCheckTimes.get(serviceName);
  }

  /**
   * Get service statistics
   */
  getServiceStats() {
    const stats = {
      total: this.services.size,
      healthy: 0,
      degraded: 0,
      unhealthy: 0,
      down: 0,
      unknown: 0
    };

    for (const service of this.services.values()) {
      switch (service.status) {
        case 'healthy':
          stats.healthy++;
          break;
        case 'degraded':
          stats.degraded++;
          break;
        case 'unhealthy':
          stats.unhealthy++;
          break;
        case 'down':
          stats.down++;
          break;
        default:
          stats.unknown++;
      }
    }

    return stats;
  }

  /**
   * Get services by status
   */
  getServicesByStatus(status) {
    const services = [];
    
    for (const [key, service] of this.services) {
      if (service.status === status) {
        services.push({
          key,
          ...this.getServiceInfo(key)
        });
      }
    }
    
    return services;
  }

  /**
   * Manually trigger health check for a service
   */
  async triggerHealthCheck(serviceName) {
    logger.info(`Manual health check triggered for service: ${serviceName}`);
    return await this.checkServiceHealth(serviceName);
  }

  /**
   * Reset service error count
   */
  resetServiceErrors(serviceName) {
    const service = this.services.get(serviceName);
    if (service) {
      service.errorCount = 0;
      logger.info(`Reset error count for service: ${serviceName}`);
    }
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
      logger.info('Health monitoring stopped');
    }
  }

  /**
   * Cleanup resources
   */
  async cleanup() {
    this.stopHealthMonitoring();
    logger.info('Service Registry cleaned up');
  }
}

module.exports = ServiceRegistry;

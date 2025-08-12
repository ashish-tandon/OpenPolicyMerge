/**
 * Circuit Breaker Implementation for API Gateway
 * 
 * Provides fault tolerance by temporarily stopping requests to failing services
 * and allowing them to recover before resuming normal operation.
 */

const logger = require('../utils/logger');

class CircuitBreaker {
  constructor() {
    this.breakers = new Map();
    this.defaultConfig = {
      failureThreshold: 5,        // Number of failures before opening circuit
      recoveryTimeout: 60000,     // Time to wait before attempting recovery (ms)
      expectedStatus: [200, 201, 204], // HTTP status codes considered successful
      monitorInterval: 10000      // Interval to check circuit state (ms)
    };
  }

  /**
   * Initialize circuit breaker for a service
   */
  initializeService(serviceName, config = {}) {
    const breakerConfig = { ...this.defaultConfig, ...config };
    
    this.breakers.set(serviceName, {
      state: 'CLOSED',           // CLOSED, OPEN, HALF_OPEN
      failureCount: 0,
      successCount: 0,
      lastFailureTime: null,
      lastSuccessTime: null,
      nextAttemptTime: null,
      config: breakerConfig,
      stats: {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        circuitOpens: 0,
        circuitCloses: 0,
        lastResetTime: new Date()
      }
    });

    logger.info(`Circuit breaker initialized for service: ${serviceName}`);
  }

  /**
   * Check if circuit breaker should be triggered
   */
  shouldTrigger(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return false;
    }

    return breaker.failureCount >= breaker.config.failureThreshold;
  }

  /**
   * Record a failure for a service
   */
  recordFailure(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return;
    }

    breaker.failureCount++;
    breaker.lastFailureTime = new Date();
    breaker.stats.failedRequests++;
    breaker.stats.totalRequests++;

    // Check if circuit should open
    if (breaker.failureCount >= breaker.config.failureThreshold && breaker.state === 'CLOSED') {
      this.openCircuit(serviceName);
    }

    logger.debug(`Circuit breaker failure recorded for ${serviceName}: ${breaker.failureCount}/${breaker.config.failureThreshold}`);
  }

  /**
   * Record a success for a service
   */
  recordSuccess(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return;
    }

    breaker.successCount++;
    breaker.lastSuccessTime = new Date();
    breaker.stats.successfulRequests++;
    breaker.stats.totalRequests++;

    // Reset failure count on success
    if (breaker.failureCount > 0) {
      breaker.failureCount = Math.max(0, breaker.failureCount - 1);
    }

    // Check if circuit should close (if in HALF_OPEN state)
    if (breaker.state === 'HALF_OPEN' && breaker.successCount >= 3) {
      this.closeCircuit(serviceName);
    }

    logger.debug(`Circuit breaker success recorded for ${serviceName}: ${breaker.successCount} consecutive`);
  }

  /**
   * Open the circuit breaker
   */
  openCircuit(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker || breaker.state === 'OPEN') return;

    breaker.state = 'OPEN';
    breaker.nextAttemptTime = new Date(Date.now() + breaker.config.recoveryTimeout);
    breaker.stats.circuitOpens++;
    breaker.successCount = 0; // Reset success count

    logger.warn(`Circuit breaker OPEN for service: ${serviceName}. Next attempt at: ${breaker.nextAttemptTime.toISOString()}`);
  }

  /**
   * Close the circuit breaker
   */
  closeCircuit(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker || breaker.state === 'CLOSED') return;

    breaker.state = 'CLOSED';
    breaker.failureCount = 0;
    breaker.successCount = 0;
    breaker.lastFailureTime = null;
    breaker.lastSuccessTime = null;
    breaker.nextAttemptTime = null;
    breaker.stats.circuitCloses++;
    breaker.stats.lastResetTime = new Date();

    logger.info(`Circuit breaker CLOSED for service: ${serviceName}`);
  }

  /**
   * Attempt to transition to HALF_OPEN state
   */
  attemptHalfOpen(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker || breaker.state !== 'OPEN') return false;

    const now = new Date();
    if (now < breaker.nextAttemptTime) {
      return false; // Not yet time to attempt recovery
    }

    breaker.state = 'HALF_OPEN';
    breaker.successCount = 0;
    breaker.failureCount = 0;

    logger.info(`Circuit breaker HALF_OPEN for service: ${serviceName}. Testing recovery...`);
    return true;
  }

  /**
   * Check if circuit breaker is open
   */
  isOpen(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return false;
    }

    // Check if it's time to attempt recovery
    if (breaker.state === 'OPEN') {
      this.attemptHalfOpen(serviceName);
    }

    return breaker.state === 'OPEN';
  }

  /**
   * Check if circuit breaker is closed
   */
  isClosed(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return true;
    }

    return breaker.state === 'CLOSED';
  }

  /**
   * Check if circuit breaker is in half-open state
   */
  isHalfOpen(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) return false;

    return breaker.state === 'HALF_OPEN';
  }

  /**
   * Get circuit breaker status
   */
  getStatus(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return this.getStatus(serviceName);
    }

    return {
      state: breaker.state,
      failureCount: breaker.failureCount,
      successCount: breaker.successCount,
      lastFailureTime: breaker.lastFailureTime,
      lastSuccessTime: breaker.lastSuccessTime,
      nextAttemptTime: breaker.nextAttemptTime,
      config: breaker.config,
      stats: { ...breaker.stats }
    };
  }

  /**
   * Get all circuit breaker statuses
   */
  getAllStatuses() {
    const statuses = {};
    
    for (const [serviceName] of this.breakers) {
      statuses[serviceName] = this.getStatus(serviceName);
    }
    
    return statuses;
  }

  /**
   * Manually reset circuit breaker for a service
   */
  reset(serviceName) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName);
      return;
    }

    this.closeCircuit(serviceName);
    logger.info(`Circuit breaker manually reset for service: ${serviceName}`);
  }

  /**
   * Reset all circuit breakers
   */
  resetAll() {
    for (const [serviceName] of this.breakers) {
      this.reset(serviceName);
    }
    
    logger.info('All circuit breakers reset');
  }

  /**
   * Get circuit breaker statistics
   */
  getStats() {
    const stats = {
      totalServices: this.breakers.size,
      openCircuits: 0,
      closedCircuits: 0,
      halfOpenCircuits: 0,
      totalOpens: 0,
      totalCloses: 0
    };

    for (const breaker of this.breakers.values()) {
      switch (breaker.state) {
        case 'OPEN':
          stats.openCircuits++;
          break;
        case 'CLOSED':
          stats.closedCircuits++;
          break;
        case 'HALF_OPEN':
          stats.halfOpenCircuits++;
          break;
      }
      
      stats.totalOpens += breaker.stats.circuitOpens;
      stats.totalCloses += breaker.stats.circuitCloses;
    }

    return stats;
  }

  /**
   * Update circuit breaker configuration
   */
  updateConfig(serviceName, newConfig) {
    const breaker = this.breakers.get(serviceName);
    if (!breaker) {
      this.initializeService(serviceName, newConfig);
      return;
    }

    breaker.config = { ...breaker.config, ...newConfig };
    logger.info(`Circuit breaker configuration updated for service: ${serviceName}`);
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.breakers.clear();
    logger.info('Circuit breaker cleanup completed');
  }
}

module.exports = CircuitBreaker;

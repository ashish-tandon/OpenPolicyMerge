const express = require('express');
const { body, query, validationResult } = require('express-validator');
const axios = require('axios');
const config = require('../config/config');
const logger = require('../utils/logger');
const { authenticateToken, optionalAuth } = require('../middleware/auth');
const cache = require('../database/cache');

const router = express.Router();

// Validation middleware
const validateBillId = [
  query('id').isMongoId().withMessage('Invalid bill ID format')
];

const validateBillSearch = [
  query('q').optional().isString().trim().isLength({ min: 1 }).withMessage('Search query must not be empty'),
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('status').optional().isIn(['introduced', 'in_committee', 'passed', 'failed', 'vetoed']).withMessage('Invalid status'),
  query('session').optional().isString().trim().isLength({ min: 1 }).withMessage('Session must not be empty'),
  query('sponsor').optional().isString().trim().isLength({ min: 1 }).withMessage('Sponsor must not be empty')
];

// GET /api/mobile/v1/bills - Get bills with pagination and filters
router.get('/', validateBillSearch, optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const {
      q = '',
      page = 1,
      limit = 20,
      status,
      session,
      sponsor,
      sort = 'introduced_date',
      order = 'desc'
    } = req.query;

    // Build cache key
    const cacheKey = `bills:${q}:${page}:${limit}:${status}:${session}:${sponsor}:${sort}:${order}`;
    
    // Try to get from cache first
    const cachedData = await cache.get(cacheKey);
    if (cachedData) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedData,
        source: 'cache'
      });
    }

    // Build query parameters for external API
    const queryParams = {
      page,
      limit,
      sort,
      order
    };

    if (q) queryParams.q = q;
    if (status) queryParams.status = status;
    if (session) queryParams.session = session;
    if (sponsor) queryParams.sponsor = sponsor;

    // Call external bills API
    const response = await axios.get(`${config.services.dataService.url}/api/bills`, {
      params: queryParams,
      timeout: config.services.dataService.timeout
    });

    const billsData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, billsData, 300);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's tracking status, voting history, etc.
      billsData.bills = billsData.bills.map(bill => ({
        ...bill,
        userTracking: false, // TODO: Get from user's tracking list
        userVote: null // TODO: Get from user's voting history
      }));
    }

    res.json({
      success: true,
      data: billsData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch bills',
        error: error.response.data?.message || 'External service error'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// GET /api/mobile/v1/bills/:id - Get specific bill details
router.get('/:id', validateBillId, optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;

    // Try to get from cache first
    const cacheKey = `bill:${id}`;
    const cachedBill = await cache.get(cacheKey);
    if (cachedBill) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedBill,
        source: 'cache'
      });
    }

    // Call external API for bill details
    const response = await axios.get(`${config.services.dataService.url}/api/bills/${id}`, {
      timeout: config.services.dataService.timeout
    });

    const billData = response.data;

    // Cache the response for 10 minutes
    await cache.set(cacheKey, billData, 600);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's tracking status, voting history, etc.
      billData.userTracking = false;
      billData.userVote = null;
    }

    res.json({
      success: true,
      data: billData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Bill not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch bill',
        error: error.response.data?.message || 'External service error'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// GET /api/mobile/v1/bills/:id/votes - Get bill voting history
router.get('/:id/votes', validateBillId, optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const { page = 1, limit = 50 } = req.query;

    // Try to get from cache first
    const cacheKey = `bill:${id}:votes:${page}:${limit}`;
    const cachedVotes = await cache.get(cacheKey);
    if (cachedVotes) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedVotes,
        source: 'cache'
      });
    }

    // Call external API for bill votes
    const response = await axios.get(`${config.services.dataService.url}/api/bills/${id}/votes`, {
      params: { page, limit },
      timeout: config.services.dataService.timeout
    });

    const votesData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, votesData, 300);

    res.json({
      success: true,
      data: votesData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Bill not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch bill votes',
        error: error.response.data?.message || 'External service error'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// GET /api/mobile/v1/bills/:id/amendments - Get bill amendments
router.get('/:id/amendments', validateBillId, optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const { page = 1, limit = 50 } = req.query;

    // Try to get from cache first
    const cacheKey = `bill:${id}:amendments:${page}:${limit}`;
    const cachedAmendments = await cache.get(cacheKey);
    if (cachedAmendments) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedAmendments,
        source: 'cache'
      });
    }

    // Call external API for bill amendments
    const response = await axios.get(`${config.services.dataService.url}/api/bills/${id}/amendments`, {
      params: { page, limit },
      timeout: config.services.dataService.timeout
    });

    const amendmentsData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, amendmentsData, 300);

    res.json({
      success: true,
      data: amendmentsData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Bill not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch bill amendments',
        error: error.response.data?.message || 'External service error'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// GET /api/mobile/v1/bills/:id/timeline - Get bill timeline
router.get('/:id/timeline', validateBillId, optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;

    // Try to get from cache first
    const cacheKey = `bill:${id}:timeline`;
    const cachedTimeline = await cache.get(cacheKey);
    if (cachedTimeline) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedTimeline,
        source: 'cache'
      });
    }

    // Call external API for bill timeline
    const response = await axios.get(`${config.services.dataService.url}/api/bills/${id}/timeline`, {
      timeout: config.services.dataService.timeout
    });

    const timelineData = response.data;

    // Cache the response for 10 minutes
    await cache.set(cacheKey, timelineData, 600);

    res.json({
      success: true,
      data: timelineData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Bill not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch bill timeline',
        error: error.response.data?.message || 'External service error'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// POST /api/mobile/v1/bills/:id/track - Track a bill (authenticated only)
router.post('/:id/track', validateBillId, authenticateToken, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const { userId } = req.user;

    // TODO: Implement bill tracking in user's profile
    // This would typically involve:
    // 1. Adding bill to user's tracking list
    // 2. Setting up notifications
    // 3. Storing tracking preferences

    logger.logSecurity('bill_tracked', {
      userId,
      billId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Bill tracked successfully',
      data: {
        billId: id,
        tracked: true,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.logError(error, req);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

// DELETE /api/mobile/v1/bills/:id/track - Untrack a bill (authenticated only)
router.delete('/:id/track', validateBillId, authenticateToken, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const { userId } = req.user;

    // TODO: Implement bill untracking in user's profile
    // This would typically involve:
    // 1. Removing bill from user's tracking list
    // 2. Stopping notifications
    // 3. Cleaning up tracking preferences

    logger.logSecurity('bill_untracked', {
      userId,
      billId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Bill untracked successfully',
      data: {
        billId: id,
        tracked: false,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.logError(error, req);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: config.server.env === 'development' ? error.message : undefined
    });
  }
});

module.exports = router;

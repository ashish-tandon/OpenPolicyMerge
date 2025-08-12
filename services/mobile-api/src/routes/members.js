const express = require('express');
const { query, validationResult } = require('express-validator');
const axios = require('axios');
const config = require('../config/config');
const logger = require('../utils/logger');
const { authenticateToken, optionalAuth } = require('../middleware/auth');
const cache = require('../database/cache');

const router = express.Router();

// Validation middleware
const validateMemberId = [
  query('id').isMongoId().withMessage('Invalid member ID format')
];

const validateMemberSearch = [
  query('q').optional().isString().trim().isLength({ min: 1 }).withMessage('Search query must not be empty'),
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('party').optional().isString().trim().isLength({ min: 1 }).withMessage('Party must not be empty'),
  query('province').optional().isString().trim().isLength({ min: 1 }).withMessage('Province must not be empty'),
  query('riding').optional().isString().trim().isLength({ min: 1 }).withMessage('Riding must not be empty'),
  query('status').optional().isIn(['active', 'former', 'all']).withMessage('Invalid status')
];

// GET /api/mobile/v1/members - Get members with pagination and filters
router.get('/', validateMemberSearch, optionalAuth, async (req, res) => {
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
      party,
      province,
      riding,
      status = 'active',
      sort = 'name',
      order = 'asc'
    } = req.query;

    // Build cache key
    const cacheKey = `members:${q}:${page}:${limit}:${party}:${province}:${riding}:${status}:${sort}:${order}`;
    
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
      order,
      status
    };

    if (q) queryParams.q = q;
    if (party) queryParams.party = party;
    if (province) queryParams.province = province;
    if (riding) queryParams.riding = riding;

    // Call external members API
    const response = await axios.get(`${config.services.dataService.url}/api/members`, {
      params: queryParams,
      timeout: config.services.dataService.timeout
    });

    const membersData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, membersData, 300);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's tracking status, contact history, etc.
      membersData.members = membersData.members.map(member => ({
        ...member,
        userTracking: false, // TODO: Get from user's tracking list
        userContacted: false // TODO: Get from user's contact history
      }));
    }

    res.json({
      success: true,
      data: membersData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch members',
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

// GET /api/mobile/v1/members/:id - Get specific member details
router.get('/:id', validateMemberId, optionalAuth, async (req, res) => {
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
    const cacheKey = `member:${id}`;
    const cachedMember = await cache.get(cacheKey);
    if (cachedMember) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedMember,
        source: 'cache'
      });
    }

    // Call external API for member details
    const response = await axios.get(`${config.services.dataService.url}/api/members/${id}`, {
      timeout: config.services.dataService.timeout
    });

    const memberData = response.data;

    // Cache the response for 10 minutes
    await cache.set(cacheKey, memberData, 600);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's tracking status, contact history, etc.
      memberData.userTracking = false;
      memberData.userContacted = false;
    }

    res.json({
      success: true,
      data: memberData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Member not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch member',
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

// GET /api/mobile/v1/members/:id/voting-record - Get member voting record
router.get('/:id/voting-record', validateMemberId, optionalAuth, async (req, res) => {
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
    const { page = 1, limit = 50, session } = req.query;

    // Try to get from cache first
    const cacheKey = `member:${id}:voting:${page}:${limit}:${session || 'all'}`;
    const cachedVoting = await cache.get(cacheKey);
    if (cachedVoting) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedVoting,
        source: 'cache'
      });
    }

    // Build query parameters
    const queryParams = { page, limit };
    if (session) queryParams.session = session;

    // Call external API for member voting record
    const response = await axios.get(`${config.services.dataService.url}/api/members/${id}/voting-record`, {
      params: queryParams,
      timeout: config.services.dataService.timeout
    });

    const votingData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, votingData, 300);

    res.json({
      success: true,
      data: votingData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Member not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch voting record',
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

// GET /api/mobile/v1/members/:id/bills - Get member's sponsored bills
router.get('/:id/bills', validateMemberId, optionalAuth, async (req, res) => {
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
    const { page = 1, limit = 50, status } = req.query;

    // Try to get from cache first
    const cacheKey = `member:${id}:bills:${page}:${limit}:${status || 'all'}`;
    const cachedBills = await cache.get(cacheKey);
    if (cachedBills) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedBills,
        source: 'cache'
      });
    }

    // Build query parameters
    const queryParams = { page, limit };
    if (status) queryParams.status = status;

    // Call external API for member's bills
    const response = await axios.get(`${config.services.dataService.url}/api/members/${id}/bills`, {
      params: queryParams,
      timeout: config.services.dataService.timeout
    });

    const billsData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, billsData, 300);

    res.json({
      success: true,
      data: billsData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Member not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch member bills',
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

// GET /api/mobile/v1/members/:id/committees - Get member's committee memberships
router.get('/:id/committees', validateMemberId, optionalAuth, async (req, res) => {
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
    const cacheKey = `member:${id}:committees`;
    const cachedCommittees = await cache.get(cacheKey);
    if (cachedCommittees) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedCommittees,
        source: 'cache'
      });
    }

    // Call external API for member's committees
    const response = await axios.get(`${config.services.dataService.url}/api/members/${id}/committees`, {
      timeout: config.services.dataService.timeout
    });

    const committeesData = response.data;

    // Cache the response for 10 minutes
    await cache.set(cacheKey, committeesData, 600);

    res.json({
      success: true,
      data: committeesData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Member not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch member committees',
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

// GET /api/mobile/v1/members/:id/contact - Get member contact information
router.get('/:id/contact', validateMemberId, optionalAuth, async (req, res) => {
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
    const cacheKey = `member:${id}:contact`;
    const cachedContact = await cache.get(cacheKey);
    if (cachedContact) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedContact,
        source: 'cache'
      });
    }

    // Call external API for member contact info
    const response = await axios.get(`${config.services.dataService.url}/api/members/${id}/contact`, {
      timeout: config.services.dataService.timeout
    });

    const contactData = response.data;

    // Cache the response for 30 minutes (contact info changes less frequently)
    await cache.set(cacheKey, contactData, 1800);

    res.json({
      success: true,
      data: contactData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response?.status === 404) {
      return res.status(404).json({
        success: false,
        message: 'Member not found'
      });
    }

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch contact information',
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

// GET /api/mobile/v1/members/parties - Get all political parties
router.get('/parties/list', optionalAuth, async (req, res) => {
  try {
    // Try to get from cache first
    const cacheKey = 'members:parties:list';
    const cachedParties = await cache.get(cacheKey);
    if (cachedParties) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedParties,
        source: 'cache'
      });
    }

    // Call external API for parties list
    const response = await axios.get(`${config.services.dataService.url}/api/members/parties`, {
      timeout: config.services.dataService.timeout
    });

    const partiesData = response.data;

    // Cache the response for 1 hour (parties list changes very rarely)
    await cache.set(cacheKey, partiesData, 3600);

    res.json({
      success: true,
      data: partiesData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch parties',
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

// GET /api/mobile/v1/members/provinces - Get all provinces
router.get('/provinces/list', optionalAuth, async (req, res) => {
  try {
    // Try to get from cache first
    const cacheKey = 'members:provinces:list';
    const cachedProvinces = await cache.get(cacheKey);
    if (cachedProvinces) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedProvinces,
        source: 'cache'
      });
    }

    // Call external API for provinces list
    const response = await axios.get(`${config.services.dataService.url}/api/members/provinces`, {
      timeout: config.services.dataService.timeout
    });

    const provincesData = response.data;

    // Cache the response for 1 hour (provinces list changes very rarely)
    await cache.set(cacheKey, provincesData, 3600);

    res.json({
      success: true,
      data: provincesData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to fetch provinces',
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

// POST /api/mobile/v1/members/:id/track - Track a member (authenticated only)
router.post('/:id/track', validateMemberId, authenticateToken, async (req, res) => {
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

    // TODO: Implement member tracking in user's profile
    // This would typically involve:
    // 1. Adding member to user's tracking list
    // 2. Setting up notifications for member activities
    // 3. Storing tracking preferences

    logger.logSecurity('member_tracked', {
      userId,
      memberId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Member tracked successfully',
      data: {
        memberId: id,
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

// DELETE /api/mobile/v1/members/:id/track - Untrack a member (authenticated only)
router.delete('/:id/track', validateMemberId, authenticateToken, async (req, res) => {
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

    // TODO: Implement member untracking in user's profile
    // This would typically involve:
    // 1. Removing member from user's tracking list
    // 2. Stopping notifications for member activities
    // 3. Cleaning up tracking preferences

    logger.logSecurity('member_untracked', {
      userId,
      memberId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Member untracked successfully',
      data: {
        memberId: id,
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

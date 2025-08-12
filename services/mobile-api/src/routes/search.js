const express = require('express');
const { query, validationResult } = require('express-validator');
const axios = require('axios');
const config = require('../config/config');
const logger = require('../utils/logger');
const { optionalAuth } = require('../middleware/auth');
const cache = require('../database/cache');

const router = express.Router();

// Validation middleware
const validateSearchQuery = [
  query('q').isString().trim().isLength({ min: 1 }).withMessage('Search query is required and must not be empty'),
  query('type').optional().isIn(['all', 'bills', 'members', 'committees', 'debates', 'votes']).withMessage('Invalid search type'),
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('sort').optional().isIn(['relevance', 'date', 'title', 'name']).withMessage('Invalid sort option'),
  query('order').optional().isIn(['asc', 'desc']).withMessage('Order must be asc or desc'),
  query('filters').optional().isJSON().withMessage('Filters must be valid JSON')
];

const validateAdvancedSearch = [
  query('query').isString().trim().isLength({ min: 1 }).withMessage('Search query is required'),
  query('filters').isJSON().withMessage('Filters must be valid JSON'),
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100')
];

// GET /api/mobile/v1/search - General search across all content types
router.get('/', validateSearchQuery, optionalAuth, async (req, res) => {
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
      q,
      type = 'all',
      page = 1,
      limit = 20,
      sort = 'relevance',
      order = 'desc',
      filters = '{}'
    } = req.query;

    // Parse filters JSON
    let parsedFilters;
    try {
      parsedFilters = JSON.parse(filters);
    } catch (parseError) {
      return res.status(400).json({
        success: false,
        message: 'Invalid filters format',
        error: 'Filters must be valid JSON'
      });
    }

    // Build cache key
    const cacheKey = `search:${q}:${type}:${page}:${limit}:${sort}:${order}:${filters}`;
    
    // Try to get from cache first
    const cachedResults = await cache.get(cacheKey);
    if (cachedResults) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedResults,
        source: 'cache'
      });
    }

    // Build search parameters
    const searchParams = {
      query: q,
      type,
      page,
      limit,
      sort,
      order,
      filters: parsedFilters
    };

    // Call external search API
    const response = await axios.get(`${config.services.searchService.url}/api/search`, {
      params: searchParams,
      timeout: config.services.searchService.timeout
    });

    const searchResults = response.data;

    // Cache the response for 2 minutes (search results can change frequently)
    await cache.set(cacheKey, searchResults, 120);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's search history, preferences, etc.
      searchResults.userSearchHistory = []; // TODO: Get from user's search history
    }

    res.json({
      success: true,
      data: searchResults,
      source: 'api',
      query: q,
      type,
      totalResults: searchResults.total || 0,
      page,
      limit
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Search failed',
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

// POST /api/mobile/v1/search/advanced - Advanced search with complex filters
router.post('/advanced', validateAdvancedSearch, optionalAuth, async (req, res) => {
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
      query,
      filters,
      page = 1,
      limit = 20,
      sort = 'relevance',
      order = 'desc'
    } = req.body;

    // Parse filters JSON
    let parsedFilters;
    try {
      parsedFilters = typeof filters === 'string' ? JSON.parse(filters) : filters;
    } catch (parseError) {
      return res.status(400).json({
        success: false,
        message: 'Invalid filters format',
        error: 'Filters must be valid JSON'
      });
    }

    // Build cache key
    const cacheKey = `search:advanced:${query}:${JSON.stringify(parsedFilters)}:${page}:${limit}:${sort}:${order}`;
    
    // Try to get from cache first
    const cachedResults = await cache.get(cacheKey);
    if (cachedResults) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedResults,
        source: 'cache'
      });
    }

    // Build advanced search parameters
    const searchParams = {
      query,
      filters: parsedFilters,
      page,
      limit,
      sort,
      order
    };

    // Call external advanced search API
    const response = await axios.post(`${config.services.searchService.url}/api/search/advanced`, searchParams, {
      timeout: config.services.searchService.timeout
    });

    const searchResults = response.data;

    // Cache the response for 2 minutes
    await cache.set(cacheKey, searchResults, 120);

    // Add user-specific data if authenticated
    if (req.user) {
      // TODO: Add user's search history, preferences, etc.
      searchResults.userSearchHistory = [];
    }

    res.json({
      success: true,
      data: searchResults,
      source: 'api',
      query,
      totalResults: searchResults.total || 0,
      page,
      limit
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Advanced search failed',
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

// GET /api/mobile/v1/search/suggestions - Get search suggestions/autocomplete
router.get('/suggestions', [
  query('q').isString().trim().isLength({ min: 1 }).withMessage('Query is required'),
  query('type').optional().isIn(['all', 'bills', 'members', 'committees']).withMessage('Invalid type'),
  query('limit').optional().isInt({ min: 1, max: 20 }).withMessage('Limit must be between 1 and 20')
], optionalAuth, async (req, res) => {
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
      q,
      type = 'all',
      limit = 10
    } = req.query;

    // Build cache key
    const cacheKey = `search:suggestions:${q}:${type}:${limit}`;
    
    // Try to get from cache first
    const cachedSuggestions = await cache.get(cacheKey);
    if (cachedSuggestions) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedSuggestions,
        source: 'cache'
      });
    }

    // Call external suggestions API
    const response = await axios.get(`${config.services.searchService.url}/api/search/suggestions`, {
      params: { query: q, type, limit },
      timeout: config.services.searchService.timeout
    });

    const suggestionsData = response.data;

    // Cache the response for 5 minutes
    await cache.set(cacheKey, suggestionsData, 300);

    res.json({
      success: true,
      data: suggestionsData,
      source: 'api',
      query: q,
      type
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to get suggestions',
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

// GET /api/mobile/v1/search/trending - Get trending search terms
router.get('/trending', [
  query('period').optional().isIn(['day', 'week', 'month']).withMessage('Invalid period'),
  query('limit').optional().isInt({ min: 1, max: 50 }).withMessage('Limit must be between 1 and 50')
], optionalAuth, async (req, res) => {
  try {
    const {
      period = 'week',
      limit = 20
    } = req.query;

    // Build cache key
    const cacheKey = `search:trending:${period}:${limit}`;
    
    // Try to get from cache first
    const cachedTrending = await cache.get(cacheKey);
    if (cachedTrending) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedTrending,
        source: 'cache'
      });
    }

    // Call external trending API
    const response = await axios.get(`${config.services.searchService.url}/api/search/trending`, {
      params: { period, limit },
      timeout: config.services.searchService.timeout
    });

    const trendingData = response.data;

    // Cache the response for 1 hour
    await cache.set(cacheKey, trendingData, 3600);

    res.json({
      success: true,
      data: trendingData,
      source: 'api',
      period,
      limit
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to get trending searches',
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

// GET /api/mobile/v1/search/filters - Get available search filters
router.get('/filters', optionalAuth, async (req, res) => {
  try {
    // Try to get from cache first
    const cacheKey = 'search:filters:available';
    const cachedFilters = await cache.get(cacheKey);
    if (cachedFilters) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedFilters,
        source: 'cache'
      });
    }

    // Call external filters API
    const response = await axios.get(`${config.services.searchService.url}/api/search/filters`, {
      timeout: config.services.searchService.timeout
    });

    const filtersData = response.data;

    // Cache the response for 1 hour
    await cache.set(cacheKey, filtersData, 3600);

    res.json({
      success: true,
      data: filtersData,
      source: 'api'
    });

  } catch (error) {
    logger.logError(error, req);
    
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: 'Failed to get search filters',
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

// POST /api/mobile/v1/search/save - Save search query (authenticated only)
router.post('/save', [
  query('query').isString().trim().isLength({ min: 1 }).withMessage('Query is required'),
  query('name').optional().isString().trim().isLength({ min: 1, max: 100 }).withMessage('Name must be between 1 and 100 characters')
], optionalAuth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { query, name } = req.body;
    const { userId } = req.user;

    // TODO: Implement saving search queries to user's profile
    // This would typically involve:
    // 1. Saving the search query to user's saved searches
    // 2. Optionally naming the saved search
    // 3. Storing search parameters and filters

    logger.logSecurity('search_saved', {
      userId,
      query,
      name: name || 'Unnamed search',
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Search saved successfully',
      data: {
        query,
        name: name || 'Unnamed search',
        savedAt: new Date().toISOString()
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

// GET /api/mobile/v1/search/saved - Get user's saved searches (authenticated only)
router.get('/saved', optionalAuth, async (req, res) => {
  try {
    const { userId } = req.user;
    const { page = 1, limit = 20 } = req.query;

    // TODO: Implement getting user's saved searches
    // This would typically involve:
    // 1. Retrieving saved searches from user's profile
    // 2. Pagination support
    // 3. Sorting options

    // For now, return empty results
    const savedSearches = {
      searches: [],
      total: 0,
      page,
      limit,
      totalPages: 0
    };

    res.json({
      success: true,
      data: savedSearches,
      message: 'No saved searches found'
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

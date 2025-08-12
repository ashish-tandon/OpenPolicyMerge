const express = require('express');
const { body, query, validationResult } = require('express-validator');
const config = require('../config/config');
const logger = require('../utils/logger');
const { authenticateToken } = require('../middleware/auth');
const cache = require('../database/cache');

const router = express.Router();

// Validation middleware
const validateNotificationId = [
  query('id').isMongoId().withMessage('Invalid notification ID format')
];

const validateNotificationPreferences = [
  body('email').optional().isBoolean().withMessage('Email must be a boolean'),
  body('push').optional().isBoolean().withMessage('Push must be a boolean'),
  body('sms').optional().isBoolean().withMessage('SMS must be a boolean'),
  body('types').optional().isArray().withMessage('Types must be an array'),
  body('types.*').optional().isIn(['bills', 'members', 'votes', 'committees', 'debates', 'general']).withMessage('Invalid notification type')
];

// GET /api/mobile/v1/notifications - Get user's notifications
router.get('/', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;
    const { page = 1, limit = 20, status = 'all', type = 'all' } = req.query;

    // Validate query parameters
    if (page < 1 || limit < 1 || limit > 100) {
      return res.status(400).json({
        success: false,
        message: 'Invalid pagination parameters'
      });
    }

    if (!['all', 'unread', 'read'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid status parameter'
      });
    }

    if (!['all', 'bills', 'members', 'votes', 'committees', 'debates', 'general'].includes(type)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid type parameter'
      });
    }

    // Build cache key
    const cacheKey = `notifications:${userId}:${page}:${limit}:${status}:${type}`;
    
    // Try to get from cache first
    const cachedNotifications = await cache.get(cacheKey);
    if (cachedNotifications) {
      logger.logCache('get', cacheKey, true, 0);
      return res.json({
        success: true,
        data: cachedNotifications,
        source: 'cache'
      });
    }

    // TODO: Implement getting notifications from database
    // This would typically involve:
    // 1. Querying notifications collection for user
    // 2. Applying filters (status, type)
    // 3. Pagination
    // 4. Sorting by creation date

    // For now, return mock data
    const mockNotifications = {
      notifications: [
        {
          id: '1',
          userId,
          type: 'bills',
          title: 'New Bill Introduced',
          message: 'Bill C-123 has been introduced in the House of Commons',
          data: {
            billId: 'bill-123',
            billTitle: 'An Act to amend the Criminal Code',
            sponsor: 'John Smith'
          },
          status: 'unread',
          priority: 'medium',
          createdAt: new Date().toISOString(),
          readAt: null
        },
        {
          id: '2',
          userId,
          type: 'votes',
          title: 'Vote Result Available',
          message: 'The vote on Bill C-123 has been completed',
          data: {
            billId: 'bill-123',
            result: 'passed',
            voteCount: '156-142'
          },
          status: 'unread',
          priority: 'high',
          createdAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          readAt: null
        }
      ],
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: 2,
        totalPages: 1
      },
      filters: {
        status,
        type
      }
    };

    // Cache the response for 1 minute (notifications can change frequently)
    await cache.set(cacheKey, mockNotifications, 60);

    res.json({
      success: true,
      data: mockNotifications,
      source: 'mock'
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

// GET /api/mobile/v1/notifications/:id - Get specific notification
router.get('/:id', validateNotificationId, authenticateToken, async (req, res) => {
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

    // TODO: Implement getting specific notification from database
    // This would typically involve:
    // 1. Querying notifications collection by ID
    // 2. Verifying the notification belongs to the user
    // 3. Marking as read if requested

    // For now, return mock data
    const mockNotification = {
      id,
      userId,
      type: 'bills',
      title: 'New Bill Introduced',
      message: 'Bill C-123 has been introduced in the House of Commons',
      data: {
        billId: 'bill-123',
        billTitle: 'An Act to amend the Criminal Code',
        sponsor: 'John Smith',
        summary: 'This bill proposes amendments to the Criminal Code regarding...',
        status: 'introduced',
        session: '44th Parliament, 1st Session'
      },
      status: 'unread',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      readAt: null,
      actions: [
        {
          type: 'view_bill',
          label: 'View Bill Details',
          url: `/bills/${id}`
        },
        {
          type: 'track_bill',
          label: 'Track This Bill',
          url: `/bills/${id}/track`
        }
      ]
    };

    res.json({
      success: true,
      data: mockNotification,
      source: 'mock'
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

// PATCH /api/mobile/v1/notifications/:id/read - Mark notification as read
router.patch('/:id/read', validateNotificationId, authenticateToken, async (req, res) => {
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

    // TODO: Implement marking notification as read
    // This would typically involve:
    // 1. Updating notification status in database
    // 2. Setting readAt timestamp
    // 3. Updating user's unread count

    logger.logSecurity('notification_read', {
      userId,
      notificationId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Notification marked as read',
      data: {
        id,
        status: 'read',
        readAt: new Date().toISOString()
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

// PATCH /api/mobile/v1/notifications/:id/unread - Mark notification as unread
router.patch('/:id/unread', validateNotificationId, authenticateToken, async (req, res) => {
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

    // TODO: Implement marking notification as unread
    // This would typically involve:
    // 1. Updating notification status in database
    // 2. Clearing readAt timestamp
    // 3. Updating user's unread count

    logger.logSecurity('notification_unread', {
      userId,
      notificationId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Notification marked as unread',
      data: {
        id,
        status: 'unread',
        readAt: null
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

// PATCH /api/mobile/v1/notifications/read-all - Mark all notifications as read
router.patch('/read-all', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;
    const { type } = req.query;

    // Validate type parameter
    if (type && !['bills', 'members', 'votes', 'committees', 'debates', 'general'].includes(type)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid type parameter'
      });
    }

    // TODO: Implement marking all notifications as read
    // This would typically involve:
    // 1. Updating all unread notifications for user
    // 2. Setting readAt timestamp for each
    // 3. Updating user's unread count
    // 4. Optionally filtering by type

    logger.logSecurity('notifications_read_all', {
      userId,
      type: type || 'all',
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'All notifications marked as read',
      data: {
        type: type || 'all',
        readAt: new Date().toISOString()
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

// DELETE /api/mobile/v1/notifications/:id - Delete notification
router.delete('/:id', validateNotificationId, authenticateToken, async (req, res) => {
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

    // TODO: Implement deleting notification
    // This would typically involve:
    // 1. Verifying the notification belongs to the user
    // 2. Removing from database
    // 3. Updating user's notification count

    logger.logSecurity('notification_deleted', {
      userId,
      notificationId: id,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Notification deleted successfully',
      data: {
        id,
        deletedAt: new Date().toISOString()
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

// DELETE /api/mobile/v1/notifications/clear-all - Clear all notifications
router.delete('/clear-all', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;
    const { type } = req.query;

    // Validate type parameter
    if (type && !['bills', 'members', 'votes', 'committees', 'debates', 'general'].includes(type)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid type parameter'
      });
    }

    // TODO: Implement clearing all notifications
    // This would typically involve:
    // 1. Removing all notifications for user from database
    // 2. Optionally filtering by type
    // 3. Updating user's notification count

    logger.logSecurity('notifications_cleared_all', {
      userId,
      type: type || 'all',
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'All notifications cleared',
      data: {
        type: type || 'all',
        clearedAt: new Date().toISOString()
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

// GET /api/mobile/v1/notifications/preferences - Get user's notification preferences
router.get('/preferences', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;

    // TODO: Implement getting notification preferences
    // This would typically involve:
    // 1. Querying user's notification settings
    // 2. Returning current preferences

    // For now, return mock data
    const mockPreferences = {
      userId,
      email: {
        enabled: true,
        frequency: 'daily',
        types: ['bills', 'votes', 'general']
      },
      push: {
        enabled: true,
        types: ['bills', 'votes', 'committees']
      },
      sms: {
        enabled: false,
        types: []
      },
      general: {
        quietHours: {
          enabled: true,
          start: '22:00',
          end: '08:00'
        },
        timezone: 'America/Toronto'
      }
    };

    res.json({
      success: true,
      data: mockPreferences,
      source: 'mock'
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

// PUT /api/mobile/v1/notifications/preferences - Update user's notification preferences
router.put('/preferences', validateNotificationPreferences, authenticateToken, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userId } = req.user;
    const preferences = req.body;

    // TODO: Implement updating notification preferences
    // This would typically involve:
    // 1. Validating preference data
    // 2. Updating user's notification settings
    // 3. Storing in database
    // 4. Updating any active notification subscriptions

    logger.logSecurity('notification_preferences_updated', {
      userId,
      preferences,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Notification preferences updated successfully',
      data: {
        userId,
        updatedAt: new Date().toISOString(),
        preferences
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

// POST /api/mobile/v1/notifications/device-token - Register device for push notifications
router.post('/device-token', [
  body('token').isString().trim().isLength({ min: 1 }).withMessage('Device token is required'),
  body('platform').isIn(['ios', 'android', 'web']).withMessage('Platform must be ios, android, or web'),
  body('deviceId').optional().isString().trim().isLength({ min: 1 }).withMessage('Device ID must not be empty')
], authenticateToken, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userId } = req.user;
    const { token, platform, deviceId } = req.body;

    // TODO: Implement device token registration
    // This would typically involve:
    // 1. Adding device token to user's profile
    // 2. Storing platform and device information
    // 3. Setting up push notification subscriptions

    logger.logSecurity('device_token_registered', {
      userId,
      platform,
      deviceId: deviceId || 'unknown',
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Device token registered successfully',
      data: {
        userId,
        platform,
        deviceId: deviceId || 'unknown',
        registeredAt: new Date().toISOString()
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

// DELETE /api/mobile/v1/notifications/device-token - Unregister device for push notifications
router.delete('/device-token', [
  body('token').isString().trim().isLength({ min: 1 }).withMessage('Device token is required')
], authenticateToken, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userId } = req.user;
    const { token } = req.body;

    // TODO: Implement device token unregistration
    // This would typically involve:
    // 1. Removing device token from user's profile
    // 2. Cleaning up push notification subscriptions
    // 3. Updating user's device list

    logger.logSecurity('device_token_unregistered', {
      userId,
      token,
      ip: req.ip
    });

    res.json({
      success: true,
      message: 'Device token unregistered successfully',
      data: {
        userId,
        token,
        unregisteredAt: new Date().toISOString()
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

// GET /api/mobile/v1/notifications/unread-count - Get unread notification count
router.get('/unread-count', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;
    const { type } = req.query;

    // Validate type parameter
    if (type && !['bills', 'members', 'votes', 'committees', 'debates', 'general'].includes(type)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid type parameter'
      });
    }

    // TODO: Implement getting unread count
    // This would typically involve:
    // 1. Querying notifications collection for unread count
    // 2. Optionally filtering by type
    // 3. Returning count

    // For now, return mock data
    const mockCount = {
      total: 5,
      byType: {
        bills: 2,
        votes: 1,
        committees: 1,
        general: 1
      }
    };

    res.json({
      success: true,
      data: mockCount,
      source: 'mock'
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

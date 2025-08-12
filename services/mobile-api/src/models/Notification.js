const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  type: {
    type: String,
    enum: ['bills', 'members', 'votes', 'committees', 'debates', 'general'],
    required: true,
    index: true
  },
  title: {
    type: String,
    required: true,
    trim: true,
    maxlength: 200
  },
  message: {
    type: String,
    required: true,
    trim: true,
    maxlength: 1000
  },
  data: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  status: {
    type: String,
    enum: ['unread', 'read'],
    default: 'unread',
    index: true
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent'],
    default: 'medium'
  },
  actions: [{
    type: {
      type: String,
      enum: ['view_bill', 'view_member', 'track_bill', 'track_member', 'contact', 'custom']
    },
    label: String,
    url: String,
    data: mongoose.Schema.Types.Mixed
  }],
  readAt: {
    type: Date,
    default: null
  },
  expiresAt: {
    type: Date,
    default: null,
    index: true
  },
  metadata: {
    source: String,
    category: String,
    tags: [String],
    externalId: String
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
notificationSchema.index({ userId: 1, status: 1, createdAt: -1 });
notificationSchema.index({ userId: 1, type: 1, status: 1 });
notificationSchema.index({ createdAt: -1 });
notificationSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// Virtual for checking if notification is expired
notificationSchema.virtual('isExpired').get(function() {
  if (!this.expiresAt) return false;
  return new Date() > this.expiresAt;
});

// Virtual for notification age
notificationSchema.virtual('age').get(function() {
  return Date.now() - this.createdAt.getTime();
});

// Pre-save middleware
notificationSchema.pre('save', function(next) {
  // Auto-expire notifications after 30 days if not specified
  if (!this.expiresAt) {
    this.expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
  }
  
  // Update readAt when status changes to read
  if (this.isModified('status') && this.status === 'read' && !this.readAt) {
    this.readAt = new Date();
  }
  
  // Clear readAt when status changes to unread
  if (this.isModified('status') && this.status === 'unread') {
    this.readAt = null;
  }
  
  next();
});

// Instance methods
notificationSchema.methods.markAsRead = function() {
  this.status = 'read';
  this.readAt = new Date();
  return this.save();
};

notificationSchema.methods.markAsUnread = function() {
  this.status = 'unread';
  this.readAt = null;
  return this.save();
};

notificationSchema.methods.isActionable = function() {
  return this.actions && this.actions.length > 0;
};

// Static methods
notificationSchema.statics.findUnreadByUser = function(userId, options = {}) {
  const query = { userId, status: 'unread' };
  
  if (options.type) {
    query.type = options.type;
  }
  
  if (options.limit) {
    return this.find(query)
      .sort({ createdAt: -1 })
      .limit(options.limit);
  }
  
  return this.find(query).sort({ createdAt: -1 });
};

notificationSchema.statics.getUnreadCount = function(userId, type = null) {
  const query = { userId, status: 'unread' };
  
  if (type) {
    query.type = type;
  }
  
  return this.countDocuments(query);
};

notificationSchema.statics.markAllAsRead = function(userId, type = null) {
  const query = { userId, status: 'unread' };
  
  if (type) {
    query.type = type;
  }
  
  return this.updateMany(query, {
    status: 'read',
    readAt: new Date()
  });
};

notificationSchema.statics.cleanupExpired = function() {
  return this.deleteMany({
    expiresAt: { $lt: new Date() }
  });
};

// Create compound index for efficient queries
notificationSchema.index({ userId: 1, type: 1, status: 1, createdAt: -1 });

const Notification = mongoose.model('Notification', notificationSchema);

module.exports = Notification;

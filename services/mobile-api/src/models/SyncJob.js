const mongoose = require('mongoose');

const syncJobSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  type: {
    type: String,
    enum: ['bills', 'members', 'committees', 'votes', 'debates', 'all'],
    required: true,
    index: true
  },
  status: {
    type: String,
    enum: ['queued', 'in_progress', 'completed', 'failed', 'cancelled'],
    default: 'queued',
    index: true
  },
  priority: {
    type: String,
    enum: ['low', 'normal', 'high', 'urgent'],
    default: 'normal',
    index: true
  },
  progress: {
    current: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      default: 0
    },
    percentage: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    }
  },
  startedAt: {
    type: Date,
    default: null
  },
  completedAt: {
    type: Date,
    default: null
  },
  estimatedCompletion: {
    type: Date,
    default: null
  },
  currentOperation: {
    type: String,
    default: ''
  },
  logs: [{
    timestamp: {
      type: Date,
      required: true
    },
    level: {
      type: String,
      enum: ['debug', 'info', 'warn', 'error'],
      default: 'info'
    },
    message: {
      type: String,
      required: true
    },
    data: mongoose.Schema.Types.Mixed
  }],
  result: {
    totalItems: {
      type: Number,
      default: 0
    },
    newItems: {
      type: Number,
      default: 0
    },
    updatedItems: {
      type: Number,
      default: 0
    },
    deletedItems: {
      type: Number,
      default: 0
    },
    errors: [{
      message: String,
      timestamp: Date,
      retryCount: {
        type: Number,
        default: 0
      }
    }]
  },
  retryCount: {
    type: Number,
    default: 0,
    max: 3
  },
  maxRetries: {
    type: Number,
    default: 3
  },
  nextRetry: {
    type: Date,
    default: null
  },
  metadata: {
    source: String,
    filters: mongoose.Schema.Types.Mixed,
    externalApi: String,
    batchSize: Number,
    timeout: Number
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
syncJobSchema.index({ userId: 1, status: 1, createdAt: -1 });
syncJobSchema.index({ status: 1, priority: -1, createdAt: 1 });
syncJobSchema.index({ type: 1, status: 1 });
syncJobSchema.index({ nextRetry: 1 }, { expireAfterSeconds: 0 });

// Virtual for job duration
syncJobSchema.virtual('duration').get(function() {
  if (!this.startedAt) return 0;
  const endTime = this.completedAt || new Date();
  return endTime.getTime() - this.startedAt.getTime();
});

// Virtual for checking if job can be retried
syncJobSchema.virtual('canRetry').get(function() {
  return this.status === 'failed' && this.retryCount < this.maxRetries;
});

// Virtual for checking if job is stale
syncJobSchema.virtual('isStale').get(function() {
  if (this.status !== 'in_progress') return false;
  const staleThreshold = 30 * 60 * 1000; // 30 minutes
  return Date.now() - this.startedAt.getTime() > staleThreshold;
});

// Pre-save middleware
syncJobSchema.pre('save', function(next) {
  // Calculate percentage when progress changes
  if (this.isModified('progress.current') || this.isModified('progress.total')) {
    if (this.progress.total > 0) {
      this.progress.percentage = Math.round((this.progress.current / this.progress.total) * 100);
    } else {
      this.progress.percentage = 0;
    }
  }
  
  // Set startedAt when status changes to in_progress
  if (this.isModified('status') && this.status === 'in_progress' && !this.startedAt) {
    this.startedAt = new Date();
  }
  
  // Set completedAt when status changes to completed or failed
  if (this.isModified('status') && ['completed', 'failed'].includes(this.status) && !this.completedAt) {
    this.completedAt = new Date();
  }
  
  // Set nextRetry when status changes to failed
  if (this.isModified('status') && this.status === 'failed' && this.canRetry) {
    const retryDelay = Math.pow(2, this.retryCount) * 60 * 1000; // Exponential backoff
    this.nextRetry = new Date(Date.now() + retryDelay);
  }
  
  next();
});

// Instance methods
syncJobSchema.methods.start = function() {
  this.status = 'in_progress';
  this.startedAt = new Date();
  return this.save();
};

syncJobSchema.methods.complete = function(result = {}) {
  this.status = 'completed';
  this.completedAt = new Date();
  this.result = { ...this.result, ...result };
  return this.save();
};

syncJobSchema.methods.fail = function(error, retry = true) {
  this.status = 'failed';
  this.completedAt = new Date();
  
  // Add error to logs
  this.logs.push({
    timestamp: new Date(),
    level: 'error',
    message: error.message || error,
    data: error
  });
  
  // Add error to result
  this.result.errors.push({
    message: error.message || error,
    timestamp: new Date(),
    retryCount: this.retryCount
  });
  
  if (retry && this.canRetry) {
    this.retryCount += 1;
    const retryDelay = Math.pow(2, this.retryCount) * 60 * 1000;
    this.nextRetry = new Date(Date.now() + retryDelay);
  }
  
  return this.save();
};

syncJobSchema.methods.cancel = function() {
  this.status = 'cancelled';
  this.completedAt = new Date();
  return this.save();
};

syncJobSchema.methods.updateProgress = function(current, total, operation = '') {
  this.progress.current = current;
  this.progress.total = total;
  this.currentOperation = operation;
  
  if (total > 0) {
    this.progress.percentage = Math.round((current / total) * 100);
  }
  
  return this.save();
};

syncJobSchema.methods.addLog = function(level, message, data = null) {
  this.logs.push({
    timestamp: new Date(),
    level,
    message,
    data
  });
  
  // Keep only last 100 logs
  if (this.logs.length > 100) {
    this.logs = this.logs.slice(-100);
  }
  
  return this.save();
};

syncJobSchema.methods.retry = function() {
  if (!this.canRetry) {
    throw new Error('Job cannot be retried');
  }
  
  this.status = 'queued';
  this.startedAt = null;
  this.completedAt = null;
  this.progress = { current: 0, total: 0, percentage: 0 };
  this.currentOperation = '';
  this.nextRetry = null;
  
  return this.save();
};

// Static methods
syncJobSchema.statics.findByUser = function(userId, options = {}) {
  const query = { userId };
  
  if (options.status) {
    query.status = options.status;
  }
  
  if (options.type) {
    query.type = options.type;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50);
};

syncJobSchema.statics.findPending = function() {
  return this.find({
    status: { $in: ['queued', 'in_progress'] }
  }).sort({ priority: -1, createdAt: 1 });
};

syncJobSchema.statics.findStale = function() {
  const staleThreshold = 30 * 60 * 1000; // 30 minutes
  const cutoff = new Date(Date.now() - staleThreshold);
  
  return this.find({
    status: 'in_progress',
    startedAt: { $lt: cutoff }
  });
};

syncJobSchema.statics.findRetryable = function() {
  return this.find({
    status: 'failed',
    nextRetry: { $lte: new Date() },
    retryCount: { $lt: '$maxRetries' }
  });
};

syncJobSchema.statics.cleanupOldJobs = function(days = 30) {
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  
  return this.deleteMany({
    createdAt: { $lt: cutoff },
    status: { $in: ['completed', 'failed', 'cancelled'] }
  });
};

// Create compound indexes for efficient queries
syncJobSchema.index({ userId: 1, type: 1, status: 1, createdAt: -1 });
syncJobSchema.index({ status: 1, priority: -1, nextRetry: 1 });

const SyncJob = mongoose.model('SyncJob', syncJobSchema);

module.exports = SyncJob;

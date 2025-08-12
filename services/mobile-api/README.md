# OpenPolicy Mobile API Service

A high-performance, scalable Express.js API service designed specifically for mobile applications, providing real-time access to parliamentary data, user management, and synchronization capabilities.

## 🚀 Features

### Core Functionality
- **User Authentication & Management**: JWT-based authentication with refresh tokens
- **Parliamentary Data Access**: Bills, members, committees, votes, and debates
- **Advanced Search**: Full-text search with filters and suggestions
- **Real-time Notifications**: Push notifications for important updates
- **Data Synchronization**: Offline-first data sync with conflict resolution
- **Caching Layer**: Redis-based caching for improved performance

### Technical Features
- **RESTful API**: Clean, consistent API design
- **Input Validation**: Comprehensive request validation using express-validator
- **Rate Limiting**: API rate limiting to prevent abuse
- **Security**: Helmet.js security headers, CORS protection
- **Logging**: Structured logging with Winston
- **Health Checks**: Kubernetes-ready health check endpoints
- **Docker Support**: Containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Client    │    │   Admin Panel   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Mobile API Service     │
                    │      (Express.js)         │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│     MongoDB       │  │      Redis        │  │   External APIs   │
│   (User Data)     │  │    (Caching)      │  │  (Data Sources)   │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## 📋 Prerequisites

- Node.js 18+ 
- MongoDB 6.0+
- Redis 7.0+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   cd services/mobile-api
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start dependencies**
   ```bash
   # Start MongoDB and Redis locally, or use Docker
   docker-compose up -d mongodb redis
   ```

5. **Run the service**
   ```bash
   npm run dev
   ```

### Docker Deployment

1. **Build and start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f mobile-api
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment (development/production) | `development` |
| `PORT` | Server port | `8082` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/openpolicy_mobile` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `JWT_SECRET` | JWT signing secret | `your-super-secret-jwt-key-change-in-production` |
| `JWT_EXPIRES_IN` | JWT token expiry | `15m` |
| `RATE_LIMIT_MAX_REQUESTS` | Rate limit requests per window | `100` |

### Service URLs

| Service | Purpose | Default URL |
|---------|---------|-------------|
| `DATA_SERVICE_URL` | Parliamentary data source | `http://localhost:8000` |
| `SEARCH_SERVICE_URL` | Search functionality | `http://localhost:8001` |
| `ADMIN_SERVICE_URL` | Admin operations | `http://localhost:8002` |

## 📚 API Endpoints

### Authentication
- `POST /api/mobile/v1/auth/register` - User registration
- `POST /api/mobile/v1/auth/login` - User login
- `POST /api/mobile/v1/auth/refresh` - Refresh access token
- `POST /api/mobile/v1/auth/logout` - User logout
- `GET /api/mobile/v1/auth/me` - Get current user profile

### Bills
- `GET /api/mobile/v1/bills` - List bills with filters
- `GET /api/mobile/v1/bills/:id` - Get bill details
- `GET /api/mobile/v1/bills/:id/votes` - Get bill voting history
- `GET /api/mobile/v1/bills/:id/amendments` - Get bill amendments
- `GET /api/mobile/v1/bills/:id/timeline` - Get bill timeline
- `POST /api/mobile/v1/bills/:id/track` - Track a bill
- `DELETE /api/mobile/v1/bills/:id/track` - Untrack a bill

### Members
- `GET /api/mobile/v1/members` - List members with filters
- `GET /api/mobile/v1/members/:id` - Get member details
- `GET /api/mobile/v1/members/:id/voting-record` - Get voting record
- `GET /api/mobile/v1/members/:id/bills` - Get sponsored bills
- `GET /api/mobile/v1/members/:id/committees` - Get committee memberships
- `GET /api/mobile/v1/members/:id/contact` - Get contact information
- `GET /api/mobile/v1/members/parties/list` - List political parties
- `GET /api/mobile/v1/members/provinces/list` - List provinces

### Search
- `GET /api/mobile/v1/search` - General search
- `POST /api/mobile/v1/search/advanced` - Advanced search
- `GET /api/mobile/v1/search/suggestions` - Search suggestions
- `GET /api/mobile/v1/search/trending` - Trending searches
- `GET /api/mobile/v1/search/filters` - Available search filters
- `POST /api/mobile/v1/search/save` - Save search query
- `GET /api/mobile/v1/search/saved` - Get saved searches

### Notifications
- `GET /api/mobile/v1/notifications` - List user notifications
- `GET /api/mobile/v1/notifications/:id` - Get notification details
- `PATCH /api/mobile/v1/notifications/:id/read` - Mark as read
- `PATCH /api/mobile/v1/notifications/:id/unread` - Mark as unread
- `PATCH /api/mobile/v1/notifications/read-all` - Mark all as read
- `DELETE /api/mobile/v1/notifications/:id` - Delete notification
- `DELETE /api/mobile/v1/notifications/clear-all` - Clear all notifications
- `GET /api/mobile/v1/notifications/preferences` - Get preferences
- `PUT /api/mobile/v1/notifications/preferences` - Update preferences
- `POST /api/mobile/v1/notifications/device-token` - Register device
- `DELETE /api/mobile/v1/notifications/device-token` - Unregister device
- `GET /api/mobile/v1/notifications/unread-count` - Get unread count

### Data Synchronization
- `POST /api/mobile/v1/sync` - Sync specific data type
- `POST /api/mobile/v1/sync/batch` - Batch sync multiple types
- `GET /api/mobile/v1/sync/status` - Get sync status
- `POST /api/mobile/v1/sync/force` - Force immediate sync
- `GET /api/mobile/v1/sync/job/:jobId` - Get job status
- `DELETE /api/mobile/v1/sync/job/:jobId` - Cancel job
- `GET /api/mobile/v1/sync/schedule` - Get sync schedule
- `PUT /api/mobile/v1/sync/schedule` - Update sync schedule

### Health & Monitoring
- `GET /healthz` - Basic health check
- `GET /healthz/detailed` - Detailed health information
- `GET /readyz` - Kubernetes readiness probe
- `GET /livez` - Kubernetes liveness probe

## 🗄️ Database Models

### User Model
- Authentication credentials
- Profile information
- Mobile device tokens
- Preferences and settings

### Notification Model
- User notifications
- Read/unread status
- Expiration handling
- Action buttons

### SyncJob Model
- Background sync jobs
- Progress tracking
- Retry logic
- Job history

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt with configurable rounds
- **Rate Limiting**: API abuse prevention
- **Input Validation**: Comprehensive request validation
- **Security Headers**: Helmet.js security middleware
- **CORS Protection**: Configurable cross-origin policies
- **Request Logging**: Security event logging

## 📊 Performance Features

- **Redis Caching**: Intelligent caching layer
- **Database Indexing**: Optimized MongoDB queries
- **Connection Pooling**: Efficient database connections
- **Response Compression**: Gzip compression
- **Async Processing**: Non-blocking operations
- **Health Monitoring**: Performance metrics

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

### Run Linting
```bash
npm run lint
```

## 🚀 Deployment

### Production Build
```bash
npm run build
npm start
```

### Docker Production
```bash
docker build -t openpolicy-mobile-api .
docker run -p 8082:8082 openpolicy-mobile-api
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

## 📈 Monitoring & Logging

### Health Checks
- **Liveness Probe**: `/livez` - Service is running
- **Readiness Probe**: `/readyz` - Service is ready to receive traffic
- **Health Check**: `/healthz` - Basic service health

### Logging
- **Structured Logging**: JSON format with metadata
- **Log Levels**: Debug, Info, Warn, Error
- **Performance Logging**: Request timing and metrics
- **Security Logging**: Authentication and authorization events

### Metrics
- **Request Counts**: Total requests per endpoint
- **Response Times**: Average and percentile response times
- **Error Rates**: Error counts and types
- **Cache Hit Rates**: Redis cache performance

## 🔧 Development

### Project Structure
```
src/
├── config/          # Configuration management
├── database/        # Database connections and models
├── middleware/      # Express middleware
├── models/          # Mongoose models
├── routes/          # API route handlers
├── utils/           # Utility functions
└── server.js        # Main application entry point
```

### Adding New Routes
1. Create route file in `src/routes/`
2. Add validation middleware
3. Implement route handlers
4. Add to `server.js`
5. Update documentation

### Adding New Models
1. Create model file in `src/models/`
2. Define schema with validation
3. Add indexes for performance
4. Implement instance/static methods
5. Update related routes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints
- Check the health check endpoints

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- Core API functionality
- User authentication
- Parliamentary data access
- Notification system
- Data synchronization
- Comprehensive documentation

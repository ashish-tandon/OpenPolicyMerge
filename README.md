# OpenPolicy Merge - Unified Civic Data Platform

A comprehensive, modernized platform that unifies code from multiple existing repositories to create a unified civic data platform for Canadian legislative and policy data.

## 🎯 Project Overview

OpenPolicy Merge is a unified civic data platform that:

- **Unifies** code from multiple existing repositories
- **Inherits** the UI/UX from the OpenPolicy project
- **Incorporates** OpenParliament's historic features and database
- **Integrates** scrapers from opencivicdata and civic-scraper
- **Provides** robust APIs with automated test cases
- **Uses** PostgreSQL as the final database (latest stable version)
- **Is fully Dockerized** for easy deployment
- **Maintains transparency** of unused code in `/reference` folder

## 🏗️ Architecture

```
OpenPolicyMerge/
├── src/
│   ├── api/                 # Go API server (main entry point)
│   ├── backend/
│   │   ├── django/         # Django backend (parliamentary data)
│   │   └── laravel/        # Laravel backend (infrastructure)
│   ├── frontend/           # React web application
│   ├── mobile/             # React Native mobile app
│   ├── scrapers/           # Data scraping services
│   └── policies/           # OPA policy definitions
├── data/                   # Data storage and management
├── scripts/                # Data management scripts
├── external-repos/         # Original repository copies
├── reference/              # Unused/deprecated code
├── docker-compose.yml      # Multi-service orchestration
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd OpenPolicyMerge

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8080
# Django Admin: http://localhost:8001
# Laravel Admin: http://localhost:8002
# Swagger Docs: http://localhost:8080/docs
```

### Option 2: Manual Setup

```bash
# Prerequisites
- Go 1.21+
- Python 3.9+
- Node.js 18+
- PostgreSQL 16+
- Redis

# Setup Go API
cd src/api
go mod download
go run main.go

# Setup Django Backend
cd src/backend/django
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001

# Setup Laravel Backend
cd src/backend/laravel
composer install
php artisan migrate
php artisan serve --port=8002

# Setup Frontend
cd src/frontend
npm install
npm start
```

## 📊 Integrated Repositories

This project unifies code from the following repositories:

1. **OpenParliament** (`michaelmulley/openparliament`) - Canadian legislative data
2. **Open Policy Infrastructure** (`rarewox/open-policy-infra`) - Policy infrastructure
3. **Admin Open Policy** (`rarewox/admin-open-policy`) - Admin panel
4. **Open Policy App** (`rarewox/open-policy-app`) - Mobile application
5. **Open Policy Web** (`rarewox/open-policy-web`) - Web frontend
6. **Open Policy** (`rarewox/open-policy`) - Core policy engine
7. **Scrapers CA** (`opencivicdata/scrapers-ca`) - Canadian civic data scrapers
8. **Civic Scraper** (`biglocalnews/civic-scraper`) - Civic data scraping framework
9. **Represent Canada** (`opennorth/represent-canada`) - Canadian representatives API

## 🔌 API Endpoints

### Go API Server (Port 8080)

#### Health & Status
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - System status

#### Policy Evaluation
- `POST /api/v1/policy/evaluate` - Evaluate policies
- `POST /api/v1/policy/validate` - Validate policy rules

#### Data Scraping
- `POST /api/v1/scrape` - Trigger data scraping
- `GET /api/v1/scrape/{jurisdiction}` - Get scraping status by jurisdiction

#### Parliament Data
- `GET /api/v1/parliament/bills` - Get parliamentary bills
- `GET /api/v1/parliament/politicians` - Get politicians data
- `GET /api/v1/parliament/votes` - Get voting records

#### Civic Data
- `GET /api/v1/civic/meetings` - Get civic meetings
- `GET /api/v1/civic/documents` - Get civic documents

#### Represent Canada
- `GET /api/v1/represent/representatives` - Get representatives
- `GET /api/v1/represent/boundaries` - Get electoral boundaries
- `GET /api/v1/represent/postcodes` - Get postal codes
- `POST /api/v1/represent/point` - Find representatives by coordinates
- `GET /api/v1/represent/postcode/{postcode}` - Find representatives by postal code

#### Admin
- `GET /api/v1/admin/policies` - Manage policies
- `GET /api/v1/admin/users` - Manage users

### Django Backend (Port 8001)
- Parliamentary data management
- OpenParliament database integration
- Data scraping orchestration

### Laravel Backend (Port 8002)
- Infrastructure management
- Policy administration
- User management

## 🗄️ Database

### PostgreSQL with PostGIS
- **Version**: Latest stable (16+)
- **Extensions**: PostGIS for geographic data
- **Databases**:
  - `openparliament` - Parliamentary data
  - `represent` - Representatives data
  - `policy` - Policy management

### Data Sources
- **OpenParliament Database**: 6.5GB of Canadian legislative data
- **Represent Canada**: Electoral boundaries and representatives
- **Live Scraping**: Federal, provincial, and municipal data

## 🔧 Configuration

### Environment Variables
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=openparliament
DB_USER=postgres
DB_PASSWORD=password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
REPRESENT_API_KEY=your_api_key
OPENPARLIAMENT_API_KEY=your_api_key

# Data Directories
REPRESENT_DATA_DIR=/app/data
OPENPARLIAMENT_DATA_DIR=/app/data
```

## 🧪 Testing

### API Testing
```bash
# Run Go API tests
cd src/api
go test ./...

# Run Django tests
cd src/backend/django
python manage.py test

# Run Laravel tests
cd src/backend/laravel
php artisan test
```

### Coverage Target
- **API Test Coverage**: 90%+
- **Data Integrity Tests**: All endpoints
- **Error Handling Tests**: Comprehensive

## 📈 Monitoring

### Services
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Health Checks**: Automated monitoring

### Logging
- Structured logging across all services
- Error tracking and alerting
- Performance monitoring

## 🔒 Security

- JWT authentication
- Role-based access control
- API rate limiting
- Input validation and sanitization
- Secure database connections

## 🚀 Deployment

### Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f
```

### Development
```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d
```

## 📚 Documentation

**ALL documentation has been consolidated into ONE master document:**

### **📖 [MASTER OPENPOLICY PLATFORM GUIDE](docs/MASTER_OPENPOLICY_PLATFORM_GUIDE.md)**

**This is the SINGLE SOURCE OF TRUTH for everything:**
- ✅ **Current Status** - What's working and what's not
- ✅ **Architecture** - Complete system design  
- ✅ **Migration Plan** - Scraper migration strategy
- ✅ **Next Steps** - Clear direction forward
- ✅ **All Technical Details** - In one place

**NO MORE DOCUMENT CHAOS - USE ONLY THE MASTER GUIDE!**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenParliament**: For the extensive Canadian legislative database
- **OpenNorth**: For the Represent Canada API and data
- **OpenCivicData**: For the civic data scraping framework
- **Big Local News**: For the civic scraper infrastructure

---

**OpenPolicy Merge** - Unifying civic data for a more transparent democracy. 
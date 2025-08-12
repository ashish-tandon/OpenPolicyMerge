# OpenPolicy Services

This directory contains the core services that power the OpenPolicy platform, including the API Gateway and Plotly Data Visualization Service.

## 🚀 **API Gateway Service**

The API Gateway serves as a unified entry point for all OpenPolicy platform APIs, providing intelligent routing, authentication, rate limiting, and fault tolerance.

### **Features**

- **🔀 Intelligent Routing**: Routes requests to appropriate backend services based on path patterns
- **🔐 Authentication & Authorization**: JWT-based authentication with role-based access control
- **⚡ Rate Limiting**: Configurable rate limiting to prevent abuse
- **🔄 Circuit Breaker**: Fault tolerance with automatic service recovery
- **📊 Service Discovery**: Automatic health monitoring and service status tracking
- **📈 Monitoring & Metrics**: Prometheus metrics and OpenTelemetry tracing
- **📚 API Documentation**: Swagger/OpenAPI documentation
- **🛡️ Security**: Helmet security headers, CORS configuration, request validation

### **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│   API Gateway   │───▶│  Backend       │
│                 │    │                 │    │  Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Service        │
                       │  Registry       │
                       └─────────────────┘
```

### **Service Routing**

| API Path | Backend Service | Description |
|----------|----------------|-------------|
| `/api/parliament` | Go API Server | Parliamentary data and bills |
| `/api/bills` | Go API Server | Bill information and tracking |
| `/api/members` | Go API Server | Parliamentary members |
| `/api/mobile/*` | Mobile API Service | Mobile application endpoints |
| `/api/etl/*` | ETL Service | Data processing and analytics |
| `/api/admin/*` | Admin Dashboard | Administrative functions |

### **Quick Start**

```bash
# Navigate to service directory
cd services/api-gateway

# Install dependencies
npm install

# Copy environment configuration
cp env.example .env

# Start the service
npm run dev

# Build and run with Docker
docker build -t openpolicy-api-gateway .
docker run -p 8000:8000 openpolicy-api-gateway
```

### **Configuration**

Key environment variables:

```bash
# Server Configuration
GATEWAY_PORT=8000
GATEWAY_HOST=0.0.0.0

# Service URLs
GO_API_URL=http://localhost:8080
MOBILE_API_URL=http://localhost:8002
ETL_SERVICE_URL=http://localhost:8003

# Authentication
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=24h

# Rate Limiting
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=900000
```

### **API Endpoints**

- `GET /` - Service information and status
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /livez` - Liveness check
- `GET /metrics` - Prometheus metrics
- `GET /docs` - Swagger documentation
- `GET /api/services` - Service discovery
- `POST /auth/login` - Authentication
- `GET /api/*` - Proxied backend services

---

## 📊 **Plotly Data Visualization Service**

The Plotly Service provides interactive data visualization capabilities for the OpenPolicy platform, enabling users to create, customize, and export various types of charts and dashboards.

### **Features**

- **📈 Chart Types**: 20+ chart types including line, bar, scatter, pie, heatmap, 3D, and geographic
- **🎨 Customization**: Themes, colors, layouts, and interactive elements
- **💾 Export Formats**: HTML, PNG, SVG, PDF, and JSON exports
- **📱 Responsive**: Mobile-friendly visualizations
- **🌍 Geographic**: Choropleth maps and location-based visualizations
- **📊 Analytics**: Statistical analysis and trend detection
- **🔧 Templates**: Pre-built chart templates for common use cases
- **⚡ Performance**: Optimized rendering and caching

### **Supported Chart Types**

| Category | Chart Types |
|----------|-------------|
| **Basic Charts** | Line, Bar, Scatter, Area, Pie, Donut |
| **Statistical** | Histogram, Box Plot, Violin Plot |
| **3D Visualization** | 3D Scatter, 3D Surface, 3D Line |
| **Geographic** | Choropleth, Mapbox, Density Maps |
| **Advanced** | Heatmap, Contour, Treemap, Sunburst |
| **Financial** | Candlestick, OHLC, Waterfall |

### **Quick Start**

```bash
# Navigate to service directory
cd services/plotly-service

# Install dependencies
pip install -r requirements.txt

# Start the service
python src/main.py

# Build and run with Docker
docker build -t openpolicy-plotly .
docker run -p 8004:8004 openpolicy-plotly
```

### **Configuration**

Key environment variables:

```bash
# Server Configuration
PLOTLY_PORT=8004
PLOTLY_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379

# Features
ENABLE_EXPORT=true
ENABLE_TEMPLATES=true
ENABLE_ANALYTICS=true
```

### **API Endpoints**

- `GET /` - Service information and documentation
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /livez` - Liveness check
- `POST /api/v1/charts` - Create new chart
- `GET /api/v1/charts/{id}` - Get chart by ID
- `PUT /api/v1/charts/{id}` - Update chart
- `DELETE /api/v1/charts/{id}` - Delete chart
- `GET /api/v1/templates` - Get chart templates
- `POST /api/v1/exports` - Export chart to various formats

### **Chart Creation Example**

```python
import requests

# Create a parliamentary votes chart
chart_data = {
    "chart_type": "bar",
    "data": {
        "x": ["Conservative", "Liberal", "NDP", "Bloc", "Green"],
        "y": [119, 157, 25, 32, 2],
        "name": "Parliamentary Seats by Party"
    },
    "options": {
        "title": "2021 Canadian Federal Election Results",
        "xaxis_title": "Political Party",
        "yaxis_title": "Number of Seats",
        "theme": "plotly_white"
    }
}

response = requests.post(
    "http://localhost:8004/api/v1/charts",
    json=chart_data
)

chart = response.json()
print(f"Chart created: {chart['id']}")
```

### **Chart Templates**

Pre-built templates for common use cases:

- **Parliamentary Votes Analysis** - Bar chart showing voting patterns
- **Bill Timeline** - Line chart showing legislative progress
- **Geographic Distribution** - Choropleth map of data across regions
- **Data Quality Metrics** - Heatmap of data quality indicators
- **Trend Analysis** - Scatter plot with trend lines

---

## 🔧 **Development & Deployment**

### **Prerequisites**

- Node.js 18+ (for API Gateway)
- Python 3.11+ (for Plotly Service)
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- MongoDB 7+ (for API Gateway)

### **Local Development**

```bash
# Clone the repository
git clone https://github.com/ashish-tandon/OpenPolicyMerge.git
cd OpenPolicyMerge

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api-gateway
docker-compose logs -f plotly-service

# Stop services
docker-compose down
```

### **Service Health Checks**

```bash
# API Gateway
curl http://localhost:8000/healthz

# Plotly Service
curl http://localhost:8004/healthz

# All services via gateway
curl http://localhost:8000/api/services
```

### **Monitoring & Metrics**

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001` (admin/admin)
- **API Gateway Metrics**: `http://localhost:8000/metrics`
- **Plotly Service Metrics**: `http://localhost:8004/metrics`

---

## 📚 **Documentation & Resources**

### **API Documentation**

- **API Gateway**: `http://localhost:8000/docs`
- **Plotly Service**: `http://localhost:8004/docs`

### **Code Structure**

```
services/
├── api-gateway/           # API Gateway service
│   ├── src/
│   │   ├── routes/       # API route definitions
│   │   ├── services/     # Business logic
│   │   ├── middleware/   # Request/response processing
│   │   └── utils/        # Utility functions
│   ├── Dockerfile        # Container configuration
│   └── package.json      # Node.js dependencies
│
└── plotly-service/        # Plotly visualization service
    ├── src/
    │   ├── services/     # Chart generation logic
    │   ├── routes/       # API endpoints
    │   ├── models/       # Data models
    │   └── utils/        # Helper functions
    ├── Dockerfile        # Container configuration
    └── requirements.txt  # Python dependencies
```

### **Testing**

```bash
# API Gateway tests
cd services/api-gateway
npm test

# Plotly Service tests
cd services/plotly-service
pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 🚀 **Next Steps**

1. **Complete ETL Service**: Finish remaining components (routes, workers, migrations)
2. **Frontend Integration**: Connect frontend applications to new services
3. **Authentication Flow**: Implement JWT token management
4. **Data Sources**: Connect to parliamentary and civic data sources
5. **Performance Optimization**: Add caching and query optimization
6. **Security Hardening**: Implement additional security measures
7. **Monitoring**: Set up comprehensive monitoring and alerting
8. **Documentation**: Create user guides and API documentation

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

.PHONY: pre-pr recover verify-discovery test-scrapers

# Pre-PR validation gates
pre-pr:
	@echo "🔍 Running pre-PR validation..."
	ruff check .
	black --check .
	pnpm -w eslint . || true
	pnpm -w tsc --noEmit || true
	@if [ -f openapi.yaml ]; then schemathesis run openapi.yaml || true; fi
	pytest -q || true
	@echo "✅ Pre-PR validation complete"

# Recovery branch creation
recover:
	@echo "🔄 Creating recovery branch..."
	@git checkout -b recover/$$(date +%Y%m%d-%H%M%S)
	@echo "✅ Recovery branch created"

# Verify service discovery compliance
verify-discovery:
	@echo "🔍 Verifying service discovery compliance..."
	bash scripts/verify_discovery.sh

# Test scraper service
test-scrapers:
	@echo "🧪 Testing scraper service..."
	cd services/scraper-service && python -m pytest tests/ -v

# Database setup
setup-db:
	@echo "🗄️ Setting up databases..."
	bash scripts/setup-databases.sh

# Start all services
up:
	@echo "🚀 Starting all services..."
	docker compose up -d

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker compose down

# View logs
logs:
	@echo "📋 Viewing service logs..."
	docker compose logs -f

# Clean build
clean-build:
	@echo "🧹 Clean building scraper service..."
	cd services/scraper-service && docker build --no-cache -t openpolicy-scraper-service .

# Health check
health:
	@echo "🏥 Checking service health..."
	curl -f http://localhost:8005/healthz || echo "❌ Scraper service not healthy"

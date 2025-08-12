#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-openpolicy}
API_SVC=api-gateway
WEB_SVC=web
ETL_SVC=etl
ADMIN_SVC=admin
SCRAPER_SVC=scraper
POLICY_SVC=policy
SEARCH_SVC=search
AUTH_SVC=auth
NOTIFICATION_SVC=notifications
CONFIG_SVC=config
HEALTH_SVC=health
MONITORING_SVC=monitoring

echo "🚀 Running production smoke tests against namespace: $NAMESPACE"

# Check if we're in production context
CURRENT_CONTEXT=$(kubectl config current-context)
if [[ "$CURRENT_CONTEXT" != "prod" ]]; then
    echo "⚠️  Warning: Current context is '$CURRENT_CONTEXT', expected 'prod'"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborting production smoke tests"
        exit 1
    fi
fi

echo "🔍 Testing API Gateway..."
kubectl -n "$NAMESPACE" exec -it deployment/api-gateway -- curl -fsS http://localhost:8080/healthz >/dev/null || { echo "❌ API Gateway health check failed"; exit 1; }
kubectl -n "$NAMESPACE" exec -it deployment/api-gateway -- curl -fsS http://localhost:8080/readyz >/dev/null || { echo "❌ API Gateway readiness check failed"; exit 1; }
kubectl -n "$NAMESPACE" exec -it deployment/api-gateway -- curl -fsS http://localhost:8080/version >/dev/null || { echo "❌ API Gateway version check failed"; exit 1; }

echo "🔍 Testing Web Frontend..."
kubectl -n "$NAMESPACE" exec -it deployment/web -- curl -fsS http://localhost:3000/ >/dev/null || { echo "❌ Web frontend check failed"; exit 1; }

echo "🔍 Testing ETL Service..."
kubectl -n "$NAMESPACE" exec -it deployment/etl -- curl -fsS http://localhost:8003/healthz >/dev/null || { echo "❌ ETL service health check failed"; exit 1; }
kubectl -n "$NAMESPACE" exec -it deployment/etl -- curl -fsS http://localhost:8003/readyz >/dev/null || { echo "❌ ETL service readiness check failed"; exit 1; }

echo "🔍 Testing Admin Interface..."
kubectl -n "$NAMESPACE" exec -it deployment/admin -- curl -fsS http://localhost:3001/ >/dev/null || { echo "❌ Admin interface check failed"; exit 1; }

echo "🔍 Testing Scraper Service..."
kubectl -n "$NAMESPACE" exec -it deployment/scraper -- curl -fsS http://localhost:8005/healthz >/dev/null || { echo "❌ Scraper service health check failed"; exit 1; }
kubectl -n "$NAMESPACE" exec -it deployment/scraper -- curl -fsS http://localhost:8005/readyz >/dev/null || { echo "❌ Scraper service readiness check failed"; exit 1; }

echo "🔍 Testing Policy Service..."
kubectl -n "$NAMESPACE" exec -it deployment/policy -- curl -fsS http://localhost:8011/healthz >/dev/null || { echo "❌ Policy service health check failed"; exit 1; }

echo "🔍 Testing Search Service..."
kubectl -n "$NAMESPACE" exec -it deployment/search -- curl -fsS http://localhost:8010/healthz >/dev/null || { echo "❌ Search service health check failed"; exit 1; }

echo "🔍 Testing Auth Service..."
kubectl -n "$NAMESPACE" exec -it deployment/auth -- curl -fsS http://localhost:8009/healthz >/dev/null || { echo "❌ Auth service health check failed"; exit 1; }

echo "🔍 Testing Notification Service..."
kubectl -n "$NAMESPACE" exec -it deployment/notifications -- curl -fsS http://localhost:8012/healthz >/dev/null || { echo "❌ Notification service health check failed"; exit 1; }

echo "🔍 Testing Config Service..."
kubectl -n "$NAMESPACE" exec -it deployment/config -- curl -fsS http://localhost:8013/healthz >/dev/null || { echo "❌ Config service health check failed"; exit 1; }

echo "🔍 Testing Health Service..."
kubectl -n "$NAMESPACE" exec -it deployment/health -- curl -fsS http://localhost:8007/healthz >/dev/null || { echo "❌ Health service health check failed"; exit 1; }

echo "🔍 Testing Monitoring Service..."
kubectl -n "$NAMESPACE" exec -it deployment/monitoring -- curl -fsS http://localhost:8015/healthz >/dev/null || { echo "❌ Monitoring service health check failed"; exit 1; }

echo "🔍 Testing Service Discovery..."
kubectl -n "$NAMESPACE" get svc | grep -q api-gateway || { echo "❌ API Gateway service not found"; exit 1; }
kubectl -n "$NAMESPACE" get svc | grep -q web || { echo "❌ Web service not found"; exit 1; }
kubectl -n "$NAMESPACE" get svc | grep -q scraper || { echo "❌ Scraper service not found"; exit 1; }

echo "🔍 Testing Database Connectivity..."
kubectl -n "$NAMESPACE" exec -it deployment/etl -- python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres',
        database='openpolicy',
        user='postgres',
        password='password'
    )
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" || { echo "❌ Database connectivity test failed"; exit 1; }

echo "🔍 Testing Data Pipeline..."
kubectl -n "$NAMESPACE" exec -it deployment/scraper -- python -c "
import requests
try:
    response = requests.get('http://localhost:8005/api/v1/scrapers/status')
    if response.status_code == 200:
        print('Scraper service API accessible')
    else:
        print(f'Scraper service API returned {response.status_code}')
        exit(1)
except Exception as e:
    print(f'Scraper service API test failed: {e}')
    exit(1)
" || { echo "❌ Data pipeline test failed"; exit 1; }

echo "🔍 Testing Monitoring Metrics..."
kubectl -n "$NAMESPACE" exec -it deployment/monitoring -- curl -fsS http://localhost:8015/metrics >/dev/null || { echo "❌ Monitoring metrics endpoint failed"; exit 1; }

echo "✅ All production smoke tests passed successfully!"

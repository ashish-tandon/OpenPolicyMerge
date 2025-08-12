#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-openpolicy-dev}
API_SVC=api-gateway
WEB_SVC=web
ETL_SVC=etl
ADMIN_SVC=admin

echo "🚀 Running dev smoke tests against namespace: $NAMESPACE"

# Port-forward services locally for smoke tests
echo "📡 Setting up port forwarding..."

kubectl -n "$NAMESPACE" port-forward svc/$API_SVC 18080:80 >/tmp/api_pf.log 2>&1 &
API_PID=$!
kubectl -n "$NAMESPACE" port-forward svc/$WEB_SVC 13000:80 >/tmp/web_pf.log 2>&1 &
WEB_PID=$!
kubectl -n "$NAMESPACE" port-forward svc/$ETL_SVC 18090:80 >/tmp/etl_pf.log 2>&1 &
ETL_PID=$!
kubectl -n "$NAMESPACE" port-forward svc/$ADMIN_SVC 13001:80 >/tmp/admin_pf.log 2>&1 &
ADMIN_PID=$!

cleanup() { 
    echo "🧹 Cleaning up port forwards..."
    kill $API_PID $WEB_PID $ETL_PID $ADMIN_PID 2>/dev/null || true
}
trap cleanup EXIT

echo "⏳ Waiting for port forwards to establish..."
sleep 5

echo "🔍 Testing API Gateway..."
curl -fsS http://localhost:18080/healthz >/dev/null || { echo "❌ API Gateway health check failed"; exit 1; }
curl -fsS http://localhost:18080/readyz >/dev/null || { echo "❌ API Gateway readiness check failed"; exit 1; }
curl -fsS http://localhost:18080/version >/dev/null || { echo "❌ API Gateway version check failed"; exit 1; }
curl -fsS "http://localhost:18080/bills?page=1" >/dev/null || echo "⚠️  Bills endpoint not yet available"

echo "🔍 Testing Web Frontend..."
curl -fsS http://localhost:13000/ >/dev/null || { echo "❌ Web frontend check failed"; exit 1; }

echo "🔍 Testing ETL Service..."
curl -fsS http://localhost:18090/healthz >/dev/null || { echo "❌ ETL service health check failed"; exit 1; }
curl -fsS http://localhost:18090/readyz >/dev/null || { echo "❌ ETL service readiness check failed"; exit 1; }

echo "🔍 Testing Admin Interface..."
curl -fsS http://localhost:13001/ >/dev/null || { echo "❌ Admin interface check failed"; exit 1; }

echo "✅ All dev smoke tests passed successfully!"

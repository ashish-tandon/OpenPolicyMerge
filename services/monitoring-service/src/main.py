from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from .config import Config

app = FastAPI(title="Monitoring Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.get("/healthz")
async def health_check():
    REQUEST_COUNT.labels(method='GET', endpoint='/healthz').inc()
    return {"status": "ok"}

@app.get("/readyz")
async def readiness_check():
    REQUEST_COUNT.labels(method='GET', endpoint='/readyz').inc()
    return {"status": "ready"}

@app.get("/")
async def root():
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()
    return {"message": "Monitoring Service is running"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/status")
async def system_status():
    # TODO: Implement system status monitoring
    return {
        "status": "healthy",
        "services": {
            "etl": "healthy",
            "scraper": "healthy",
            "api-gateway": "healthy"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.SERVICE_PORT,
        reload=True,
        log_level="info"
    )

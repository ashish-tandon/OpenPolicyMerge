"""
OPA Service (Open Policy Agent)
Provides policy evaluation and management for the OpenPolicy platform
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any, List, Optional

from .config import get_settings
from .models import PolicyRequest, PolicyResponse, PolicyDefinition
from .policy_engine import PolicyEngine
from .database import get_database
from .auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting OPA Service...")
    # Initialize policy engine
    app.state.policy_engine = PolicyEngine()
    yield
    logger.info("Shutting down OPA Service...")

# Create FastAPI app
app = FastAPI(
    title="OPA Service",
    description="Open Policy Agent service for policy evaluation and management",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "opa-service",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check_alt():
    """Alternative health check endpoint"""
    return await health_check()

# Policy evaluation endpoint
@app.post("/api/v1/evaluate", response_model=PolicyResponse)
async def evaluate_policy(
    request: PolicyRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Evaluate a policy against input data"""
    try:
        result = await app.state.policy_engine.evaluate_policy(
            policy_id=request.policy_id,
            input_data=request.input_data,
            context=request.context
        )
        return PolicyResponse(
            decision=result["decision"],
            confidence=result["confidence"],
            explanation=result.get("explanation", ""),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Policy management endpoints
@app.get("/api/v1/policies", response_model=List[PolicyDefinition])
async def list_policies(
    current_user: Dict = Depends(get_current_user)
):
    """List all available policies"""
    try:
        policies = await app.state.policy_engine.list_policies()
        return policies
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/policies/{policy_id}", response_model=PolicyDefinition)
async def get_policy(
    policy_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a specific policy by ID"""
    try:
        policy = await app.state.policy_engine.get_policy(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/policies", response_model=PolicyDefinition)
async def create_policy(
    policy: PolicyDefinition,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new policy"""
    try:
        created_policy = await app.state.policy_engine.create_policy(policy)
        return created_policy
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/policies/{policy_id}", response_model=PolicyDefinition)
async def update_policy(
    policy_id: str,
    policy: PolicyDefinition,
    current_user: Dict = Depends(get_current_user)
):
    """Update an existing policy"""
    try:
        updated_policy = await app.state.policy_engine.update_policy(policy_id, policy)
        if not updated_policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return updated_policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete a policy"""
    try:
        success = await app.state.policy_engine.delete_policy(policy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"message": "Policy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Policy validation endpoint
@app.post("/api/v1/validate")
async def validate_policy(
    policy_content: str,
    current_user: Dict = Depends(get_current_user)
):
    """Validate policy syntax and structure"""
    try:
        is_valid = await app.state.policy_engine.validate_policy(policy_content)
        return {
            "valid": is_valid,
            "message": "Policy is valid" if is_valid else "Policy has syntax errors"
        }
    except Exception as e:
        logger.error(f"Policy validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    try:
        metrics = await app.state.policy_engine.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8181,
        reload=True,
        log_level="info"
    )

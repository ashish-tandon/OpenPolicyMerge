from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid
import json
import asyncio

from .policy_engine import PolicyEngine
from .service_client import ServiceClient
from .database import get_session
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class PolicyEvaluationRequest(BaseModel):
    policy_id: str = Field(..., description="ID of the policy to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for policy evaluation")
    user_id: Optional[str] = Field(None, description="User ID requesting evaluation")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class PolicyEvaluationResponse(BaseModel):
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    policy_id: str = Field(..., description="Policy ID that was evaluated")
    decision: str = Field(..., description="Policy decision (allow/deny/unknown)")
    confidence: int = Field(..., description="Confidence score (0-100)")
    result: Dict[str, Any] = Field(..., description="Detailed evaluation result")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    evaluated_at: str = Field(..., description="Evaluation timestamp")
    status: str = Field(..., description="Evaluation status")

class PolicyCreateRequest(BaseModel):
    name: str = Field(..., description="Policy name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Policy description")
    content: str = Field(..., description="Policy content in Rego format")
    version: str = Field(default="1.0.0", description="Policy version")
    status: str = Field(default="draft", description="Policy status")
    category: Optional[str] = Field(None, description="Policy category")
    tags: Optional[List[str]] = Field(None, description="Policy tags")
    created_by: Optional[str] = Field(None, description="User who created the policy")

class PolicyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Policy name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Policy description")
    content: Optional[str] = Field(None, description="Policy content in Rego format")
    version: Optional[str] = Field(None, description="Policy version")
    status: Optional[str] = Field(None, description="Policy status")
    category: Optional[str] = Field(None, description="Policy category")
    tags: Optional[List[str]] = Field(None, description="Policy tags")

class PolicyResponse(BaseModel):
    id: str = Field(..., description="Policy ID")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    content: str = Field(..., description="Policy content")
    version: str = Field(..., description="Policy version")
    status: str = Field(..., description="Policy status")
    category: Optional[str] = Field(None, description="Policy category")
    tags: Optional[List[str]] = Field(None, description="Policy tags")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created the policy")

class PolicyBundleRequest(BaseModel):
    name: str = Field(..., description="Bundle name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Bundle description")
    policies: List[str] = Field(..., description="List of policy IDs in the bundle")
    version: str = Field(default="1.0.0", description="Bundle version")
    status: str = Field(default="active", description="Bundle status")

class PolicyBundleResponse(BaseModel):
    id: str = Field(..., description="Bundle ID")
    name: str = Field(..., description="Bundle name")
    description: Optional[str] = Field(None, description="Bundle description")
    policies: List[str] = Field(..., description="List of policy IDs")
    version: str = Field(..., description="Bundle version")
    status: str = Field(..., description="Bundle status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

class BulkEvaluationRequest(BaseModel):
    evaluations: List[PolicyEvaluationRequest] = Field(..., description="List of evaluation requests")
    batch_id: Optional[str] = Field(None, description="Optional batch ID for tracking")

class BulkEvaluationResponse(BaseModel):
    batch_id: str = Field(..., description="Batch ID")
    total_evaluations: int = Field(..., description="Total number of evaluations")
    successful: int = Field(..., description="Number of successful evaluations")
    failed: int = Field(..., description="Number of failed evaluations")
    results: List[PolicyEvaluationResponse] = Field(..., description="Evaluation results")
    processing_time_ms: int = Field(..., description="Total processing time")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    uptime: str = Field(..., description="Service uptime")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: str = Field(..., description="Request ID for tracking")

# Initialize FastAPI app
app = FastAPI(
    title="Policy Service API",
    description="OpenPolicy platform policy evaluation and management service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
policy_engine = PolicyEngine()
service_client = ServiceClient()

# Dependency for database session
def get_db_session():
    return get_session()

# Dependency for authentication (placeholder)
async def get_current_user(authorization: str = Depends(Query(..., alias="Authorization"))):
    # In a real implementation, this would validate JWT tokens
    # For now, return a placeholder user
    return {"user_id": "system", "username": "system"}

# Health check endpoints
@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check OPA connectivity
        opa_healthy = await policy_engine.health_check()
        
        status = "healthy" if opa_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="0 days, 0 hours, 0 minutes"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="0 days, 0 hours, 0 minutes"
        )

@app.get("/readyz", response_model=HealthResponse, tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if service is ready to handle requests
        # This could include database connectivity, OPA status, etc.
        
        return HealthResponse(
            status="ready",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="0 days, 0 hours, 0 minutes"
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return HealthResponse(
            status="not_ready",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="0 days, 0 hours, 0 minutes"
        )

# Policy evaluation endpoints
@app.post("/evaluate", response_model=PolicyEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """Evaluate a policy against input data"""
    try:
        start_time = datetime.now()
        
        # Validate policy exists
        policy = await _get_policy_by_id(request.policy_id, db_session)
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {request.policy_id} not found")
        
        # Check if policy is active
        if policy["status"] != "active":
            raise HTTPException(status_code=400, detail=f"Policy {request.policy_id} is not active")
        
        # Evaluate policy
        evaluation_result = await policy_engine.evaluate_policy(
            request.policy_id,
            request.input_data,
            policy["content"]
        )
        
        # Generate evaluation ID
        evaluation_id = str(uuid.uuid4())
        
        # Store evaluation result
        await _store_evaluation_result(
            evaluation_id, request.policy_id, request.input_data,
            evaluation_result, current_user["user_id"], db_session
        )
        
        # Record metrics
        await service_client.record_metric(
            "policy_evaluations_total", 1,
            {"policy_id": request.policy_id, "decision": evaluation_result["decision"]}
        )
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return PolicyEvaluationResponse(
            evaluation_id=evaluation_id,
            policy_id=request.policy_id,
            decision=evaluation_result["decision"],
            confidence=evaluation_result["confidence"],
            result=evaluation_result["result"],
            execution_time_ms=int(execution_time),
            evaluated_at=evaluation_result["evaluated_at"],
            status=evaluation_result["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/evaluate/bulk", response_model=BulkEvaluationResponse, tags=["Policy Evaluation"])
async def bulk_evaluate_policies(
    request: BulkEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """Evaluate multiple policies in bulk"""
    try:
        start_time = datetime.now()
        
        # Generate batch ID if not provided
        batch_id = request.batch_id or str(uuid.uuid4())
        
        # Process evaluations concurrently
        evaluation_tasks = []
        for eval_request in request.evaluations:
            task = _evaluate_single_policy(eval_request, current_user, db_session)
            evaluation_tasks.append(task)
        
        # Execute all evaluations
        results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
                logger.error(f"Bulk evaluation failed: {result}")
            else:
                successful_results.append(result)
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BulkEvaluationResponse(
            batch_id=batch_id,
            total_evaluations=len(request.evaluations),
            successful=len(successful_results),
            failed=failed_count,
            results=successful_results,
            processing_time_ms=int(total_time)
        )
        
    except Exception as e:
        logger.error(f"Bulk evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/evaluate/bundle/{bundle_id}", response_model=Dict[str, Any], tags=["Policy Evaluation"])
async def evaluate_policy_bundle(
    bundle_id: str = Path(..., description="Policy bundle ID"),
    input_data: Dict[str, Any] = Body(..., description="Input data for evaluation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """Evaluate all policies in a bundle"""
    try:
        # Get bundle details
        bundle = await _get_policy_bundle_by_id(bundle_id, db_session)
        if not bundle:
            raise HTTPException(status_code=404, detail=f"Policy bundle {bundle_id} not found")
        
        # Evaluate bundle
        bundle_result = await policy_engine.evaluate_policy_bundle(bundle_id, input_data)
        
        # Store bundle evaluation
        await _store_bundle_evaluation(bundle_id, input_data, bundle_result, current_user["user_id"], db_session)
        
        return bundle_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bundle evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Policy management endpoints
@app.post("/policies", response_model=PolicyResponse, tags=["Policy Management"])
async def create_policy(
    request: PolicyCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """Create a new policy"""
    try:
        # Validate policy content (basic Rego syntax check)
        if not _validate_rego_syntax(request.content):
            raise HTTPException(status_code=400, detail="Invalid Rego syntax")
        
        # Generate policy ID
        policy_id = str(uuid.uuid4())
        
        # Create policy
        await _create_policy_record(policy_id, request, current_user["user_id"], db_session)
        
        # Get created policy
        policy = await _get_policy_by_id(policy_id, db_session)
        
        return PolicyResponse(**policy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/policies", response_model=List[PolicyResponse], tags=["Policy Management"])
async def list_policies(
    status: Optional[str] = Query(None, description="Filter by policy status"),
    category: Optional[str] = Query(None, description="Filter by policy category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of policies to return"),
    offset: int = Query(0, ge=0, description="Number of policies to skip"),
    db_session = Depends(get_db_session)
):
    """List policies with optional filtering"""
    try:
        policies = await _list_policies(status, category, limit, offset, db_session)
        return [PolicyResponse(**policy) for policy in policies]
        
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/policies/{policy_id}", response_model=PolicyResponse, tags=["Policy Management"])
async def get_policy(
    policy_id: str = Path(..., description="Policy ID"),
    db_session = Depends(get_db_session)
):
    """Get policy by ID"""
    try:
        policy = await _get_policy_by_id(policy_id, db_session)
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        
        return PolicyResponse(**policy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/policies/{policy_id}", response_model=PolicyResponse, tags=["Policy Management"])
async def update_policy(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session),
    policy_id: str = Path(..., description="Policy ID"),
    request: PolicyUpdateRequest
):
    """Update an existing policy"""
    try:
        # Check if policy exists
        existing_policy = await _get_policy_by_id(policy_id, db_session)
        if not existing_policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        
        # Validate content if provided
        if request.content and not _validate_rego_syntax(request.content):
            raise HTTPException(status_code=400, detail="Invalid Rego syntax")
        
        # Update policy
        await _update_policy_record(policy_id, request, current_user["user_id"], db_session)
        
        # Get updated policy
        policy = await _get_policy_by_id(policy_id, db_session)
        
        return PolicyResponse(**policy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy update failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/policies/{policy_id}", tags=["Policy Management"])
async def delete_policy(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session),
    policy_id: str = Path(..., description="Policy ID")
):
    """Delete a policy"""
    try:
        # Check if policy exists
        existing_policy = await _get_policy_by_id(policy_id, db_session)
        if not existing_policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        
        # Soft delete (mark as deleted)
        await _soft_delete_policy(policy_id, current_user["user_id"], db_session)
        
        return {"message": f"Policy {policy_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Policy bundle endpoints
@app.post("/bundles", response_model=PolicyBundleResponse, tags=["Policy Bundles"])
async def create_policy_bundle(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session),
    request: PolicyBundleRequest
):
    """Create a new policy bundle"""
    try:
        # Validate that all policies exist
        for policy_id in request.policies:
            policy = await _get_policy_by_id(policy_id, db_session)
            if not policy:
                raise HTTPException(status_code=400, detail=f"Policy {policy_id} not found")
        
        # Generate bundle ID
        bundle_id = str(uuid.uuid4())
        
        # Create bundle
        await _create_policy_bundle(bundle_id, request, current_user["user_id"], db_session)
        
        # Get created bundle
        bundle = await _get_policy_bundle_by_id(bundle_id, db_session)
        
        return PolicyBundleResponse(**bundle)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bundle creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/bundles", response_model=List[PolicyBundleResponse], tags=["Policy Bundles"])
async def list_policy_bundles(
    db_session = Depends(get_db_session),
    status: Optional[str] = Query(None, description="Filter by bundle status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of bundles to return"),
    offset: int = Query(0, ge=0, description="Number of bundles to skip")
):
    """List policy bundles with optional filtering"""
    try:
        bundles = await _list_policy_bundles(status, limit, offset, db_session)
        return [PolicyBundleResponse(**bundle) for bundle in bundles]
        
    except Exception as e:
        logger.error(f"Failed to list bundles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Utility endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Policy Service is running",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/healthz",
            "readiness": "/readyz",
            "evaluate": "/evaluate",
            "policies": "/policies",
            "bundles": "/bundles",
            "docs": "/docs"
        }
    }

# Helper functions
async def _get_policy_by_id(policy_id: str, db_session) -> Optional[Dict[str, Any]]:
    """Get policy by ID from database"""
    try:
        result = db_session.execute(
            text("""
                SELECT id, name, description, content, version, status, category, tags,
                       created_at, updated_at, created_by
                FROM policy.policies 
                WHERE id = :policy_id AND deleted_at IS NULL
            """),
            {"policy_id": policy_id}
        ).fetchone()
        
        if result:
            policy = dict(result)
            policy['created_at'] = policy['created_at'].isoformat() if policy['created_at'] else None
            policy['updated_at'] = policy['updated_at'].isoformat() if policy['updated_at'] else None
            if policy.get('tags'):
                try:
                    policy['tags'] = json.loads(policy['tags'])
                except:
                    policy['tags'] = []
            return policy
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get policy by ID: {e}")
        return None

async def _create_policy_record(policy_id: str, request: PolicyCreateRequest, 
                              user_id: str, db_session):
    """Create policy record in database"""
    try:
        db_session.execute(
            text("""
                INSERT INTO policy.policies 
                (id, name, description, content, version, status, category, tags,
                 created_at, updated_at, created_by)
                VALUES (:id, :name, :description, :content, :version, :status,
                       :category, :tags, NOW(), NOW(), :created_by)
            """),
            {
                "id": policy_id,
                "name": request.name,
                "description": request.description,
                "content": request.content,
                "version": request.version,
                "status": request.status,
                "category": request.category,
                "tags": json.dumps(request.tags) if request.tags else None,
                "created_by": user_id
            }
        )
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to create policy record: {e}")
        raise

def _validate_rego_syntax(content: str) -> bool:
    """Basic Rego syntax validation"""
    # This is a simplified validation - in production, use proper Rego parser
    required_keywords = ["package", "allow"]
    
    content_lower = content.lower()
    for keyword in required_keywords:
        if keyword not in content_lower:
            return False
    
    return True

async def _store_evaluation_result(evaluation_id: str, policy_id: str, input_data: Dict[str, Any],
                                 result: Dict[str, Any], user_id: str, db_session):
    """Store evaluation result in database"""
    try:
        db_session.execute(
            text("""
                INSERT INTO policy.policy_evaluations 
                (id, policy_id, input_data, result, decision, confidence, execution_time_ms, created_at)
                VALUES (:id, :policy_id, :input_data, :result, :decision, :confidence, :execution_time, NOW())
            """),
            {
                "id": evaluation_id,
                "policy_id": policy_id,
                "input_data": json.dumps(input_data),
                "result": json.dumps(result),
                "decision": result["decision"],
                "confidence": result["confidence"],
                "execution_time": result["execution_time_ms"]
            }
        )
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to store evaluation result: {e}")

async def _evaluate_single_policy(eval_request: PolicyEvaluationRequest, 
                                current_user: Dict[str, Any], db_session = None) -> PolicyEvaluationResponse:
    """Evaluate a single policy (for bulk operations)"""
    try:
        # This would call the same logic as the single evaluation endpoint
        # Simplified for now
        return PolicyEvaluationResponse(
            evaluation_id=str(uuid.uuid4()),
            policy_id=eval_request.policy_id,
            decision="allow",
            confidence=85,
            result={"allow": True},
            execution_time_ms=50,
            evaluated_at=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        logger.error(f"Single policy evaluation failed: {e}")
        raise

async def _get_policy_bundle_by_id(bundle_id: str, db_session) -> Optional[Dict[str, Any]]:
    """Get policy bundle by ID"""
    try:
        result = db_session.execute(
            text("""
                SELECT id, name, description, policies, version, status, created_at, updated_at
                FROM policy.policy_bundles 
                WHERE id = :bundle_id
            """),
            {"bundle_id": bundle_id}
        ).fetchone()
        
        if result:
            bundle = dict(result)
            bundle['created_at'] = bundle['created_at'].isoformat() if bundle['created_at'] else None
            bundle['updated_at'] = bundle['updated_at'].isoformat() if bundle['updated_at'] else None
            if bundle.get('policies'):
                try:
                    bundle['policies'] = json.loads(bundle['policies'])
                except:
                    bundle['policies'] = []
            return bundle
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get policy bundle: {e}")
        return None

async def _create_policy_bundle(bundle_id: str, request: PolicyBundleRequest, 
                              user_id: str, db_session):
    """Create policy bundle record"""
    try:
        db_session.execute(
            text("""
                INSERT INTO policy.policy_bundles 
                (id, name, description, policies, version, status, created_at, updated_at)
                VALUES (:id, :name, :description, :policies, :version, :status, NOW(), NOW())
            """),
            {
                "id": bundle_id,
                "name": request.name,
                "description": request.description,
                "policies": json.dumps(request.policies),
                "version": request.version,
                "status": request.status
            }
        )
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to create policy bundle: {e}")
        raise

async def _list_policies(status: Optional[str], category: Optional[str], 
                        limit: int, offset: int, db_session) -> List[Dict[str, Any]]:
    """List policies with filtering"""
    try:
        query = """
            SELECT id, name, description, content, version, status, category, tags,
                   created_at, updated_at, created_by
            FROM policy.policies 
            WHERE deleted_at IS NULL
        """
        params = {}
        
        if status:
            query += " AND status = :status"
            params["status"] = status
        
        if category:
            query += " AND category = :category"
            params["category"] = category
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db_session.execute(text(query), params).fetchall()
        
        policies = []
        for row in result:
            policy = dict(row)
            policy['created_at'] = policy['created_at'].isoformat() if policy['created_at'] else None
            policy['updated_at'] = policy['updated_at'].isoformat() if policy['updated_at'] else None
            if policy.get('tags'):
                try:
                    policy['tags'] = json.loads(policy['tags'])
                except:
                    policy['tags'] = []
            policies.append(policy)
        
        return policies
        
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        return []

async def _update_policy_record(policy_id: str, request: PolicyUpdateRequest, 
                              user_id: str, db_session):
    """Update policy record"""
    try:
        update_fields = []
        params = {"policy_id": policy_id}
        
        if request.name is not None:
            update_fields.append("name = :name")
            params["name"] = request.name
        
        if request.description is not None:
            update_fields.append("description = :description")
            params["description"] = request.description
        
        if request.content is not None:
            update_fields.append("content = :content")
            params["content"] = request.content
        
        if request.version is not None:
            update_fields.append("version = :version")
            params["version"] = request.version
        
        if request.status is not None:
            update_fields.append("status = :status")
            params["status"] = request.status
        
        if request.category is not None:
            update_fields.append("category = :category")
            params["category"] = request.category
        
        if request.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = json.dumps(request.tags)
        
        if update_fields:
            update_fields.append("updated_at = NOW()")
            query = f"UPDATE policy.policies SET {', '.join(update_fields)} WHERE id = :policy_id"
            
            db_session.execute(text(query), params)
            db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to update policy record: {e}")
        raise

async def _soft_delete_policy(policy_id: str, user_id: str, db_session):
    """Soft delete policy"""
    try:
        db_session.execute(
            text("""
                UPDATE policy.policies 
                SET deleted_at = NOW(), updated_at = NOW() 
                WHERE id = :policy_id
            """),
            {"policy_id": policy_id}
        )
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to soft delete policy: {e}")
        raise

async def _list_policy_bundles(status: Optional[str], limit: int, offset: int, 
                              db_session) -> List[Dict[str, Any]]:
    """List policy bundles with filtering"""
    try:
        query = """
            SELECT id, name, description, policies, version, status, created_at, updated_at
            FROM policy.policy_bundles
        """
        params = {}
        
        if status:
            query += " WHERE status = :status"
            params["status"] = status
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db_session.execute(text(query), params).fetchall()
        
        bundles = []
        for row in result:
            bundle = dict(row)
            bundle['created_at'] = bundle['created_at'].isoformat() if bundle['created_at'] else None
            bundle['updated_at'] = bundle['updated_at'].isoformat() if bundle['updated_at'] else None
            if bundle.get('policies'):
                try:
                    bundle['policies'] = json.loads(bundle['policies'])
                except:
                    bundle['policies'] = []
            bundles.append(bundle)
        
        return bundles
        
    except Exception as e:
        logger.error(f"Failed to list policy bundles: {e}")
        return []

async def _store_bundle_evaluation(bundle_id: str, input_data: Dict[str, Any], 
                                 result: Dict[str, Any], user_id: str, db_session):
    """Store bundle evaluation result"""
    try:
        # This would store bundle evaluation results
        # Implementation depends on database schema
        pass
    except Exception as e:
        logger.error(f"Failed to store bundle evaluation: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat(),
            request_id=str(uuid.uuid4())
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now().isoformat(),
            request_id=str(uuid.uuid4())
        ).dict()
    )

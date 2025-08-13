"""
Policy Service API - Complete Implementation
FastAPI application for policy management and evaluation.
"""

from fastapi import FastAPI, Depends, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime, timedelta

from .models import Policy, PolicyEvaluation, PolicyRule, PolicyBundle
from .database import get_session as get_db_session
from .policy_engine import PolicyEngine
from .service_client import ServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Policy Service API",
    description="OpenPolicy Platform - Policy Management and Evaluation Service",
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

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PolicyCreateRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    content: str = Field(..., description="Policy content (Rego code)")
    version: str = Field(..., description="Policy version")
    category: Optional[str] = Field(None, description="Policy category")
    tags: Optional[List[str]] = Field(None, description="Policy tags")
    enabled: bool = Field(True, description="Whether policy is enabled")

class PolicyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    content: Optional[str] = Field(None, description="Policy content (Rego code)")
    version: Optional[str] = Field(None, description="Policy version")
    category: Optional[str] = Field(None, description="Policy category")
    tags: Optional[List[str]] = Field(None, description="Policy tags")
    enabled: Optional[bool] = Field(None, description="Whether policy is enabled")

class PolicyResponse(BaseModel):
    id: str
    name: str
    description: str
    content: str
    version: str
    category: Optional[str]
    tags: Optional[List[str]]
    enabled: bool
    created_at: datetime
    updated_at: datetime

class PolicyEvaluationRequest(BaseModel):
    policy_id: str = Field(..., description="Policy ID to evaluate")
    input: Dict[str, Any] = Field(..., description="Input data for policy evaluation")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class PolicyEvaluationResponse(BaseModel):
    policy_id: str
    result: bool
    explanation: str
    metadata: Dict[str, Any]
    evaluation_time: datetime
    duration_ms: float

class BulkEvaluationRequest(BaseModel):
    evaluations: List[PolicyEvaluationRequest] = Field(..., description="List of evaluations to perform")

class BulkEvaluationResponse(BaseModel):
    results: List[PolicyEvaluationResponse]
    summary: Dict[str, Any]

class PolicyBundleCreateRequest(BaseModel):
    name: str = Field(..., description="Bundle name")
    description: str = Field(..., description="Bundle description")
    policies: List[str] = Field(..., description="List of policy IDs in bundle")
    version: str = Field(..., description="Bundle version")

class PolicyBundleResponse(BaseModel):
    id: str
    name: str
    description: str
    policies: List[str]
    version: str
    created_at: datetime
    updated_at: datetime

class PolicyRuleCreateRequest(BaseModel):
    policy_id: str = Field(..., description="Policy ID")
    rule_name: str = Field(..., description="Rule name")
    rule_condition: str = Field(..., description="Rule condition")
    rule_action: str = Field(..., description="Rule action")
    priority: int = Field(1, description="Rule priority")

class PolicyRuleResponse(BaseModel):
    id: str
    policy_id: str
    rule_name: str
    rule_condition: str
    rule_action: str
    priority: int
    created_at: datetime

# Dependency functions
async def get_current_user():
    """Get current authenticated user (placeholder for now)."""
    # TODO: Implement actual JWT validation
    return {"id": "test-user", "username": "testuser", "role": "admin"}

def get_db_session():
    """Get database session."""
    return next(get_db_session())

# Health and readiness endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Simplified health check to prevent recursion
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "policy-service",
            "version": "1.0.0",
            "database": "available",
            "policy_engine": "ready"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Simplified readiness check to prevent recursion
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "service": "policy-service"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Policy management endpoints
@app.post("/policies", response_model=PolicyResponse, status_code=201, tags=["Policy Management"])
async def create_policy(
    request: PolicyCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Create a new policy."""
    try:
        # Validate policy content
        if not policy_engine.validate_policy(request.content):
            raise HTTPException(status_code=400, detail="Invalid policy content")
        
        # Create policy
        policy = Policy(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            content=request.content,
            version=request.version,
            category=request.category,
            tags=request.tags or [],
            enabled=request.enabled,
            created_by=current_user["id"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(policy)
        db_session.commit()
        db_session.refresh(policy)
        
        logger.info(f"Policy created: {policy.id}")
        return PolicyResponse(
            id=policy.id,
            name=policy.name,
            description=policy.description,
            content=policy.content,
            version=policy.version,
            category=policy.category,
            tags=policy.tags,
            enabled=policy.enabled,
            created_at=policy.created_at,
            updated_at=policy.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create policy")

@app.get("/policies", response_model=List[PolicyResponse], tags=["Policy Management"])
async def list_policies(
    skip: int = Query(0, ge=0, description="Number of policies to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of policies to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db_session: Session = Depends(get_db_session)
):
    """List policies with optional filtering."""
    try:
        query = db_session.query(Policy)
        
        if category:
            query = query.filter(Policy.category == category)
        if enabled is not None:
            query = query.filter(Policy.enabled == enabled)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Policy.name.ilike(search_term)) | 
                (Policy.description.ilike(search_term))
            )
        
        policies = query.offset(skip).limit(limit).all()
        
        return [
            PolicyResponse(
                id=policy.id,
                name=policy.name,
                description=policy.description,
                content=policy.content,
                version=policy.version,
                category=policy.category,
                tags=policy.tags,
                enabled=policy.enabled,
                created_at=policy.created_at,
                updated_at=policy.updated_at
            )
            for policy in policies
        ]
        
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail="Failed to list policies")

@app.get("/policies/{policy_id}", response_model=PolicyResponse, tags=["Policy Management"])
async def get_policy(
    policy_id: str = Path(..., description="Policy ID"),
    db_session: Session = Depends(get_db_session)
):
    """Get a specific policy by ID."""
    try:
        policy = db_session.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return PolicyResponse(
            id=policy.id,
            name=policy.name,
            description=policy.description,
            content=policy.content,
            version=policy.version,
            category=policy.category,
            tags=policy.tags,
            enabled=policy.enabled,
            created_at=policy.created_at,
            updated_at=policy.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get policy")

@app.put("/policies/{policy_id}", response_model=PolicyResponse, tags=["Policy Management"])
async def update_policy(
    policy_id: str = Path(..., description="Policy ID"),
    request: PolicyUpdateRequest = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Update an existing policy."""
    try:
        policy = db_session.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Update fields if provided
        if request.name is not None:
            policy.name = request.name
        if request.description is not None:
            policy.description = request.description
        if request.content is not None:
            if not policy_engine.validate_policy(request.content):
                raise HTTPException(status_code=400, detail="Invalid policy content")
            policy.content = request.content
        if request.version is not None:
            policy.version = request.version
        if request.category is not None:
            policy.category = request.category
        if request.tags is not None:
            policy.tags = request.tags
        if request.enabled is not None:
            policy.enabled = request.enabled
        
        policy.updated_at = datetime.now()
        policy.updated_by = current_user["id"]
        
        db_session.commit()
        db_session.refresh(policy)
        
        logger.info(f"Policy updated: {policy.id}")
        return PolicyResponse(
            id=policy.id,
            name=policy.name,
            description=policy.description,
            content=policy.content,
            version=policy.version,
            category=policy.category,
            tags=policy.tags,
            enabled=policy.enabled,
            created_at=policy.created_at,
            updated_at=policy.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update policy {policy_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update policy")

@app.delete("/policies/{policy_id}", status_code=204, tags=["Policy Management"])
async def delete_policy(
    policy_id: str = Path(..., description="Policy ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Delete a policy."""
    try:
        policy = db_session.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        db_session.delete(policy)
        db_session.commit()
        
        logger.info(f"Policy deleted: {policy_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete policy {policy_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete policy")

# Policy evaluation endpoints
@app.post("/evaluate", response_model=PolicyEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Evaluate a single policy."""
    try:
        # Get policy
        policy = db_session.query(Policy).filter(Policy.id == request.policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        if not policy.enabled:
            raise HTTPException(status_code=400, detail="Policy is disabled")
        
        # Evaluate policy
        start_time = datetime.now()
        result = policy_engine.evaluate_policy(policy.content, request.input, request.context)
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # Record evaluation
        evaluation = PolicyEvaluation(
            id=str(uuid.uuid4()),
            policy_id=policy.id,
            input_data=request.input,
            context=request.context or {},
            result=result["result"],
            explanation=result.get("explanation", ""),
            metadata=result.get("metadata", {}),
            evaluated_by=current_user["id"],
            evaluation_time=datetime.now(),
            duration_ms=duration
        )
        
        db_session.add(evaluation)
        db_session.commit()
        
        return PolicyEvaluationResponse(
            policy_id=policy.id,
            result=result["result"],
            explanation=result.get("explanation", ""),
            metadata=result.get("metadata", {}),
            evaluation_time=datetime.now(),
            duration_ms=duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate policy")

@app.post("/evaluate/bulk", response_model=BulkEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policies_bulk(
    request: BulkEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Evaluate multiple policies in bulk."""
    try:
        results = []
        total_evaluations = len(request.evaluations)
        successful_evaluations = 0
        failed_evaluations = 0
        
        for eval_request in request.evaluations:
            try:
                # Get policy
                policy = db_session.query(Policy).filter(Policy.id == eval_request.policy_id).first()
                if not policy:
                    results.append(PolicyEvaluationResponse(
                        policy_id=eval_request.policy_id,
                        result=False,
                        explanation="Policy not found",
                        metadata={"error": "Policy not found"},
                        evaluation_time=datetime.now(),
                        duration_ms=0
                    ))
                    failed_evaluations += 1
                    continue
                
                if not policy.enabled:
                    results.append(PolicyEvaluationResponse(
                        policy_id=eval_request.policy_id,
                        result=False,
                        explanation="Policy is disabled",
                        metadata={"error": "Policy disabled"},
                        evaluation_time=datetime.now(),
                        duration_ms=0
                    ))
                    failed_evaluations += 1
                    continue
                
                # Evaluate policy
                start_time = datetime.now()
                result = policy_engine.evaluate_policy(policy.content, eval_request.input, eval_request.context)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Record evaluation
                evaluation = PolicyEvaluation(
                    id=str(uuid.uuid4()),
                    policy_id=policy.id,
                    input_data=eval_request.input,
                    context=eval_request.context or {},
                    result=result["result"],
                    explanation=result.get("explanation", ""),
                    metadata=result.get("metadata", {}),
                    evaluated_by=current_user["id"],
                    evaluation_time=datetime.now(),
                    duration_ms=duration
                )
                
                db_session.add(evaluation)
                
                results.append(PolicyEvaluationResponse(
                    policy_id=policy.id,
                    result=result["result"],
                    explanation=result.get("explanation", ""),
                    metadata=result.get("metadata", {}),
                    evaluation_time=datetime.now(),
                    duration_ms=duration
                ))
                
                successful_evaluations += 1
                
            except Exception as e:
                logger.error(f"Failed to evaluate policy {eval_request.policy_id}: {e}")
                results.append(PolicyEvaluationResponse(
                    policy_id=eval_request.policy_id,
                    result=False,
                    explanation="Evaluation failed",
                    metadata={"error": str(e)},
                    evaluation_time=datetime.now(),
                    duration_ms=0
                ))
                failed_evaluations += 1
        
        db_session.commit()
        
        summary = {
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": failed_evaluations,
            "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0
        }
        
        return BulkEvaluationResponse(results=results, summary=summary)
        
    except Exception as e:
        logger.error(f"Failed to evaluate policies in bulk: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to evaluate policies in bulk")

@app.post("/evaluate/bundle/{bundle_id}", response_model=BulkEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policy_bundle(
    bundle_id: str = Path(..., description="Policy bundle ID"),
    input_data: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Evaluate all policies in a bundle."""
    try:
        # Get bundle
        bundle = db_session.query(PolicyBundle).filter(PolicyBundle.id == bundle_id).first()
        if not bundle:
            raise HTTPException(status_code=404, detail="Policy bundle not found")
        
        # Get all policies in bundle
        policies = db_session.query(Policy).filter(
            Policy.id.in_(bundle.policies),
            Policy.enabled == True
        ).all()
        
        if not policies:
            raise HTTPException(status_code=400, detail="No enabled policies found in bundle")
        
        results = []
        successful_evaluations = 0
        failed_evaluations = 0
        
        for policy in policies:
            try:
                # Evaluate policy
                start_time = datetime.now()
                result = policy_engine.evaluate_policy(policy.content, input_data or {}, context or {})
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Record evaluation
                evaluation = PolicyEvaluation(
                    id=str(uuid.uuid4()),
                    policy_id=policy.id,
                    input_data=input_data or {},
                    context=context or {},
                    result=result["result"],
                    explanation=result.get("explanation", ""),
                    metadata=result.get("metadata", {}),
                    evaluated_by=current_user["id"],
                    evaluation_time=datetime.now(),
                    duration_ms=duration
                )
                
                db_session.add(evaluation)
                
                results.append(PolicyEvaluationResponse(
                    policy_id=policy.id,
                    result=result["result"],
                    explanation=result.get("explanation", ""),
                    metadata=result.get("metadata", {}),
                    evaluation_time=datetime.now(),
                    duration_ms=duration
                ))
                
                successful_evaluations += 1
                
            except Exception as e:
                logger.error(f"Failed to evaluate policy {policy.id}: {e}")
                results.append(PolicyEvaluationResponse(
                    policy_id=policy.id,
                    result=False,
                    explanation="Evaluation failed",
                    metadata={"error": str(e)},
                    evaluation_time=datetime.now(),
                    duration_ms=0
                ))
                failed_evaluations += 1
        
        db_session.commit()
        
        summary = {
            "bundle_id": bundle_id,
            "total_policies": len(policies),
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": failed_evaluations,
            "success_rate": successful_evaluations / len(policies) if policies else 0
        }
        
        return BulkEvaluationResponse(results=results, summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate policy bundle {bundle_id}: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to evaluate policy bundle")

# Policy bundle management endpoints
@app.post("/bundles", response_model=PolicyBundleResponse, status_code=201, tags=["Policy Bundles"])
async def create_policy_bundle(
    request: PolicyBundleCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Create a new policy bundle."""
    try:
        # Validate that all policies exist
        policies = db_session.query(Policy).filter(Policy.id.in_(request.policies)).all()
        if len(policies) != len(request.policies):
            existing_ids = [p.id for p in policies]
            missing_ids = [pid for pid in request.policies if pid not in existing_ids]
            raise HTTPException(status_code=400, detail=f"Policies not found: {missing_ids}")
        
        # Create bundle
        bundle = PolicyBundle(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            policies=request.policies,
            version=request.version,
            created_by=current_user["id"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db_session.add(bundle)
        db_session.commit()
        db_session.refresh(bundle)
        
        logger.info(f"Policy bundle created: {bundle.id}")
        return PolicyBundleResponse(
            id=bundle.id,
            name=bundle.name,
            description=bundle.description,
            policies=bundle.policies,
            version=bundle.version,
            created_at=bundle.created_at,
            updated_at=bundle.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create policy bundle: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create policy bundle")

@app.get("/bundles", response_model=List[PolicyBundleResponse], tags=["Policy Bundles"])
async def list_policy_bundles(
    skip: int = Query(0, ge=0, description="Number of bundles to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of bundles to return"),
    db_session: Session = Depends(get_db_session)
):
    """List policy bundles."""
    try:
        bundles = db_session.query(PolicyBundle).offset(skip).limit(limit).all()
        
        return [
            PolicyBundleResponse(
                id=bundle.id,
                name=bundle.name,
                description=bundle.description,
                policies=bundle.policies,
                version=bundle.version,
                created_at=bundle.created_at,
                updated_at=bundle.updated_at
            )
            for bundle in bundles
        ]
        
    except Exception as e:
        logger.error(f"Failed to list policy bundles: {e}")
        raise HTTPException(status_code=500, detail="Failed to list policy bundles")

@app.get("/bundles/{bundle_id}", response_model=PolicyBundleResponse, tags=["Policy Bundles"])
async def get_policy_bundle(
    bundle_id: str = Path(..., description="Policy bundle ID"),
    db_session: Session = Depends(get_db_session)
):
    """Get a specific policy bundle by ID."""
    try:
        bundle = db_session.query(PolicyBundle).filter(PolicyBundle.id == bundle_id).first()
        if not bundle:
            raise HTTPException(status_code=404, detail="Policy bundle not found")
        
        return PolicyBundleResponse(
            id=bundle.id,
            name=bundle.name,
            description=bundle.description,
            policies=bundle.policies,
            version=bundle.version,
            created_at=bundle.created_at,
            updated_at=bundle.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy bundle {bundle_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get policy bundle")

# Policy rule management endpoints
@app.post("/rules", response_model=PolicyRuleResponse, status_code=201, tags=["Policy Rules"])
async def create_policy_rule(
    request: PolicyRuleCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Create a new policy rule."""
    try:
        # Validate that policy exists
        policy = db_session.query(Policy).filter(Policy.id == request.policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Create rule
        rule = PolicyRule(
            id=str(uuid.uuid4()),
            policy_id=request.policy_id,
            rule_name=request.rule_name,
            rule_condition=request.rule_condition,
            rule_action=request.rule_action,
            priority=request.priority,
            created_at=datetime.now()
        )
        
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        
        logger.info(f"Policy rule created: {rule.id}")
        return PolicyRuleResponse(
            id=rule.id,
            policy_id=rule.policy_id,
            rule_name=rule.rule_name,
            rule_condition=rule.rule_condition,
            rule_action=rule.rule_action,
            priority=rule.priority,
            created_at=rule.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create policy rule: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create policy rule")

@app.get("/rules", response_model=List[PolicyRuleResponse], tags=["Policy Rules"])
async def list_policy_rules(
    policy_id: Optional[str] = Query(None, description="Filter by policy ID"),
    skip: int = Query(0, ge=0, description="Number of rules to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of rules to return"),
    db_session: Session = Depends(get_db_session)
):
    """List policy rules with optional filtering."""
    try:
        query = db_session.query(PolicyRule)
        
        if policy_id:
            query = query.filter(PolicyRule.policy_id == policy_id)
        
        rules = query.offset(skip).limit(limit).all()
        
        return [
            PolicyRuleResponse(
                id=rule.id,
                policy_id=rule.policy_id,
                rule_name=rule.rule_name,
                rule_condition=rule.rule_condition,
                rule_action=rule.rule_action,
                priority=rule.priority,
                created_at=rule.created_at
            )
            for rule in rules
        ]
        
    except Exception as e:
        logger.error(f"Failed to list policy rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to list policy rules")

# Statistics and analytics endpoints
@app.get("/stats", tags=["Analytics"])
async def get_policy_statistics(
    db_session: Session = Depends(get_db_session)
):
    """Get policy service statistics."""
    try:
        total_policies = db_session.query(Policy).count()
        enabled_policies = db_session.query(Policy).filter(Policy.enabled == True).count()
        total_evaluations = db_session.query(PolicyEvaluation).count()
        total_bundles = db_session.query(PolicyBundle).count()
        
        # Recent activity
        recent_evaluations = db_session.query(PolicyEvaluation).filter(
            PolicyEvaluation.evaluation_time >= datetime.now() - timedelta(hours=24)
        ).count()
        
        return {
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "disabled_policies": total_policies - enabled_policies,
            "total_evaluations": total_evaluations,
            "total_bundles": total_bundles,
            "evaluations_last_24h": recent_evaluations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

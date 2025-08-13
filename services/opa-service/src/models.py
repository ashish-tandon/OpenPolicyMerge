"""
Data models for OPA Service
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class PolicyRequest(BaseModel):
    """Request model for policy evaluation"""
    policy_id: str = Field(..., description="ID of the policy to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for policy evaluation")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class PolicyResponse(BaseModel):
    """Response model for policy evaluation"""
    decision: str = Field(..., description="Policy decision (allow/deny/unknown)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    explanation: str = Field(default="", description="Explanation of the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PolicyDefinition(BaseModel):
    """Model for policy definition"""
    id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Human-readable policy name")
    description: str = Field(default="", description="Policy description")
    content: str = Field(..., description="Policy content in Rego format")
    version: str = Field(default="1.0.0", description="Policy version")
    enabled: bool = Field(default=True, description="Whether policy is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PolicyValidationRequest(BaseModel):
    """Request model for policy validation"""
    content: str = Field(..., description="Policy content to validate")

class PolicyValidationResponse(BaseModel):
    """Response model for policy validation"""
    valid: bool = Field(..., description="Whether policy is valid")
    message: str = Field(..., description="Validation message")
    errors: List[str] = Field(default_factory=list, description="Validation errors")

class PolicyMetrics(BaseModel):
    """Model for policy metrics"""
    total_policies: int = Field(..., description="Total number of policies")
    active_policies: int = Field(..., description="Number of active policies")
    evaluation_count: int = Field(..., description="Total evaluation count")
    average_response_time: float = Field(..., description="Average response time in ms")
    error_rate: float = Field(..., description="Error rate percentage")
    last_evaluation: Optional[datetime] = Field(default=None, description="Last evaluation timestamp")

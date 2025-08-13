"""
Simple Policy Engine for OPA Service
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PolicyEngine:
    """Simple policy evaluation engine"""
    
    def __init__(self):
        self.policies = {}
        self.evaluation_count = 0
        self.response_times = []
        
        # Initialize with some sample policies
        self._init_sample_policies()
    
    def _init_sample_policies(self):
        """Initialize with sample policies"""
        sample_policies = {
            "data-access": {
                "id": "data-access",
                "name": "Data Access Control",
                "description": "Controls access to sensitive data",
                "content": "package data.access\n\ndefault allow = false\n\nallow {\n  input.user.role == \"admin\"\n}\n\nallow {\n  input.user.role == \"analyst\"\n  input.data.sensitivity == \"low\"\n}",
                "version": "1.0.0",
                "enabled": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "tags": ["access-control", "data"],
                "metadata": {}
            },
            "resource-limits": {
                "id": "resource-limits",
                "name": "Resource Usage Limits",
                "description": "Enforces resource usage limits",
                "content": "package resource.limits\n\ndefault allow = true\n\ndeny {\n  input.resource.cpu > 1000\n}\n\ndeny {\n  input.resource.memory > 8192\n}",
                "version": "1.0.0",
                "enabled": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "tags": ["resource-management", "limits"],
                "metadata": {}
            }
        }
        
        for policy_id, policy in sample_policies.items():
            self.policies[policy_id] = policy
    
    async def evaluate_policy(self, policy_id: str, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate a policy against input data"""
        start_time = datetime.utcnow()
        
        try:
            if policy_id not in self.policies:
                raise ValueError(f"Policy {policy_id} not found")
            
            policy = self.policies[policy_id]
            if not policy["enabled"]:
                raise ValueError(f"Policy {policy_id} is disabled")
            
            # Simple policy evaluation logic
            decision = self._evaluate_policy_logic(policy, input_data, context)
            confidence = self._calculate_confidence(policy, input_data, decision)
            explanation = self._generate_explanation(policy, input_data, decision)
            
            # Update metrics
            self.evaluation_count += 1
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.response_times.append(response_time)
            
            return {
                "decision": decision,
                "confidence": confidence,
                "explanation": explanation,
                "metadata": {
                    "policy_id": policy_id,
                    "policy_version": policy["version"],
                    "response_time_ms": response_time,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")
            raise
    
    def _evaluate_policy_logic(self, policy: Dict[str, Any], input_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Simple policy evaluation logic"""
        policy_id = policy["id"]
        
        if policy_id == "data-access":
            # Data access control logic
            user_role = input_data.get("user", {}).get("role", "unknown")
            data_sensitivity = input_data.get("data", {}).get("sensitivity", "high")
            
            if user_role == "admin":
                return "allow"
            elif user_role == "analyst" and data_sensitivity == "low":
                return "allow"
            else:
                return "deny"
        
        elif policy_id == "resource-limits":
            # Resource limits logic
            cpu_usage = input_data.get("resource", {}).get("cpu", 0)
            memory_usage = input_data.get("resource", {}).get("memory", 0)
            
            if cpu_usage > 1000 or memory_usage > 8192:
                return "deny"
            else:
                return "allow"
        
        else:
            # Default policy logic
            return "allow"
    
    def _calculate_confidence(self, policy: Dict[str, Any], input_data: Dict[str, Any], decision: str) -> float:
        """Calculate confidence score for decision"""
        # Simple confidence calculation
        base_confidence = 0.8
        
        # Adjust based on input data completeness
        if input_data:
            base_confidence += 0.1
        
        # Adjust based on policy complexity
        if len(policy["content"]) > 100:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _generate_explanation(self, policy: Dict[str, Any], input_data: Dict[str, Any], decision: str) -> str:
        """Generate explanation for decision"""
        policy_name = policy["name"]
        
        if decision == "allow":
            return f"Policy '{policy_name}' evaluation resulted in ALLOW decision"
        elif decision == "deny":
            return f"Policy '{policy_name}' evaluation resulted in DENY decision"
        else:
            return f"Policy '{policy_name}' evaluation resulted in UNKNOWN decision"
    
    async def list_policies(self) -> List[Dict[str, Any]]:
        """List all available policies"""
        return list(self.policies.values())
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific policy by ID"""
        return self.policies.get(policy_id)
    
    async def create_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new policy"""
        policy_id = policy["id"]
        if policy_id in self.policies:
            raise ValueError(f"Policy {policy_id} already exists")
        
        # Add timestamps
        policy["created_at"] = datetime.utcnow()
        policy["updated_at"] = datetime.utcnow()
        
        self.policies[policy_id] = policy
        return policy
    
    async def update_policy(self, policy_id: str, policy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing policy"""
        if policy_id not in self.policies:
            return None
        
        # Update timestamp
        policy["updated_at"] = datetime.utcnow()
        
        self.policies[policy_id] = policy
        return policy
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy"""
        if policy_id not in self.policies:
            return False
        
        del self.policies[policy_id]
        return True
    
    async def validate_policy(self, policy_content: str) -> bool:
        """Validate policy syntax (simplified)"""
        # Simple validation - check if content is not empty and contains basic Rego syntax
        if not policy_content or len(policy_content.strip()) < 10:
            return False
        
        # Check for basic Rego keywords
        basic_keywords = ["package", "default", "allow", "deny"]
        has_keywords = any(keyword in policy_content for keyword in basic_keywords)
        
        return has_keywords
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        avg_response_time = 0
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
        
        return {
            "total_policies": len(self.policies),
            "active_policies": len([p for p in self.policies.values() if p["enabled"]]),
            "evaluation_count": self.evaluation_count,
            "average_response_time": round(avg_response_time, 2),
            "error_rate": 0.0,  # Simplified for now
            "last_evaluation": datetime.utcnow().isoformat() if self.evaluation_count > 0 else None
        }

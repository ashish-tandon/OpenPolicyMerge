import json
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class PolicyEngine:
    """Policy evaluation engine using Open Policy Agent (OPA)"""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self.timeout = 30.0
    
    async def evaluate_policy(self, policy_id: str, input_data: Dict[str, Any], 
                            policy_content: str = None) -> Dict[str, Any]:
        """
        Evaluate a policy against input data
        
        Args:
            policy_id: ID of the policy to evaluate
            input_data: Data to evaluate against the policy
            policy_content: Optional policy content (if not stored in OPA)
        
        Returns:
            Evaluation result with decision and metadata
        """
        start_time = datetime.now()
        
        try:
            # Prepare the query for OPA
            query = {
                "input": {
                    "data": input_data,
                    "policy_id": policy_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # If policy content is provided, include it in the query
            if policy_content:
                query["input"]["policy"] = policy_content
            
            # Send request to OPA
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.opa_url}/v1/data/policy/{policy_id}",
                    json=query
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Calculate execution time
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Extract decision from OPA response
                    decision = self._extract_decision(result)
                    confidence = self._calculate_confidence(result)
                    
                    return {
                        "policy_id": policy_id,
                        "decision": decision,
                        "confidence": confidence,
                        "result": result,
                        "execution_time_ms": int(execution_time),
                        "evaluated_at": datetime.now().isoformat(),
                        "status": "success"
                    }
                else:
                    logger.error(f"OPA evaluation failed: {response.status_code} - {response.text}")
                    return {
                        "policy_id": policy_id,
                        "decision": "unknown",
                        "confidence": 0,
                        "result": {"error": response.text},
                        "execution_time_ms": 0,
                        "evaluated_at": datetime.now().isoformat(),
                        "status": "error"
                    }
                    
        except Exception as e:
            logger.error(f"Policy evaluation error: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "policy_id": policy_id,
                "decision": "unknown",
                "confidence": 0,
                "result": {"error": str(e)},
                "execution_time_ms": int(execution_time),
                "evaluated_at": datetime.now().isoformat(),
                "status": "error"
            }
    
    async def evaluate_policy_bundle(self, bundle_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate multiple policies in a bundle
        
        Args:
            bundle_id: ID of the policy bundle
            input_data: Data to evaluate against all policies
        
        Returns:
            Bundle evaluation results
        """
        try:
            # This would typically fetch the bundle from the database
            # For now, we'll simulate bundle evaluation
            bundle_result = {
                "bundle_id": bundle_id,
                "evaluations": [],
                "overall_decision": "allow",
                "evaluated_at": datetime.now().isoformat()
            }
            
            # Simulate evaluating multiple policies
            # In a real implementation, this would fetch policies from the bundle
            policies = ["policy1", "policy2", "policy3"]  # Placeholder
            
            for policy_id in policies:
                result = await self.evaluate_policy(policy_id, input_data)
                bundle_result["evaluations"].append(result)
                
                # If any policy denies, overall decision is deny
                if result["decision"] == "deny":
                    bundle_result["overall_decision"] = "deny"
            
            return bundle_result
            
        except Exception as e:
            logger.error(f"Bundle evaluation error: {e}")
            return {
                "bundle_id": bundle_id,
                "error": str(e),
                "status": "error"
            }
    
    def _extract_decision(self, opa_result: Dict[str, Any]) -> str:
        """Extract decision from OPA result"""
        try:
            # OPA typically returns results in a specific format
            if "result" in opa_result:
                result = opa_result["result"]
                if isinstance(result, list) and len(result) > 0:
                    # Check if the result contains allow/deny logic
                    if "allow" in result[0]:
                        return "allow" if result[0]["allow"] else "deny"
                    elif "decision" in result[0]:
                        return result[0]["decision"]
            
            # Default decision logic
            return "allow"  # Default to allow if unclear
            
        except Exception as e:
            logger.warning(f"Could not extract decision from OPA result: {e}")
            return "unknown"
    
    def _calculate_confidence(self, opa_result: Dict[str, Any]) -> int:
        """Calculate confidence score from OPA result"""
        try:
            # This is a simplified confidence calculation
            # In a real implementation, this would be more sophisticated
            if "result" in opa_result and opa_result["result"]:
                return 85  # High confidence if we got a result
            else:
                return 50  # Medium confidence if no clear result
        except:
            return 0
    
    async def health_check(self) -> bool:
        """Check if OPA is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.opa_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OPA health check failed: {e}")
            return False

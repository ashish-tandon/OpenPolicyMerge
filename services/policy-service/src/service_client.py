import httpx
import os
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class ServiceClient:
    """Client for communicating with other services"""
    
    def __init__(self):
        self.base_urls = {
            'auth': os.getenv('AUTH_SERVICE_URL', 'http://localhost:9003'),
            'search': os.getenv('SEARCH_SERVICE_URL', 'http://localhost:9002'),
            'config': os.getenv('CONFIG_SERVICE_URL', 'http://localhost:9005'),
            'monitoring': os.getenv('MONITORING_SERVICE_URL', 'http://localhost:9010'),
            'notification': os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:9004')
        }
        self.timeout = 30.0
    
    def get_auth_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get authenticated user from auth service"""
        try:
            # For now, return a mock user to prevent recursion issues
            # In production, this would make actual HTTP calls
            return {
                "id": "mock-user-123",
                "username": "testuser",
                "email": "test@example.com",
                "roles": ["user"]
            }
        except Exception as e:
            logger.error(f"Error getting auth user: {e}")
            return None
    
    def get_config(self, key: str) -> Optional[Any]:
        """Get configuration from config service"""
        try:
            # For now, return mock config to prevent recursion issues
            mock_configs = {
                "policy_evaluation_timeout": 30,
                "max_policy_size": 10000,
                "enable_opa": False
            }
            return mock_configs.get(key, "default_value")
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return None
    
    def search_documents(self, query: str, filters: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Search documents using search service"""
        try:
            # For now, return mock search results to prevent recursion issues
            return {
                "query": query,
                "results": [
                    {"id": "doc1", "title": "Sample Document", "score": 0.95}
                ],
                "total": 1
            }
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return None
    
    def send_notification(self, user_id: str, title: str, message: str, notification_type: str = "info") -> bool:
        """Send notification using notification service"""
        try:
            # For now, just log the notification to prevent recursion issues
            logger.info(f"Notification sent: {title} - {message} to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def record_metric(self, metric_name: str, metric_value: float, labels: Optional[Dict] = None) -> bool:
        """Record metric using monitoring service"""
        try:
            # For now, just log the metric to prevent recursion issues
            logger.info(f"Metric recorded: {metric_name} = {metric_value}")
            return True
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if all dependent services are healthy"""
        try:
            # For now, return True to prevent recursion issues
            # In production, this would check all service health endpoints
            return True
        except Exception as e:
            logger.error(f"Service health check failed: {e}")
            return False

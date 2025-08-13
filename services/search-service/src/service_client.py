"""
Service Client for Search Service
Handles inter-service communication and external API calls.
"""

import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ServiceClient:
    """Client for communicating with other services."""
    
    def __init__(self):
        self.base_urls = {
            'policy': 'http://localhost:9001',
            'auth': 'http://localhost:9003',
            'config': 'http://localhost:9005',
            'health': 'http://localhost:9006',
            'etl': 'http://localhost:9007',
            'scraper': 'http://localhost:9008',
            'api_gateway': 'http://localhost:9009',
            'monitoring': 'http://localhost:9010',
            'plotly': 'http://localhost:9011',
            'mcp': 'http://localhost:9012',
            'op_import': 'http://localhost:9013'
        }
    
    async def get_auth_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from auth service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_urls['auth']}/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to get auth user: {e}")
        return None
    
    async def get_config(self, key: str) -> Optional[Dict[str, Any]]:
        """Get configuration from config service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_urls['config']}/config/{key}")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
        return None
    
    async def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search documents in the search index."""
        # This is a mock implementation for now
        return {
            "query": query,
            "results": [],
            "total": 0,
            "filters": filters or {}
        }
    
    async def send_notification(self, user_id: str, message: str) -> bool:
        """Send notification to user."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_urls['monitoring']}/notifications", json={
                    "user_id": user_id,
                    "message": message
                })
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    async def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_urls['monitoring']}/metrics", json={
                    "name": metric_name,
                    "value": value,
                    "tags": tags or {}
                })
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all dependent services."""
        health_status = {}
        
        for service_name, url in self.base_urls.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/healthz", timeout=5.0)
                    health_status[service_name] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "response_time": response.elapsed.total_seconds()
                    }
            except Exception as e:
                health_status[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status

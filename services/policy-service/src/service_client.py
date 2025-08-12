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
            'auth': os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8000'),
            'search': os.getenv('SEARCH_SERVICE_URL', 'http://search-service:8000'),
            'config': os.getenv('CONFIG_SERVICE_URL', 'http://config-service:8000'),
            'monitoring': os.getenv('MONITORING_SERVICE_URL', 'http://monitoring-service:8000'),
            'notification': os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:8000')
        }
        self.timeout = 30.0
    
    async def get_auth_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get authenticated user from auth service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_urls['auth']}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Auth service returned {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error communicating with auth service: {e}")
            return None
    
    async def get_config(self, key: str) -> Optional[Any]:
        """Get configuration from config service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_urls['config']}/config/{key}")
                if response.status_code == 200:
                    return response.json().get('value')
                else:
                    logger.warning(f"Config service returned {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error communicating with config service: {e}")
            return None
    
    async def search_documents(self, query: str, filters: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Search documents using search service"""
        try:
            params = {"query": query}
            if filters:
                params["filters"] = json.dumps(filters)
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_urls['search']}/search", params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Search service returned {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error communicating with search service: {e}")
            return None
    
    async def send_notification(self, user_id: str, title: str, message: str, notification_type: str = "info") -> bool:
        """Send notification using notification service"""
        try:
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_urls['notification']}/notifications/send",
                    json=notification_data
                )
                if response.status_code == 200:
                    return True
                else:
                    logger.warning(f"Notification service returned {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error communicating with notification service: {e}")
            return False
    
    async def record_metric(self, metric_name: str, metric_value: float, labels: Optional[Dict] = None) -> bool:
        """Record metric using monitoring service"""
        try:
            metric_data = {
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_type": "gauge",
                "service_name": "policy-service",
                "labels": labels or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_urls['monitoring']}/metrics",
                    json=metric_data
                )
                if response.status_code == 200:
                    return True
                else:
                    logger.warning(f"Monitoring service returned {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error communicating with monitoring service: {e}")
            return False
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all dependent services"""
        health_status = {}
        
        for service_name, base_url in self.base_urls.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{base_url}/healthz")
                    health_status[service_name] = response.status_code == 200
            except Exception:
                health_status[service_name] = False
        
        return health_status

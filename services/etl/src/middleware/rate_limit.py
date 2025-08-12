"""
Rate limiting middleware for the ETL service.
"""
import time
from typing import Callable, Dict, Tuple
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse

from config import get_settings
from core.logging import get_logger

# Get settings
settings = get_settings()

# In-memory rate limiting storage (use Redis in production)
rate_limit_storage: Dict[str, Tuple[int, float]] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.rate_limit")
        
        # Rate limiting configuration
        self.max_requests = settings.security.rate_limit_max_requests
        self.window_seconds = settings.security.rate_limit_window_seconds
        
        # Exempt paths from rate limiting
        self.exempt_paths = {
            "/healthz",
            "/healthz/detailed", 
            "/readyz",
            "/livez",
            "/metrics"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if path is exempt from rate limiting
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id):
            return self._rate_limit_exceeded_response(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self._get_remaining_requests(client_id))
        response.headers["X-RateLimit-Reset"] = str(self._get_reset_time(client_id))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get from X-Forwarded-For header (for proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP address
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Combine IP with user agent for better identification
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Create client ID hash
        client_id = f"{client_ip}:{hash(user_agent) % 10000}"
        
        return client_id
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        current_time = time.time()
        
        if client_id in rate_limit_storage:
            request_count, window_start = rate_limit_storage[client_id]
            
            # Check if window has expired
            if current_time - window_start > self.window_seconds:
                # Reset window
                rate_limit_storage[client_id] = (1, current_time)
                return True
            
            # Check if limit exceeded
            if request_count >= self.max_requests:
                return False
            
            # Increment request count
            rate_limit_storage[client_id] = (request_count + 1, window_start)
        else:
            # First request from this client
            rate_limit_storage[client_id] = (1, current_time)
        
        return True
    
    def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        if client_id in rate_limit_storage:
            request_count, window_start = rate_limit_storage[client_id]
            current_time = time.time()
            
            # Check if window has expired
            if current_time - window_start > self.window_seconds:
                return self.max_requests
            
            return max(0, self.max_requests - request_count)
        
        return self.max_requests
    
    def _get_reset_time(self, client_id: str) -> int:
        """Get reset time for client's rate limit window."""
        if client_id in rate_limit_storage:
            _, window_start = rate_limit_storage[client_id]
            return int(window_start + self.window_seconds)
        
        return int(time.time() + self.window_seconds)
    
    def _rate_limit_exceeded_response(self, client_id: str) -> Response:
        """Return rate limit exceeded response."""
        reset_time = self._get_reset_time(client_id)
        
        # Log rate limit violation
        self.logger.warning(
            f"Rate limit exceeded for client: {client_id}",
            extra={
                "client_id": client_id,
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "reset_time": reset_time
            }
        )
        
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Rate limit exceeded",
                "error": "TOO_MANY_REQUESTS",
                "details": {
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "reset_time": reset_time,
                    "retry_after": max(0, reset_time - int(time.time()))
                }
            },
            headers={
                "Retry-After": str(max(0, reset_time - int(time.time()))),
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time)
            }
        )
    
    def _cleanup_expired_entries(self):
        """Clean up expired rate limit entries."""
        current_time = time.time()
        expired_clients = []
        
        for client_id, (_, window_start) in rate_limit_storage.items():
            if current_time - window_start > self.window_seconds:
                expired_clients.append(client_id)
        
        for client_id in expired_clients:
            del rate_limit_storage[client_id]
        
        if expired_clients:
            self.logger.debug(f"Cleaned up {len(expired_clients)} expired rate limit entries")


class AdaptiveRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for adaptive rate limiting based on client behavior."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.adaptive_rate_limit")
        
        # Base rate limiting configuration
        self.base_max_requests = settings.security.rate_limit_requests
        self.base_window_seconds = settings.security.rate_limit_window
        
        # Adaptive rate limiting storage
        self.client_scores: Dict[str, float] = {}
        self.client_violations: Dict[str, int] = {}
        
        # Scoring thresholds
        self.good_behavior_threshold = 0.7
        self.bad_behavior_threshold = 0.3
        self.max_violations = 5
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Calculate adaptive limits
        max_requests, window_seconds = self._get_adaptive_limits(client_id)
        
        # Check rate limit with adaptive values
        if not self._check_adaptive_rate_limit(client_id, max_requests, window_seconds):
            return self._adaptive_rate_limit_exceeded_response(client_id, max_requests, window_seconds)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Update client score based on response
            self._update_client_score(client_id, response.status_code < 400)
            
            # Add adaptive rate limit headers
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Window"] = str(window_seconds)
            response.headers["X-RateLimit-Client-Score"] = str(self.client_scores.get(client_id, 1.0))
            
            return response
            
        except Exception as e:
            # Update client score negatively for errors
            self._update_client_score(client_id, False)
            raise
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Similar to basic rate limiting but with additional factors
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        user_agent = request.headers.get("user-agent", "unknown")
        api_key = request.headers.get("x-api-key", "none")
        
        # Create more sophisticated client ID
        client_id = f"{client_ip}:{hash(user_agent + api_key) % 10000}"
        
        return client_id
    
    def _get_adaptive_limits(self, client_id: str) -> Tuple[int, int]:
        """Get adaptive rate limit values for client."""
        score = self.client_scores.get(client_id, 1.0)
        violations = self.client_violations.get(client_id, 0)
        
        # Base limits
        max_requests = self.base_max_requests
        window_seconds = self.base_window_seconds
        
        # Adjust based on client score
        if score > self.good_behavior_threshold:
            # Good behavior: increase limits
            max_requests = int(max_requests * 1.5)
            window_seconds = max(60, int(window_seconds * 0.8))
        elif score < self.bad_behavior_threshold:
            # Bad behavior: decrease limits
            max_requests = max(10, int(max_requests * 0.5))
            window_seconds = int(window_seconds * 1.5)
        
        # Adjust based on violation count
        if violations > 0:
            violation_multiplier = max(0.1, 1.0 - (violations * 0.2))
            max_requests = max(5, int(max_requests * violation_multiplier))
            window_seconds = int(window_seconds * (1.0 + violations * 0.1))
        
        return max_requests, window_seconds
    
    def _check_adaptive_rate_limit(self, client_id: str, max_requests: int, window_seconds: int) -> bool:
        """Check adaptive rate limit."""
        current_time = time.time()
        
        # Use a more sophisticated storage key
        storage_key = f"{client_id}:{max_requests}:{window_seconds}"
        
        if storage_key in rate_limit_storage:
            request_count, window_start = rate_limit_storage[storage_key]
            
            if current_time - window_start > window_seconds:
                rate_limit_storage[storage_key] = (1, current_time)
                return True
            
            if request_count >= max_requests:
                return False
            
            rate_limit_storage[storage_key] = (request_count + 1, window_start)
        else:
            rate_limit_storage[storage_key] = (1, current_time)
        
        return True
    
    def _update_client_score(self, client_id: str, success: bool):
        """Update client behavior score."""
        current_score = self.client_scores.get(client_id, 1.0)
        
        if success:
            # Increase score for successful requests
            new_score = min(1.0, current_score + 0.01)
        else:
            # Decrease score for failed requests
            new_score = max(0.0, current_score - 0.05)
        
        self.client_scores[client_id] = new_score
        
        # Update violation count
        if not success:
            violations = self.client_violations.get(client_id, 0) + 1
            self.client_violations[client_id] = min(violations, self.max_violations)
    
    def _adaptive_rate_limit_exceeded_response(self, client_id: str, max_requests: int, window_seconds: int) -> Response:
        """Return adaptive rate limit exceeded response."""
        score = self.client_scores.get(client_id, 1.0)
        violations = self.client_violations.get(client_id, 0)
        
        # Log adaptive rate limit violation
        self.logger.warning(
            f"Adaptive rate limit exceeded for client: {client_id}",
            extra={
                "client_id": client_id,
                "limit": max_requests,
                "window_seconds": window_seconds,
                "client_score": score,
                "violations": violations
            }
        )
        
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Adaptive rate limit exceeded",
                "error": "ADAPTIVE_RATE_LIMIT_EXCEEDED",
                "details": {
                    "limit": max_requests,
                    "window_seconds": window_seconds,
                    "client_score": score,
                    "violations": violations,
                    "suggestions": self._get_rate_limit_suggestions(score, violations)
                }
            }
        )
    
    def _get_rate_limit_suggestions(self, score: float, violations: int) -> list:
        """Get suggestions for improving rate limit compliance."""
        suggestions = []
        
        if score < 0.5:
            suggestions.append("Reduce request frequency")
            suggestions.append("Implement proper error handling")
        
        if violations > 2:
            suggestions.append("Implement exponential backoff")
            suggestions.append("Review API usage patterns")
        
        if not suggestions:
            suggestions.append("Wait before making additional requests")
        
        return suggestions

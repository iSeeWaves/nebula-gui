"""Security middleware for FastAPI."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self' http://localhost:* http://127.0.0.1:*; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Remove server header
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.period
                }
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.calls - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=self.period)).timestamp()))
        
        return response


class LoginAttemptTracker:
    """Track failed login attempts and implement lockout."""
    
    def __init__(self, max_attempts: int = 5, lockout_duration: int = 900):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration  # seconds
        self.attempts = defaultdict(list)
        self.locked_accounts = {}
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt."""
        now = datetime.now()
        
        # Clean old attempts
        cutoff = now - timedelta(seconds=self.lockout_duration)
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if attempt_time > cutoff
        ]
        
        # Add current attempt
        self.attempts[identifier].append(now)
        
        # Check if account should be locked
        if len(self.attempts[identifier]) >= self.max_attempts:
            self.locked_accounts[identifier] = now + timedelta(seconds=self.lockout_duration)
    
    def is_locked(self, identifier: str) -> bool:
        """Check if an account is locked."""
        if identifier not in self.locked_accounts:
            return False
        
        # Check if lockout has expired
        if datetime.now() > self.locked_accounts[identifier]:
            del self.locked_accounts[identifier]
            self.attempts[identifier] = []
            return False
        
        return True
    
    def get_remaining_lockout_time(self, identifier: str) -> int:
        """Get remaining lockout time in seconds."""
        if identifier not in self.locked_accounts:
            return 0
        
        remaining = (self.locked_accounts[identifier] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def clear_attempts(self, identifier: str):
        """Clear all attempts for an identifier."""
        self.attempts[identifier] = []
        if identifier in self.locked_accounts:
            del self.locked_accounts[identifier]
    
    def get_attempt_count(self, identifier: str) -> int:
        """Get number of recent failed attempts."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.lockout_duration)
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if attempt_time > cutoff
        ]
        return len(self.attempts[identifier])


# Global instance
login_tracker = LoginAttemptTracker()


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware (optional)."""
    
    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
    
    async def dispatch(self, request: Request, call_next: Callable):
        if not self.whitelist:
            return await call_next(request)
        
        client_ip = request.client.host
        
        if client_ip not in self.whitelist:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )
        
        return await call_next(request)


class RequestHashingMiddleware(BaseHTTPMiddleware):
    """Add request integrity checking."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request ID
        request_id = hashlib.sha256(
            f"{request.client.host}{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Add to request state
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response
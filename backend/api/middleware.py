"""Middleware for rate limiting and request validation."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import re

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Input validation patterns
SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
IP_CIDR_PATTERN = re.compile(r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$')
NEBULA_IP_PATTERN = re.compile(r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$')

def validate_certificate_name(name: str) -> bool:
    """Validate certificate name format."""
    if not name or len(name) > 100:
        return False
    return bool(SAFE_STRING_PATTERN.match(name))

def validate_ip_cidr(ip: str) -> bool:
    """Validate IP/CIDR format."""
    if not IP_CIDR_PATTERN.match(ip):
        return False
    
    # Validate IP ranges
    parts = ip.split('/')
    ip_parts = parts[0].split('.')
    
    for part in ip_parts:
        if not 0 <= int(part) <= 255:
            return False
    
    # Validate CIDR
    cidr = int(parts[1])
    if not 0 <= cidr <= 32:
        return False
    
    return True

def validate_config_name(name: str) -> bool:
    """Validate configuration name."""
    if not name or len(name) > 100:
        return False
    return bool(SAFE_STRING_PATTERN.match(name))

async def validate_request_size(request: Request):
    """Limit request body size to prevent DoS."""
    body = await request.body()
    max_size = 10 * 1024 * 1024  # 10MB
    if len(body) > max_size:
        raise HTTPException(
            status_code=413,
            detail="Request body too large"
        )

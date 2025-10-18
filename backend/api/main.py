"""Main FastAPI application with enhanced security."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.database import init_db, SessionLocal, User
from core.security import get_password_hash
from core.config import settings
from core.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestHashingMiddleware
)
from api import auth, certificates, config, process, monitoring, audit, users
from api.middleware import limiter
from api import client_setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager with security initialization."""
    print("🚀 Starting Nebula GUI...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 Security features enabled")
    print(f"🔐 Encryption: {'Enabled' if settings.ENCRYPTION_KEY else 'Disabled (Warning!)'}")
    
    # Initialize database
    print("💾 Initializing database...")
    init_db()
    
    # Create default admin user if needed
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("👤 Creating default admin user...")
            admin_user = User(
                username="admin",
                email="admin@nebula.local",
                hashed_password=get_password_hash("Admin123!"),
                role="admin",
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created: username='admin', password='Admin123!'")
            print("⚠️  SECURITY WARNING: Please change the default password immediately!")
        else:
            print(f"✅ Database initialized with {user_count} users")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    finally:
        db.close()
    
    print("✅ Application startup complete")
    print("="*60)
    
    yield
    
    print("\n" + "="*60)
    print("👋 Shutting down Nebula GUI...")
    print("="*60)


app = FastAPI(
    title=settings.APP_NAME,
    description="Secure API for managing Nebula VPN with encryption and audit logging",
    version=settings.VERSION,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware (should be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # ← Fixed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,
)

# Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.RATE_LIMIT_PER_MINUTE,
    period=60
)
app.add_middleware(RequestHashingMiddleware)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions securely."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the error
    print(f"❌ Error [{request_id}]: {type(exc).__name__}: {str(exc)}")
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error. Please contact support.",
                "request_id": request_id
            }
        )
    else:
        # In development, show more details
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "request_id": request_id
            }
        )


# API routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(client_setup.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


# Static files (if exists)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Root endpoint
@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with rate limiting."""
    return {
        "message": "Nebula GUI API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
        "health": "/api/health",
        "security": {
            "encryption": "enabled" if settings.ENCRYPTION_KEY else "disabled",
            "rate_limiting": "enabled",
            "audit_logging": "enabled" if settings.ENABLE_AUDIT_LOG else "disabled"
        }
    }


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint with system status."""
    db = SessionLocal()
    try:
        # Test database connection
        user_count = db.query(User).count()
        db_status = "healthy"
    except Exception as e:
        user_count = None
        db_status = f"unhealthy: {str(e)}"
    finally:
        db.close()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "users": user_count,
        "security": {
            "encryption": "enabled" if settings.ENCRYPTION_KEY else "disabled",
            "rate_limiting": f"{settings.RATE_LIMIT_PER_MINUTE}/min"
        }
    }


# Security info endpoint (development only)
@app.get("/api/security-info")
@limiter.limit("5/minute")
async def security_info(request: Request):
    """Security information endpoint (development only)."""
    if settings.ENVIRONMENT != "development":
        return JSONResponse(
            status_code=403,
            content={"detail": "This endpoint is only available in development mode"}
        )
    
    return {
        "environment": settings.ENVIRONMENT,
        "encryption": {
            "enabled": bool(settings.ENCRYPTION_KEY),
            "private_keys": settings.ENCRYPT_PRIVATE_KEYS
        },
        "rate_limiting": {
            "global": f"{settings.RATE_LIMIT_PER_MINUTE}/min",
            "login_attempts": settings.MAX_LOGIN_ATTEMPTS,
            "lockout_duration": f"{settings.LOCKOUT_DURATION_MINUTES} minutes"
        },
        "jwt": {
            "algorithm": settings.ALGORITHM,
            "expiration": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
        },
        "password_policy": {
            "min_length": settings.MIN_PASSWORD_LENGTH,
            "require_uppercase": settings.REQUIRE_UPPERCASE,
            "require_lowercase": settings.REQUIRE_LOWERCASE,
            "require_digit": settings.REQUIRE_DIGIT,
            "require_special": settings.REQUIRE_SPECIAL_CHAR
        },
        "cors": {
            "allowed_origins": settings.ALLOWED_ORIGINS
        },
        "audit": {
            "enabled": settings.ENABLE_AUDIT_LOG
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 Starting Nebula GUI in direct mode")
    print("="*60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
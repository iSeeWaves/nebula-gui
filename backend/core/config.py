"""Security configuration and settings."""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # App Info
    APP_NAME: str = "Nebula GUI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "change-this-to-a-secure-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Encryption
    ENCRYPTION_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./nebula_gui.db"
    
    # CORS - will be parsed from comma-separated string
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Password Policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL_CHAR: bool = True
    
    # Session
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".crt", ".key", ".yaml", ".yml", ".conf"]
    
    # Certificate Storage
    CERT_STORAGE_PATH: str = "./certs"
    ENCRYPT_PRIVATE_KEYS: bool = True
    
    # Audit Logging
    ENABLE_AUDIT_LOG: bool = True
    LOG_RETENTION_DAYS: int = 90
    
    # Security Headers
    ENABLE_HSTS: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    ENABLE_CSP: bool = True
    ENABLE_X_FRAME_OPTIONS: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS


# Create settings instance
settings = Settings()


# Security validation
def validate_security_config():
    """Validate security configuration."""
    issues = []
    
    if settings.ENVIRONMENT == "production":
        # Check for default secret key
        if settings.SECRET_KEY == "change-this-to-a-secure-secret-key":
            issues.append("⚠️  SECRET_KEY is using default value! Generate a secure key!")
        
        # Check encryption key
        if not settings.ENCRYPTION_KEY:
            issues.append("⚠️  ENCRYPTION_KEY is not set! Private keys won't be encrypted!")
        
        # Check token expiration
        if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 10080:  # More than 7 days
            issues.append("⚠️  ACCESS_TOKEN_EXPIRE_MINUTES is too long for production!")
    
    if issues:
        print("\n" + "="*60)
        print("🔒 SECURITY CONFIGURATION WARNINGS")
        print("="*60)
        for issue in issues:
            print(issue)
        print("="*60 + "\n")
    else:
        print("✅ Security configuration validated successfully!")


# Run validation on import
validate_security_config()

"""Database configuration and models with enhanced logging and encryption."""
import os
from datetime import datetime
from typing import Generator, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nebula_gui.db")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model with role-based access control."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Security fields for future 2FA support
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)  # Encrypted
    
    certificates = relationship("Certificate", foreign_keys="[Certificate.created_by]", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", foreign_keys="[AuditLog.user_id]", back_populates="user")
    
    def set_2fa_secret(self, secret: str):
        """Set encrypted 2FA secret."""
        from core.config import settings
        if secret and settings.ENCRYPTION_KEY:
            from core.encryption import encrypt_data
            self.two_factor_secret = encrypt_data(secret)
        else:
            self.two_factor_secret = secret
    
    def get_2fa_secret(self) -> Optional[str]:
        """Get decrypted 2FA secret."""
        from core.config import settings
        if self.two_factor_secret and settings.ENCRYPTION_KEY:
            try:
                from core.encryption import decrypt_data
                return decrypt_data(self.two_factor_secret)
            except:
                return None
        return self.two_factor_secret


class Certificate(Base):
    """Certificate model with optional encryption for private keys."""
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    cert_type = Column(String(20), nullable=False)
    ip_address = Column(String(50), nullable=True)
    groups = Column(Text, nullable=True)
    is_ca = Column(Boolean, default=False)
    duration_hours = Column(Integer, default=8760)
    public_key = Column(Text, nullable=False)
    
    # Private key - can be encrypted if ENCRYPT_PRIVATE_KEYS is enabled
    _private_key = Column("private_key", Text, nullable=True)
    _is_encrypted = Column("is_encrypted", Boolean, default=False)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="certificates")
    
    @property
    def private_key(self) -> Optional[str]:
        """Get private key (decrypt if needed)."""
        if not self._private_key:
            return None
        
        from core.config import settings
        
        # If encryption is enabled and key is marked as encrypted
        if self._is_encrypted and settings.ENCRYPTION_KEY:
            try:
                from core.encryption import decrypt_data
                return decrypt_data(self._private_key)
            except Exception as e:
                print(f"Error decrypting private key for {self.name}: {e}")
                return self._private_key
        
        return self._private_key
    
    @private_key.setter
    def private_key(self, value: Optional[str]):
        """Set private key (encrypt if enabled)."""
        if not value:
            self._private_key = None
            self._is_encrypted = False
            return
        
        from core.config import settings
        
        # Encrypt if enabled
        if settings.ENCRYPT_PRIVATE_KEYS and settings.ENCRYPTION_KEY:
            try:
                from core.encryption import encrypt_data
                self._private_key = encrypt_data(value)
                self._is_encrypted = True
            except Exception as e:
                print(f"Error encrypting private key: {e}")
                self._private_key = value
                self._is_encrypted = False
        else:
            self._private_key = value
            self._is_encrypted = False


class NebulaConfig(Base):
    """Nebula configuration storage with optional encryption."""
    __tablename__ = "nebula_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Config data - can be encrypted if it contains sensitive info
    _config_data = Column("config_data", Text, nullable=False)
    _is_encrypted = Column("config_encrypted", Boolean, default=False)
    
    is_active = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def config_data(self) -> str:
        """Get config data (decrypt if needed)."""
        from core.config import settings
        
        if self._is_encrypted and settings.ENCRYPTION_KEY:
            try:
                from core.encryption import decrypt_data
                return decrypt_data(self._config_data)
            except Exception as e:
                print(f"Error decrypting config {self.name}: {e}")
                return self._config_data
        
        return self._config_data
    
    @config_data.setter
    def config_data(self, value: str):
        """Set config data (optionally encrypt)."""
        from core.config import settings
        
        # For now, we don't auto-encrypt configs by default
        # You can enable this if you want to encrypt all configs
        self._config_data = value
        self._is_encrypted = False


class NebulaProcess(Base):
    """Track running Nebula processes."""
    __tablename__ = "nebula_processes"
    
    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer, nullable=False, unique=True)
    config_name = Column(String(100), nullable=False)
    started_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")


class AuditLog(Base):
    """Enhanced audit log for tracking all actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    resource_name = Column(String(200), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")


class SessionToken(Base):
    """Session token model for better session management."""
    __tablename__ = "session_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
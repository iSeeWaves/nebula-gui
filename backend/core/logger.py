"""Centralized logging utility."""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from core.database import AuditLog

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("nebula_gui")


def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None
):
    """Log user action to database and system logs."""
    try:
        # Database log
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )
        
        db.add(audit_entry)
        db.commit()
        
        # System log
        log_msg = f"User {user_id} - {action} on {resource_type}"
        if resource_name:
            log_msg += f" '{resource_name}'"
        if status == "failed":
            log_msg += f" - FAILED: {error_message}"
        
        if status == "success":
            logger.info(log_msg)
        else:
            logger.error(log_msg)
            
    except Exception as e:
        logger.error(f"Failed to log action: {str(e)}")

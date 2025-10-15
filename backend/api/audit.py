"""Audit log endpoints."""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import get_db, AuditLog, User
from api.auth import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None  # ✅ Make optional
    username: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str]
    resource_name: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit logs with filtering (admin only)."""
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if status:
        query = query.filter(AuditLog.status == status)
    
    # Get logs with user info
    logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    # Enrich with username
    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else "Unknown",
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": log.resource_name,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "status": log.status,
            "error_message": log.error_message,
            "created_at": log.created_at
        }
        result.append(log_dict)
    
    return result


@router.get("/logs/my", response_model=List[AuditLogResponse])
async def get_my_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's audit logs."""
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == current_user.id
    ).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "username": current_user.username,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": log.resource_name,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "status": log.status,
            "error_message": log.error_message,
            "created_at": log.created_at
        }
        result.append(log_dict)
    
    return result


@router.get("/stats")
async def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit statistics (admin only)."""
    total_logs = db.query(AuditLog).count()
    failed_actions = db.query(AuditLog).filter(AuditLog.status == "failed").count()
    
    # Recent activity count
    from datetime import timedelta
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_activity = db.query(AuditLog).filter(AuditLog.created_at >= recent_cutoff).count()
    
    return {
        "total_logs": total_logs,
        "failed_actions": failed_actions,
        "recent_activity_24h": recent_activity
    }


@router.get("/actions")
async def get_available_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of unique actions in logs."""
    actions = db.query(AuditLog.action).distinct().all()
    return {"actions": [action[0] for action in actions]}


@router.get("/resources")
async def get_available_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of unique resource types in logs."""
    resources = db.query(AuditLog.resource_type).distinct().all()
    return {"resources": [resource[0] for resource in resources]}

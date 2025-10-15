"""Nebula process management endpoints."""
from typing import List, Optional
from datetime import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db, User, NebulaConfig, NebulaProcess
from core.nebula_manager import NebulaManager
from api.auth import get_current_active_user

router = APIRouter(prefix="/process", tags=["process"])

# Use local directory for testing if /etc/nebula is not writable
config_dir = os.path.expanduser("~/.nebula-gui/configs") if not os.access("/etc/nebula", os.W_OK) else "/etc/nebula"
nebula_manager = NebulaManager(config_dir=config_dir)


class ProcessStart(BaseModel):
    config_id: int


class ProcessStatus(BaseModel):
    running: bool
    config_name: str
    pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    started_at: Optional[str] = None
    status: Optional[str] = None


@router.post("/start")
async def start_nebula_process(
    process_data: ProcessStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start Nebula process."""
    config = db.query(NebulaConfig).filter(NebulaConfig.id == process_data.config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    result = nebula_manager.start_nebula(config.name, config.config_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to start Nebula")
        )
    
    db_process = NebulaProcess(
        pid=result["pid"],
        config_name=config.name,
        status="running"
    )
    
    db.add(db_process)
    db.commit()
    
    return {
        "message": f"Nebula started with config '{config.name}'",
        "pid": result["pid"],
        "started_at": result["started_at"]
    }


@router.post("/stop/{config_name}")
async def stop_nebula_process(
    config_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop Nebula process."""
    result = nebula_manager.stop_nebula(config_name)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to stop Nebula")
        )
    
    db_process = db.query(NebulaProcess).filter(
        NebulaProcess.config_name == config_name,
        NebulaProcess.status == "running"
    ).first()
    
    if db_process:
        db_process.status = "stopped"
        db_process.stopped_at = datetime.utcnow()
        db.commit()
    
    return {
        "message": result["message"],
        "stopped_at": result["stopped_at"]
    }


@router.get("/status/{config_name}", response_model=ProcessStatus)
async def get_process_status(
    config_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get process status."""
    status = nebula_manager.get_status(config_name)
    return status


@router.get("/status", response_model=List[ProcessStatus])
async def get_all_process_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get all process statuses."""
    statuses = nebula_manager.get_all_status()
    return statuses


@router.post("/stop-all")
async def stop_all_processes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop all processes."""
    result = nebula_manager.kill_all()
    
    db.query(NebulaProcess).filter(
        NebulaProcess.status == "running"
    ).update({
        "status": "stopped",
        "stopped_at": datetime.utcnow()
    })
    db.commit()
    
    return result

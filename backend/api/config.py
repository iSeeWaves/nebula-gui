"""Configuration management endpoints."""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db, NebulaConfig, User
from api.auth import get_current_active_user

router = APIRouter(prefix="/configs", tags=["configurations"])


class ConfigCreate(BaseModel):
    name: str
    config_data: str


class ConfigResponse(BaseModel):
    id: int
    name: str
    config_data: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new configuration."""
    # Check if name already exists
    existing = db.query(NebulaConfig).filter(NebulaConfig.name == config.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration with this name already exists"
        )
    
    db_config = NebulaConfig(
        name=config.name,
        config_data=config.config_data,
        is_active=False,
        created_by=current_user.id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/", response_model=List[ConfigResponse])
async def list_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all configurations."""
    configs = db.query(NebulaConfig).offset(skip).limit(limit).all()
    return configs


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific configuration."""
    config = db.query(NebulaConfig).filter(NebulaConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    return config


@router.post("/{config_id}/activate")
async def activate_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Activate a configuration (deactivates all others)."""
    config = db.query(NebulaConfig).filter(NebulaConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Deactivate all other configs
    db.query(NebulaConfig).update({NebulaConfig.is_active: False})
    
    # Activate this config
    config.is_active = True
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return {"message": "Configuration activated", "config": config}


@router.post("/{config_id}/deactivate")
async def deactivate_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate a configuration."""
    config = db.query(NebulaConfig).filter(NebulaConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    config.is_active = False
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return {"message": "Configuration deactivated", "config": config}


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a configuration."""
    config = db.query(NebulaConfig).filter(NebulaConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return None

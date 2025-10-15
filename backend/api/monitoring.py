import psutil
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.auth import get_current_active_user

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class SystemStats(BaseModel):
    cpu_percent: float
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    uptime_seconds: float
    timestamp: str


class NetworkStats(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int


@router.get("/system", response_model=SystemStats)
async def get_system_stats(current_user = Depends(get_current_active_user)):
    """Get system statistics."""
    cpu_percent = psutil.cpu_percent(interval=1)
    
    memory = psutil.virtual_memory()
    memory_total_mb = memory.total / 1024 / 1024
    memory_used_mb = memory.used / 1024 / 1024
    memory_percent = memory.percent
    
    disk = psutil.disk_usage('/')
    disk_total_gb = disk.total / 1024 / 1024 / 1024
    disk_used_gb = disk.used / 1024 / 1024 / 1024
    disk_percent = disk.percent
    
    boot_time = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot_time
    
    return SystemStats(
        cpu_percent=cpu_percent,
        memory_total_mb=memory_total_mb,
        memory_used_mb=memory_used_mb,
        memory_percent=memory_percent,
        disk_total_gb=disk_total_gb,
        disk_used_gb=disk_used_gb,
        disk_percent=disk_percent,
        uptime_seconds=uptime_seconds,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/network", response_model=NetworkStats)
async def get_network_stats(current_user = Depends(get_current_active_user)):
    """Get network statistics."""
    net_io = psutil.net_io_counters()
    
    return NetworkStats(
        bytes_sent=net_io.bytes_sent,
        bytes_recv=net_io.bytes_recv,
        packets_sent=net_io.packets_sent,
        packets_recv=net_io.packets_recv,
        errors_in=net_io.errin,
        errors_out=net_io.errout,
        drops_in=net_io.dropin,
        drops_out=net_io.dropout
    )


@router.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


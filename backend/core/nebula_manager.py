"""Nebula process management."""
import os
import signal
import subprocess
import psutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class NebulaManager:
    """Manage Nebula daemon processes."""
    
    def __init__(self, config_dir: str = "/etc/nebula", binary_path: str = None):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.nebula_binary = binary_path or self._find_nebula_binary()
        self.processes: Dict[str, int] = {}
    
    def _find_nebula_binary(self) -> str:
        """Find the nebula binary."""
        possible_paths = [
            "/usr/local/bin/nebula",
            "/usr/bin/nebula",
            "nebula"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        raise FileNotFoundError("nebula binary not found in system")
    
    def start_nebula(self, config_name: str, config_content: str, background: bool = True) -> Dict[str, Any]:
        """Start a Nebula instance."""
        try:
            config_path = self.config_dir / f"{config_name}.yaml"
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            if config_name in self.processes:
                pid = self.processes[config_name]
                if self.is_process_running(pid):
                    return {"success": False, "error": f"Instance already running", "pid": pid}
            
            cmd = [self.nebula_binary, "-config", str(config_path)]
            
            if background:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                pid = process.pid
            else:
                process = subprocess.run(cmd, capture_output=True, text=True)
                return {"success": process.returncode == 0, "output": process.stdout, "error": process.stderr}
            
            self.processes[config_name] = pid
            
            import time
            time.sleep(1)
            
            if not self.is_process_running(pid):
                return {"success": False, "error": "Process failed to start", "pid": pid}
            
            return {"success": True, "pid": pid, "config_name": config_name, "started_at": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"success": False, "error": f"Failed to start: {str(e)}"}
    
    def stop_nebula(self, config_name: str) -> Dict[str, Any]:
        """Stop a Nebula instance."""
        try:
            if config_name not in self.processes:
                return {"success": False, "error": f"No instance found"}
            
            pid = self.processes[config_name]
            
            if not self.is_process_running(pid):
                del self.processes[config_name]
                return {"success": False, "error": f"Process not running"}
            
            try:
                os.kill(pid, signal.SIGTERM)
                import time
                for _ in range(10):
                    time.sleep(1)
                    if not self.is_process_running(pid):
                        break
                if self.is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)
            except ProcessLookupError:
                pass
            
            del self.processes[config_name]
            return {"success": True, "message": f"Stopped", "stopped_at": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"success": False, "error": f"Failed to stop: {str(e)}"}
    
    def get_status(self, config_name: str) -> Dict[str, Any]:
        """Get status."""
        if config_name not in self.processes:
            return {"running": False, "config_name": config_name}
        
        pid = self.processes[config_name]
        running = self.is_process_running(pid)
        
        if not running:
            del self.processes[config_name]
            return {"running": False, "config_name": config_name}
        
        try:
            process = psutil.Process(pid)
            return {
                "running": True,
                "config_name": config_name,
                "pid": pid,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "started_at": datetime.fromtimestamp(process.create_time()).isoformat(),
                "status": process.status()
            }
        except psutil.NoSuchProcess:
            del self.processes[config_name]
            return {"running": False, "config_name": config_name}
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get all statuses."""
        statuses = []
        for config_name in list(self.processes.keys()):
            statuses.append(self.get_status(config_name))
        return statuses
    
    def is_process_running(self, pid: int) -> bool:
        """Check if process is running."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False
    
    def kill_all(self) -> Dict[str, Any]:
        """Stop all instances."""
        results = []
        for config_name in list(self.processes.keys()):
            result = self.stop_nebula(config_name)
            results.append({"config_name": config_name, "result": result})
        return {"success": True, "stopped_count": len(results), "results": results}

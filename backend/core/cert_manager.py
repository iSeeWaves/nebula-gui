"""Certificate management for Nebula."""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any


class CertificateManager:
    """Manage Nebula certificates using nebula-cert command."""
    
    def __init__(self, cert_dir: str = "/tmp/nebula-certs"):
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        self.nebula_cert_cmd = self._find_nebula_cert()
    
    def _find_nebula_cert(self) -> str:
        """Find the nebula-cert binary."""
        possible_paths = [
            "/usr/local/bin/nebula-cert",
            "/usr/bin/nebula-cert",
            "nebula-cert"
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
        
        raise FileNotFoundError("nebula-cert binary not found in system")
    
    def create_ca(self, name: str, duration_hours: int = 87600) -> Dict[str, str]:
        """Create a Certificate Authority."""
        try:
            ca_crt_path = self.cert_dir / f"{name}.crt"
            ca_key_path = self.cert_dir / f"{name}.key"
            
            cmd = [
                self.nebula_cert_cmd,
                "ca",
                "-name", name,
                "-duration", f"{duration_hours}h",
                "-out-crt", str(ca_crt_path),
                "-out-key", str(ca_key_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create CA: {result.stderr}")
            
            with open(ca_crt_path, 'r') as f:
                cert_content = f.read()
            
            with open(ca_key_path, 'r') as f:
                key_content = f.read()
            
            return {
                "cert": cert_content,
                "key": key_content,
                "cert_path": str(ca_crt_path),
                "key_path": str(ca_key_path)
            }
        
        except subprocess.TimeoutExpired:
            raise RuntimeError("CA creation timed out")
        except Exception as e:
            raise RuntimeError(f"Error creating CA: {str(e)}")
    
    def sign_certificate(
        self,
        name: str,
        ip: str,
        ca_cert_path: str,
        ca_key_path: str,
        groups: Optional[List[str]] = None,
        duration_hours: int = 8760
    ) -> Dict[str, str]:
        """Sign a host or client certificate."""
        try:
            cert_path = self.cert_dir / f"{name}.crt"
            key_path = self.cert_dir / f"{name}.key"
            
            cmd = [
                self.nebula_cert_cmd,
                "sign",
                "-name", name,
                "-ip", ip,
                "-ca-crt", ca_cert_path,
                "-ca-key", ca_key_path,
                "-duration", f"{duration_hours}h",
                "-out-crt", str(cert_path),
                "-out-key", str(key_path)
            ]
            
            if groups:
                for group in groups:
                    cmd.extend(["-groups", group])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to sign certificate: {result.stderr}")
            
            with open(cert_path, 'r') as f:
                cert_content = f.read()
            
            with open(key_path, 'r') as f:
                key_content = f.read()
            
            return {
                "cert": cert_content,
                "key": key_content,
                "cert_path": str(cert_path),
                "key_path": str(key_path)
            }
        
        except subprocess.TimeoutExpired:
            raise RuntimeError("Certificate signing timed out")
        except Exception as e:
            raise RuntimeError(f"Error signing certificate: {str(e)}")
    
    def save_certificate_files(
        self,
        name: str,
        cert_content: str,
        key_content: Optional[str] = None
    ) -> Dict[str, str]:
        """Save certificate and key to files."""
        try:
            cert_path = self.cert_dir / f"{name}.crt"
            
            with open(cert_path, 'w') as f:
                f.write(cert_content)
            
            result = {"cert_path": str(cert_path)}
            
            if key_content:
                key_path = self.cert_dir / f"{name}.key"
                with open(key_path, 'w') as f:
                    f.write(key_content)
                
                os.chmod(key_path, 0o600)
                result["key_path"] = str(key_path)
            
            return result
        
        except Exception as e:
            raise RuntimeError(f"Error saving certificate files: {str(e)}")

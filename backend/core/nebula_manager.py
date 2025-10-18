"""Nebula VPN Manager - Real Nebula binary integration."""
import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from core.config import settings


class NebulaManager:
    """Manager for Nebula VPN operations using real nebula binaries."""
    
    def __init__(self):
        self.nebula_bin = "/usr/local/bin/nebula"
        self.nebula_cert_bin = "/usr/local/bin/nebula-cert"
        self.cert_dir = Path(settings.CERT_STORAGE_PATH)
        self.config_dir = Path("/etc/nebula/configs")
        
        # Create directories if they don't exist
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def check_nebula_installed(self) -> bool:
        """Check if Nebula binaries are installed."""
        try:
            result = subprocess.run(
                [self.nebula_bin, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def create_ca(
        self,
        name: str,
        duration_hours: int = 87600,  # 10 years default
        groups: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Create a new Certificate Authority.
        
        Args:
            name: CA name
            duration_hours: Certificate validity in hours
            groups: Optional list of groups
            
        Returns:
            Dictionary with ca_cert and ca_key paths
        """
        ca_cert_path = self.cert_dir / f"{name}.crt"
        ca_key_path = self.cert_dir / f"{name}.key"
        
        cmd = [
            self.nebula_cert_bin,
            "ca",
            "-name", name,
            "-duration", f"{duration_hours}h",
            "-out-crt", str(ca_cert_path),
            "-out-key", str(ca_key_path)
        ]
        
        if groups:
            cmd.extend(["-groups", ",".join(groups)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"CA creation failed: {result.stderr}")
            
            # Read the generated files
            with open(ca_cert_path, 'r') as f:
                ca_cert = f.read()
            
            with open(ca_key_path, 'r') as f:
                ca_key = f.read()
            
            return {
                "ca_cert": ca_cert,
                "ca_key": ca_key,
                "ca_cert_path": str(ca_cert_path),
                "ca_key_path": str(ca_key_path)
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("CA creation timed out")
        except Exception as e:
            raise Exception(f"Failed to create CA: {str(e)}")
    
    def sign_certificate(
        self,
        name: str,
        ip: str,
        ca_name: str,
        duration_hours: int = 8760,  # 1 year default
        groups: Optional[List[str]] = None,
        subnets: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Sign a host certificate.
        
        Args:
            name: Host name
            ip: IP address in CIDR format (e.g., 192.168.100.1/24)
            ca_name: CA name to use for signing
            duration_hours: Certificate validity in hours
            groups: Optional list of groups
            subnets: Optional list of unsafe routes
            
        Returns:
            Dictionary with host_cert and host_key
        """
        ca_cert_path = self.cert_dir / f"{ca_name}.crt"
        ca_key_path = self.cert_dir / f"{ca_name}.key"
        host_cert_path = self.cert_dir / f"{name}.crt"
        host_key_path = self.cert_dir / f"{name}.key"
        
        # Verify CA exists
        if not ca_cert_path.exists() or not ca_key_path.exists():
            raise Exception(f"CA '{ca_name}' not found")
        
        cmd = [
            self.nebula_cert_bin,
            "sign",
            "-name", name,
            "-ip", ip,
            "-ca-crt", str(ca_cert_path),
            "-ca-key", str(ca_key_path),
            "-duration", f"{duration_hours}h",
            "-out-crt", str(host_cert_path),
            "-out-key", str(host_key_path)
        ]
        
        if groups:
            cmd.extend(["-groups", ",".join(groups)])
        
        if subnets:
            for subnet in subnets:
                cmd.extend(["-subnets", subnet])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Certificate signing failed: {result.stderr}")
            
            # Read the generated files
            with open(host_cert_path, 'r') as f:
                host_cert = f.read()
            
            with open(host_key_path, 'r') as f:
                host_key = f.read()
            
            return {
                "host_cert": host_cert,
                "host_key": host_key,
                "host_cert_path": str(host_cert_path),
                "host_key_path": str(host_key_path)
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("Certificate signing timed out")
        except Exception as e:
            raise Exception(f"Failed to sign certificate: {str(e)}")
    
    def print_certificate(self, cert_path: str) -> Dict[str, Any]:
        """
        Get certificate information.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Dictionary with certificate details
        """
        cmd = [
            self.nebula_cert_bin,
            "print",
            "-json",
            "-path", cert_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to read certificate: {result.stderr}")
            
            return json.loads(result.stdout)
            
        except Exception as e:
            raise Exception(f"Failed to get certificate info: {str(e)}")
    
    def create_config(
        self,
        name: str,
        ca_cert_path: str,
        host_cert_path: str,
        host_key_path: str,
        lighthouse_hosts: List[str] = None,
        static_host_map: Dict[str, List[str]] = None,
        listen_port: int = 4242,
        punchy: bool = True,
        cipher: str = "aes",
        local_range: str = "192.168.100.0/24",
        unsafe_routes: List[Dict[str, str]] = None,
        firewall_outbound: List[Dict[str, Any]] = None,
        firewall_inbound: List[Dict[str, Any]] = None
    ) -> str:
        """
        Create a Nebula configuration file.
        
        Returns:
            Path to the created config file
        """
        config = {
            "pki": {
                "ca": ca_cert_path,
                "cert": host_cert_path,
                "key": host_key_path
            },
            "static_host_map": static_host_map or {},
            "lighthouse": {
                "am_lighthouse": False,
                "interval": 60,
                "hosts": lighthouse_hosts or []
            },
            "listen": {
                "host": "0.0.0.0",
                "port": listen_port
            },
            "punchy": {
                "punch": punchy,
                "respond": True
            },
            "cipher": cipher,
            "local_range": local_range,
            "tun": {
                "disabled": False,
                "dev": "nebula1",
                "drop_local_broadcast": False,
                "drop_multicast": False,
                "tx_queue": 500,
                "mtu": 1300
            },
            "logging": {
                "level": "info",
                "format": "text"
            },
            "firewall": {
                "conntrack": {
                    "tcp_timeout": "12m",
                    "udp_timeout": "3m",
                    "default_timeout": "10m"
                },
                "outbound": firewall_outbound or [
                    {"port": "any", "proto": "any", "host": "any"}
                ],
                "inbound": firewall_inbound or [
                    {"port": "any", "proto": "icmp", "host": "any"}
                ]
            }
        }
        
        if unsafe_routes:
            config["tun"]["unsafe_routes"] = unsafe_routes
        
        config_path = self.config_dir / f"{name}.yaml"
        
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return str(config_path)
    
    def start_nebula(self, config_path: str) -> int:
        """
        Start Nebula with the given configuration.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Process ID
        """
        if not os.path.exists(config_path):
            raise Exception(f"Config file not found: {config_path}")
        
        cmd = [
            self.nebula_bin,
            "-config", config_path
        ]
        
        try:
            # Start Nebula in the background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return process.pid
            
        except Exception as e:
            raise Exception(f"Failed to start Nebula: {str(e)}")
    
    def stop_nebula(self, pid: int) -> bool:
        """
        Stop a running Nebula process.
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful
        """
        try:
            import signal
            os.kill(pid, signal.SIGTERM)
            return True
        except ProcessLookupError:
            return False
        except Exception as e:
            raise Exception(f"Failed to stop Nebula: {str(e)}")
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process is running."""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def get_nebula_version(self) -> str:
        """Get Nebula version."""
        try:
            result = subprocess.run(
                [self.nebula_bin, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "Unknown"


# Global instance
nebula_manager = NebulaManager()

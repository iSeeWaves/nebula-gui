"""Nebula configuration parser and validator."""
import yaml
from typing import Dict, Any, List, Optional


class NebulaConfigParser:
    """Parse and validate Nebula configuration files."""
    
    REQUIRED_FIELDS = ["pki", "static_host_map", "lighthouse", "listen", "punchy", "tun"]
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.errors: List[str] = []
    
    def parse_file(self, file_path: str) -> bool:
        """Parse configuration from a YAML file."""
        try:
            with open(file_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return self.validate()
        except FileNotFoundError:
            self.errors.append(f"Configuration file not found: {file_path}")
            return False
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error parsing config: {str(e)}")
            return False
    
    def parse_string(self, config_str: str) -> bool:
        """Parse configuration from a YAML string."""
        try:
            self.config = yaml.safe_load(config_str)
            return self.validate()
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error parsing config: {str(e)}")
            return False
    
    def validate(self) -> bool:
        """Validate the configuration structure."""
        self.errors = []
        
        if not isinstance(self.config, dict):
            self.errors.append("Configuration must be a dictionary")
            return False
        
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                self.errors.append(f"Missing required field: {field}")
        
        if "pki" in self.config:
            pki = self.config["pki"]
            if not isinstance(pki, dict):
                self.errors.append("PKI section must be a dictionary")
            else:
                if "ca" not in pki:
                    self.errors.append("PKI section missing 'ca' field")
                if "cert" not in pki:
                    self.errors.append("PKI section missing 'cert' field")
                if "key" not in pki:
                    self.errors.append("PKI section missing 'key' field")
        
        if "lighthouse" in self.config:
            lighthouse = self.config["lighthouse"]
            if not isinstance(lighthouse, dict):
                self.errors.append("Lighthouse section must be a dictionary")
            else:
                if "am_lighthouse" not in lighthouse:
                    self.errors.append("Lighthouse section missing 'am_lighthouse' field")
        
        if "listen" in self.config:
            listen = self.config["listen"]
            if not isinstance(listen, dict):
                self.errors.append("Listen section must be a dictionary")
            else:
                if "host" not in listen:
                    self.errors.append("Listen section missing 'host' field")
                if "port" not in listen:
                    self.errors.append("Listen section missing 'port' field")
        
        return len(self.errors) == 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get the parsed configuration."""
        return self.config
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors
    
    def to_yaml(self) -> str:
        """Convert configuration back to YAML string."""
        return yaml.dump(self.config, default_flow_style=False)
    
    def set_pki_paths(self, ca_path: str, cert_path: str, key_path: str):
        """Set PKI certificate paths in the configuration."""
        if "pki" not in self.config:
            self.config["pki"] = {}
        
        self.config["pki"]["ca"] = ca_path
        self.config["pki"]["cert"] = cert_path
        self.config["pki"]["key"] = key_path
    
    def set_listen_port(self, host: str = "0.0.0.0", port: int = 4242):
        """Set listen address and port."""
        if "listen" not in self.config:
            self.config["listen"] = {}
        
        self.config["listen"]["host"] = host
        self.config["listen"]["port"] = port
    
    def set_lighthouse(self, am_lighthouse: bool, hosts: Optional[List[str]] = None):
        """Configure lighthouse settings."""
        if "lighthouse" not in self.config:
            self.config["lighthouse"] = {}
        
        self.config["lighthouse"]["am_lighthouse"] = am_lighthouse
        
        if hosts is not None:
            self.config["lighthouse"]["hosts"] = hosts
    
    def add_static_host(self, nebula_ip: str, public_addresses: List[str]):
        """Add a static host mapping."""
        if "static_host_map" not in self.config:
            self.config["static_host_map"] = {}
        
        self.config["static_host_map"][nebula_ip] = public_addresses
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create a default Nebula configuration."""
        self.config = {
            "pki": {
                "ca": "/etc/nebula/ca.crt",
                "cert": "/etc/nebula/host.crt",
                "key": "/etc/nebula/host.key"
            },
            "static_host_map": {},
            "lighthouse": {
                "am_lighthouse": False,
                "interval": 60,
                "hosts": []
            },
            "listen": {
                "host": "0.0.0.0",
                "port": 4242
            },
            "punchy": {
                "punch": True,
                "respond": True
            },
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
                "outbound": [
                    {"port": "any", "proto": "any", "host": "any"}
                ],
                "inbound": [
                    {"port": "any", "proto": "any", "host": "any"}
                ]
            }
        }
        return self.config

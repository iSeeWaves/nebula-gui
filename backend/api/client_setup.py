"""Client setup and provisioning endpoints - NEW FEATURE."""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import secrets
import zipfile
import io
import json
import qrcode
from pathlib import Path

from core.database import get_db, User, Certificate
from api.auth import get_current_active_user
from core.logger import log_action
from core.cert_manager import CertificateManager

router = APIRouter(prefix="/client-setup", tags=["client-setup"])

cert_manager = CertificateManager()


class ClientProvisionRequest(BaseModel):
    """Request to provision a new client device."""
    device_name: str
    device_type: str  # windows, macos, linux, android, ios
    ip_address: str  # Auto-assigned if empty
    ca_id: int
    auto_connect: bool = True


class ProvisionToken(BaseModel):
    """Temporary token for client provisioning."""
    token: str
    expires_at: datetime
    device_name: str
    download_url: str


@router.post("/provision", response_model=ProvisionToken)
async def provision_client_device(
    request: Request,
    provision_data: ClientProvisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a one-time provisioning token for a client device.
    
    Returns a token that can be used to download pre-configured client package.
    """
    # Get CA certificate
    ca_cert = db.query(Certificate).filter(
        Certificate.id == provision_data.ca_id,
        Certificate.is_ca == True
    ).first()
    
    if not ca_cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA certificate not found"
        )
    
    # Auto-assign IP if not provided
    if not provision_data.ip_address:
        # Find next available IP in range
        last_cert = db.query(Certificate).filter(
            Certificate.ip_address.like("192.168.100.%")
        ).order_by(Certificate.id.desc()).first()
        
        if last_cert and last_cert.ip_address:
            last_ip = int(last_cert.ip_address.split('.')[3].split('/')[0])
            next_ip = last_ip + 1
        else:
            next_ip = 10  # Start from .10
        
        provision_data.ip_address = f"192.168.100.{next_ip}/24"
    
    # Generate one-time token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Store token in session (you might want a separate table for this)
    # For now, we'll encode it in the token itself
    token_data = {
        "device_name": provision_data.device_name,
        "device_type": provision_data.device_type,
        "ip_address": provision_data.ip_address,
        "ca_id": provision_data.ca_id,
        "user_id": current_user.id,
        "expires_at": expires_at.isoformat(),
        "auto_connect": provision_data.auto_connect
    }
    
    # Save to temp storage (implement proper storage later)
    token_file = Path(f"/tmp/nebula-tokens/{token}.json")
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(json.dumps(token_data))
    
    # Generate download URL
    download_url = f"/api/client-setup/download/{token}"
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        action="client_provision_token_created",
        resource_type="client",
        resource_name=provision_data.device_name,
        details=f"Token created for {provision_data.device_type} device",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return ProvisionToken(
        token=token,
        expires_at=expires_at,
        device_name=provision_data.device_name,
        download_url=download_url
    )


@router.get("/download/{token}")
async def download_client_package(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Download pre-configured client package using one-time token.
    
    Returns a ZIP file containing:
    - Nebula binary
    - Certificate files
    - Pre-configured config.yaml
    - Installation script
    """
    # Load token data
    token_file = Path(f"/tmp/nebula-tokens/{token}.json")
    
    if not token_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    token_data = json.loads(token_file.read_text())
    
    # Check expiration
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.utcnow() > expires_at:
        token_file.unlink()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Token expired"
        )
    
    # Get CA certificate
    ca_cert = db.query(Certificate).filter(
        Certificate.id == token_data["ca_id"]
    ).first()
    
    if not ca_cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CA certificate not found"
        )
    
    # Create client certificate
    try:
        # Sign certificate
        result = cert_manager.sign_certificate(
            name=token_data["device_name"],
            ip=token_data["ip_address"],
            ca_cert_path=f"/tmp/nebula-certs/{ca_cert.name}.crt",
            ca_key_path=f"/tmp/nebula-certs/{ca_cert.name}.key",
            groups=["clients"],
            duration_hours=8760  # 1 year
        )
        
        # Save to database
        new_cert = Certificate(
            name=token_data["device_name"],
            cert_type="host",
            ip_address=token_data["ip_address"],
            groups="clients",
            is_ca=False,
            duration_hours=8760,
            public_key=result["cert"],
            private_key=result["key"],
            created_by=token_data["user_id"],
            expires_at=datetime.utcnow() + timedelta(hours=8760)
        )
        db.add(new_cert)
        db.commit()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create certificate: {str(e)}"
        )
    
    # Generate configuration
    config = generate_client_config(
        device_name=token_data["device_name"],
        ip_address=token_data["ip_address"],
        auto_connect=token_data["auto_connect"]
    )
    
    # Create ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add certificates
        zip_file.writestr(f"{token_data['device_name']}/ca.crt", ca_cert.public_key)
        zip_file.writestr(f"{token_data['device_name']}/host.crt", result["cert"])
        zip_file.writestr(f"{token_data['device_name']}/host.key", result["key"])
        
        # Add config
        zip_file.writestr(f"{token_data['device_name']}/config.yaml", config)
        
        # Add installation script
        install_script = generate_install_script(token_data["device_type"])
        zip_file.writestr(f"{token_data['device_name']}/install.sh", install_script)
        
        # Add README
        readme = generate_readme(token_data["device_name"], token_data["device_type"])
        zip_file.writestr(f"{token_data['device_name']}/README.md", readme)
    
    # Delete token (one-time use)
    token_file.unlink()
    
    # Log download
    log_action(
        db=db,
        user_id=token_data["user_id"],
        action="client_package_downloaded",
        resource_type="client",
        resource_name=token_data["device_name"],
        details=f"Client package downloaded for {token_data['device_type']}",
        ip_address="unknown",  # Can't get from here
        user_agent="unknown"
    )
    
    # Return ZIP file
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={token_data['device_name']}-nebula-client.zip"
        }
    )


@router.get("/qr-code/{token}")
async def generate_qr_code_for_token(token: str):
    """
    Generate QR code for mobile device provisioning.
    
    Mobile app can scan this QR code to auto-configure.
    """
    token_file = Path(f"/tmp/nebula-tokens/{token}.json")
    
    if not token_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    # Generate QR code with simple download URL
    download_url = f"http://localhost:8000/api/client-setup/download/{token}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return StreamingResponse(
        img_buffer,
        media_type="image/png",
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "image/png"
        }
    )


def generate_client_config(device_name: str, ip_address: str, auto_connect: bool) -> str:
    """Generate Nebula configuration for client."""
    config = f"""# Nebula VPN Configuration for {device_name}
# Auto-generated by Nebula GUI

pki:
  ca: ca.crt
  cert: host.crt
  key: host.key

static_host_map:
  "192.168.100.1": ["YOUR_LIGHTHOUSE_IP:4242"]

lighthouse:
  am_lighthouse: false
  interval: 60
  hosts:
    - "192.168.100.1"

listen:
  host: 0.0.0.0
  port: 0

punchy:
  punch: true
  respond: true

tun:
  dev: nebula1
  drop_local_broadcast: false
  drop_multicast: false
  tx_queue: 500
  mtu: 1300

logging:
  level: info
  format: text

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m
  
  outbound:
    - port: any
      proto: any
      host: any
  
  inbound:
    - port: any
      proto: icmp
      host: any
    - port: any
      proto: tcp
      host: any
    - port: any
      proto: udp
      host: any
"""
    return config


def generate_install_script(device_type: str) -> str:
    """Generate installation script for device type."""
    if device_type == "linux":
        return """#!/bin/bash
# Nebula VPN Installation Script

set -e

echo "🚀 Installing Nebula VPN..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Download Nebula binary if not present
if ! command -v nebula &> /dev/null; then
    echo "Downloading Nebula binary..."
    wget https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-linux-amd64.tar.gz
    tar -xzf nebula-linux-amd64.tar.gz
    mv nebula /usr/local/bin/
    chmod +x /usr/local/bin/nebula
fi

# Copy certificates
mkdir -p /etc/nebula
cp ca.crt /etc/nebula/
cp host.crt /etc/nebula/
cp host.key /etc/nebula/
cp config.yaml /etc/nebula/
chmod 600 /etc/nebula/host.key

# Create systemd service
cat > /etc/systemd/system/nebula.service << 'SERVICE'
[Unit]
Description=Nebula VPN
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/nebula -config /etc/nebula/config.yaml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# Start service
systemctl daemon-reload
systemctl enable nebula
systemctl start nebula

echo "✅ Nebula VPN installed and started!"
echo "Check status: sudo systemctl status nebula"
"""
    
    elif device_type == "macos":
        return """#!/bin/bash
# Nebula VPN Installation Script for macOS

set -e

echo "🚀 Installing Nebula VPN..."

# Download Nebula binary
if ! command -v nebula &> /dev/null; then
    echo "Downloading Nebula binary..."
    curl -LO https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-darwin.tar.gz
    tar -xzf nebula-darwin.tar.gz
    sudo mv nebula /usr/local/bin/
    sudo chmod +x /usr/local/bin/nebula
fi

# Copy certificates
sudo mkdir -p /etc/nebula
sudo cp ca.crt /etc/nebula/
sudo cp host.crt /etc/nebula/
sudo cp host.key /etc/nebula/
sudo cp config.yaml /etc/nebula/
sudo chmod 600 /etc/nebula/host.key

# Create LaunchDaemon
sudo cat > /Library/LaunchDaemons/com.nebula.vpn.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nebula.vpn</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/nebula</string>
        <string>-config</string>
        <string>/etc/nebula/config.yaml</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
PLIST

# Load and start
sudo launchctl load /Library/LaunchDaemons/com.nebula.vpn.plist

echo "✅ Nebula VPN installed and started!"
echo "Check status: sudo launchctl list | grep nebula"
"""
    
    else:  # Windows
        return """@echo off
REM Nebula VPN Installation Script for Windows

echo Installing Nebula VPN...

REM Download Nebula binary
if not exist "C:\\Program Files\\Nebula\\nebula.exe" (
    echo Downloading Nebula binary...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-windows-amd64.zip' -OutFile 'nebula.zip'"
    powershell -Command "Expand-Archive -Path 'nebula.zip' -DestinationPath 'C:\\Program Files\\Nebula\\'"
)

REM Copy certificates
mkdir "C:\\Program Files\\Nebula\\config"
copy ca.crt "C:\\Program Files\\Nebula\\config\\"
copy host.crt "C:\\Program Files\\Nebula\\config\\"
copy host.key "C:\\Program Files\\Nebula\\config\\"
copy config.yaml "C:\\Program Files\\Nebula\\config\\"

REM Create Windows service
sc create NebulaVPN binPath= "C:\\Program Files\\Nebula\\nebula.exe -config C:\\Program Files\\Nebula\\config\\config.yaml" start= auto
sc start NebulaVPN

echo Nebula VPN installed and started!
echo Check status: sc query NebulaVPN
pause
"""


def generate_readme(device_name: str, device_type: str) -> str:
    """Generate README for client package."""
    return f"""# Nebula VPN Client Package - {device_name}

This package contains everything you need to connect to your Nebula VPN.

## Contents

- `ca.crt` - Certificate Authority certificate
- `host.crt` - Your device certificate
- `host.key` - Your device private key (keep this secret!)
- `config.yaml` - Nebula configuration
- `install.sh` - Installation script

## Quick Start

### Linux/macOS:
```bash
chmod +x install.sh
sudo ./install.sh
```

### Windows:
Run `install.bat` as Administrator

## Manual Installation

1. Install Nebula binary from: https://github.com/slackhq/nebula/releases
2. Copy all files to `/etc/nebula/` (Linux/Mac) or `C:\\Program Files\\Nebula\\` (Windows)
3. Run: `nebula -config /etc/nebula/config.yaml`

## Verify Connection

After installation, you should be able to ping other devices on the VPN:
```bash
ping 192.168.100.1
```

## Support

For help, contact your VPN administrator or visit: https://your-domain.com/docs

## Security Note

⚠️ Keep your `host.key` file secure! Never share it with anyone.
"""


@router.get("/status/{device_name}")
async def get_client_status(
    device_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if a client device is currently connected."""
    # This would integrate with your monitoring system
    # For now, return placeholder
    return {
        "device_name": device_name,
        "status": "unknown",
        "last_seen": None,
        "ip_address": None
    }

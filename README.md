# Nebula GUI Backend - Complete Setup Guide

## 📁 File Structure

Create these files in your `backend/` directory:

```
backend/
├── api/
│   ├── __init__.py          # Empty file
│   ├── main.py              # Main FastAPI application
│   ├── auth.py              # Authentication endpoints
│   ├── certificates.py      # Certificate management
│   ├── config.py            # Configuration management
│   ├── process.py           # Process management
│   ├── monitoring.py        # System monitoring
│   ├── audit.py             # Audit logging
│   └── users.py             # User management
├── core/
│   ├── __init__.py          # Core module exports
│   ├── database.py          # Database models
│   ├── security.py          # Security utilities
│   ├── config_parser.py     # Nebula config parser
│   ├── cert_manager.py      # Certificate manager
│   └── nebula_manager.py    # Process manager
├── static/
│   └── index.html           # API landing page
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── .env                     # Environment variables (create from .env.example)
```

## 🚀 Quick Start

### 1. Create All Files

Save each code section from the artifacts above into the correct file path shown in the comments.

### 2. Create Environment File

Create `backend/.env`:

```bash
DATABASE_URL=postgresql://nebula:nebula@localhost:5432/nebula_gui
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 4. Create Database

```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE USER nebula WITH PASSWORD 'nebula';
CREATE DATABASE nebula_gui OWNER nebula;
GRANT ALL PRIVILEGES ON DATABASE nebula_gui TO nebula;
\q
```

### 5. Install Nebula Binaries

```bash
cd /tmp
wget https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-linux-amd64.tar.gz
tar -xzf nebula-linux-amd64.tar.gz
sudo mv nebula /usr/local/bin/
sudo mv nebula-cert /usr/local/bin/
sudo chmod +x /usr/local/bin/nebula /usr/local/bin/nebula-cert
```

### 6. Setup Python Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. Create Necessary Directories

```bash
sudo mkdir -p /etc/nebula /tmp/nebula-certs
sudo chmod 755 /etc/nebula /tmp/nebula-certs
```

### 8. Run the Application

```bash
source venv/bin/activate
uvicorn api.main:app --reload
```

The API will be available at: http://localhost:8000

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Certificates
- `POST /api/certificates/ca` - Create CA certificate
- `POST /api/certificates/sign?ca_id={id}` - Sign certificate
- `GET /api/certificates/` - List all certificates
- `GET /api/certificates/{id}` - Get certificate
- `GET /api/certificates/{id}/download` - Download certificate
- `DELETE /api/certificates/{id}` - Revoke certificate
- `GET /api/certificates/ca/list` - List CA certificates

### Configurations
- `POST /api/configs/` - Create configuration
- `GET /api/configs/` - List configurations
- `GET /api/configs/{id}` - Get configuration
- `PUT /api/configs/{id}` - Update configuration
- `DELETE /api/configs/{id}` - Delete configuration
- `POST /api/configs/{id}/activate` - Activate configuration
- `POST /api/configs/validate` - Validate configuration

### Process Management
- `POST /api/process/start` - Start Nebula process
- `POST /api/process/stop/{name}` - Stop process
- `POST /api/process/restart/{name}` - Restart process
- `GET /api/process/status/{name}` - Get process status
- `GET /api/process/status` - Get all process statuses
- `POST /api/process/stop-all` - Stop all processes
- `GET /api/process/logs/{name}` - Get process logs

### Monitoring
- `GET /api/monitoring/system` - System statistics
- `GET /api/monitoring/network` - Network statistics
- `GET /api/monitoring/health` - Health check

### Audit Logs
- `POST /api/audit/` - Create audit log
- `GET /api/audit/` - List audit logs
- `GET /api/audit/{id}` - Get audit log
- `GET /api/audit/user/{id}` - Get user audit logs

### User Management
- `GET /api/users/` - List users (admin)
- `GET /api/users/{id}` - Get user (admin)
- `PUT /api/users/{id}` - Update user (admin)
- `DELETE /api/users/{id}` - Delete user (admin)
- `POST /api/users/{id}/password` - Update password

## 🔐 Default Credentials

- **Username:** admin
- **Password:** Admin123!

**⚠️ CHANGE THESE IMMEDIATELY IN PRODUCTION!**

## 🧪 Testing the API

### Using curl

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!"
```

**Get Current User:**
```bash
TOKEN="your-token-here"
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "Admin123!"}
)
token = response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(response.json())
```

## 🐳 Docker Deployment

### Build and Run

```bash
cd backend
docker build -t nebula-gui-backend .
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://nebula:nebula@host.docker.internal:5432/nebula_gui" \
  -e SECRET_KEY="your-secret-key" \
  --name nebula-gui-backend \
  nebula-gui-backend
```

### Using Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: nebula
      POSTGRES_PASSWORD: nebula
      POSTGRES_DB: nebula_gui
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://nebula:nebula@postgres:5432/nebula_gui
      SECRET_KEY: change-this-secret-key
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - nebula_configs:/etc/nebula
      - nebula_certs:/tmp/nebula-certs
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun

volumes:
  postgres_data:
  nebula_configs:
  nebula_certs:
```

Run:
```bash
docker-compose up -d
```

## 🔧 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
psql -U nebula -d nebula_gui
```

### Nebula Binary Not Found

```bash
# Check if installed
which nebula
which nebula-cert

# Install manually if needed
cd /tmp
wget https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-linux-amd64.tar.gz
tar -xzf nebula-linux-amd64.tar.gz
sudo mv nebula nebula-cert /usr/local/bin/
```

### Permission Denied Errors

```bash
# Fix directory permissions
sudo mkdir -p /etc/nebula /tmp/nebula-certs
sudo chmod 755 /etc/nebula /tmp/nebula-certs
sudo chown $USER:$USER /etc/nebula /tmp/nebula-certs
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Monitoring

### Check System Status

```bash
curl http://localhost:8000/api/monitoring/health
```

### View Logs

```bash
# If running directly
tail -f /var/log/nebula-gui.log

# If running with uvicorn
# Logs will be in the terminal
```

## 🔄 Updating

```bash
cd backend
source venv/bin/activate
git pull  # or update files manually
pip install -r requirements.txt --upgrade
uvicorn api.main:app --reload
```

## 📚 Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Nebula Documentation:** https://nebula.defined.net/docs/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/

## 🆘 Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure PostgreSQL and Nebula binaries are accessible
4. Check file permissions on `/etc/nebula` and `/tmp/nebula-certs`
5. Verify the DATABASE_URL in `.env` is correct

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created with correct credentials
- [ ] Nebula binaries installed (`nebula` and `nebula-cert`)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt
- [ ] Directories created: `/etc/nebula` and `/tmp/nebula-certs`
- [ ] `.env` file created with correct values
- [ ] API starts without errors
- [ ] Can access http://localhost:8000
- [ ] Can login with default credentials
- [ ] Swagger docs accessible at http://localhost:8000/docs

## 🎉 Success!

If all checks pass, your Nebula GUI backend is ready to use!

Access the API documentation at: http://localhost:8000/docs
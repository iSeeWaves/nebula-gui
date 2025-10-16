#!/bin/bash

# Nebula GUI Security Setup Script
# This script sets up all security features

set -e

echo "🔒 Nebula GUI Security Setup"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Please run this script from the backend directory${NC}"
    exit 1
fi

# Step 1: Generate secure keys
echo -e "${YELLOW}Step 1: Generating secure keys...${NC}"

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo -e "${GREEN}✓ Keys generated${NC}"

# Step 2: Create .env file
echo -e "${YELLOW}Step 2: Creating .env file...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file already exists. Creating .env.new instead${NC}"
    ENV_FILE=".env.new"
else
    ENV_FILE=".env"
fi

cat > "$ENV_FILE" << EOF
# Security Settings
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Database
DATABASE_URL=sqlite:///./nebula_gui.db

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Environment
ENVIRONMENT=development

# Session Settings
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Certificate Storage
ENCRYPT_PRIVATE_KEYS=true
EOF

echo -e "${GREEN}✓ Environment file created: $ENV_FILE${NC}"

# Step 3: Install dependencies
echo -e "${YELLOW}Step 3: Installing security dependencies...${NC}"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install -q python-dotenv cryptography pycryptodome secure slowapi zxcvbn

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 4: Create security directories
echo -e "${YELLOW}Step 4: Creating secure directories...${NC}"

mkdir -p certs
mkdir -p logs
chmod 700 certs
chmod 700 logs

echo -e "${GREEN}✓ Directories created with secure permissions${NC}"

# Step 5: Create .gitignore if not exists
echo -e "${YELLOW}Step 5: Updating .gitignore...${NC}"

if [ ! -f "../.gitignore" ]; then
    cat > ../.gitignore << 'EOF'
# Environment
.env
.env.*
!.env.example

# Database
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
*.egg-info/

# Certificates and Keys
certs/
*.key
*.crt
*.pem

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}✓ .gitignore created${NC}"
else
    echo -e "${YELLOW}ℹ .gitignore already exists${NC}"
fi

# Step 6: Create example .env file for GitHub
echo -e "${YELLOW}Step 6: Creating .env.example...${NC}"

cat > ".env.example" << 'EOF'
# Security Settings
SECRET_KEY=change-this-to-a-secure-secret-key
ALGORITHM=HS256
ENCRYPTION_KEY=change-this-to-a-secure-encryption-key

# Database
DATABASE_URL=sqlite:///./nebula_gui.db

# JWT Settings (7 days in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Environment
ENVIRONMENT=development

# Session Settings
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Certificate Storage
ENCRYPT_PRIVATE_KEYS=true
EOF

echo -e "${GREEN}✓ .env.example created${NC}"

# Step 7: Set file permissions
echo -e "${YELLOW}Step 7: Setting secure file permissions...${NC}"

chmod 600 "$ENV_FILE"
chmod 644 ".env.example"

if [ -f "nebula_gui.db" ]; then
    chmod 600 nebula_gui.db
fi

echo -e "${GREEN}✓ File permissions set${NC}"

# Summary
echo ""
echo -e "${GREEN}=============================="
echo "✅ Security Setup Complete!"
echo "==============================${NC}"
echo ""
echo "📋 Summary:"
echo "  - SECRET_KEY: Generated and stored in $ENV_FILE"
echo "  - ENCRYPTION_KEY: Generated and stored in $ENV_FILE"
echo "  - Secure directories created: certs/, logs/"
echo "  - .gitignore updated"
echo "  - File permissions set"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo "  1. Never commit $ENV_FILE to Git!"
echo "  2. Change default admin password immediately!"
echo "  3. Keep your SECRET_KEY and ENCRYPTION_KEY secure"
echo "  4. For production, set ENVIRONMENT=production in $ENV_FILE"
echo "  5. Consider using HTTPS in production"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Review and adjust settings in $ENV_FILE"
echo "  2. Install updated requirements: pip install -r requirements.txt"
echo "  3. Start the server: uvicorn api.main:app --reload"
echo "  4. Change admin password from the profile page"
echo ""
echo -e "${YELLOW}Your keys (KEEP THESE SECURE):${NC}"
echo "SECRET_KEY=$SECRET_KEY"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo ""

# Nebula VPN Management GUI

A modern web-based management interface for Nebula VPN with role-based access control, audit logging, and comprehensive certificate management.

## Features

### 🔐 Authentication & Security
- JWT-based authentication
- Role-Based Access Control (RBAC)
  - Admin: Full access
  - User: Manage own resources
  - Viewer: Read-only access
- Password strength validation
- Session management

### 📜 Certificate Management
- Create Certificate Authority (CA)
- Sign host certificates
- Revoke certificates
- Download certificates and keys
- View certificate details and expiration

### ⚙️ Configuration Management
- Create and manage Nebula configurations
- YAML editor with validation
- Activate/deactivate configurations
- Download configuration files

### 👥 User Management (Admin Only)
- Create and manage users
- Assign roles and permissions
- Activate/deactivate accounts
- View user statistics

### 📊 Monitoring
- Real-time system metrics (CPU, Memory, Disk)
- Network statistics
- Custom refresh intervals

### 📋 Audit Logging
- Track all user actions
- Filter by action, resource, status
- View login history
- Admin activity monitoring

## Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT tokens with OAuth2
- **Security:** Bcrypt password hashing, RBAC
- **Certificate Management:** Nebula-cert CLI integration

### Frontend
- **Framework:** React 18 with Vite
- **Routing:** React Router v6
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State Management:** React Context API

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- nebula-cert binary

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Default Credentials

- **Username:** `admin`
- **Password:** `Admin123!`

⚠️ **Change the default password immediately after first login!**

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
nebula-gui/
├── backend/
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── requirements.txt  # Python dependencies
│   └── nebula_gui.db    # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── context/     # Context providers
│   │   └── services/    # API services
│   ├── package.json     # Node dependencies
│   └── vite.config.js   # Vite configuration
└── README.md
```

## Security Notes

- All passwords are hashed using bcrypt
- JWT tokens expire after 7 days
- Admin endpoints are protected by RBAC
- Audit logging tracks all sensitive operations
- Certificate private keys are stored securely

## Contributing

This is a private repository. If you have access and want to contribute:

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

Private/Proprietary - All rights reserved

## Author

Your Name - Final Year Project 2024/2025

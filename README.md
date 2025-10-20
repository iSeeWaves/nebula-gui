# 🚀 Nebula GUI

<div align="center">

![Nebula GUI](https://img.shields.io/badge/Nebula-GUI-blue?style=for-the-badge&logo=nebula)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-Proprietary-orange?style=for-the-badge)

**Enterprise VPN Management Made Simple**

A modern, intuitive web interface for managing [Nebula VPN](https://github.com/slackhq/nebula) mesh networks.

**Developed by [iSeeWaves (Private) Limited](https://github.com/iSeeWaves)**

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 🔐 **Certificate Management**
- ✅ Create Certificate Authorities with one click
- ✅ Sign host certificates instantly
- ✅ Automatic IP address assignment
- ✅ Certificate lifecycle tracking
- ✅ Bulk certificate operations

### 🚀 **One-Click Client Setup** (NEW!)
- ✅ Generate pre-configured client packages
- ✅ QR code provisioning for mobile devices
- ✅ Complete installation scripts included
- ✅ Zero manual configuration required
- ✅ Support for Linux, macOS, Windows, iOS, Android

### 👥 **User Management**
- ✅ Role-based access control (Admin/User)
- ✅ Multi-user support
- ✅ Activity tracking
- ✅ Profile management

### 📊 **Monitoring & Analytics**
- ✅ Real-time system metrics
- ✅ Network statistics
- ✅ Certificate expiration alerts
- ✅ Process management

### 🔒 **Enterprise Security**
- ✅ JWT authentication
- ✅ Encrypted private keys (AES-256)
- ✅ Comprehensive audit logging
- ✅ Rate limiting & DDoS protection
- ✅ Security headers (HSTS, CSP, etc.)
- ✅ Session management
- ✅ Account lockout after failed attempts

### 🎨 **Modern UI/UX**
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode ready
- ✅ Intuitive navigation
- ✅ Real-time updates

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Nebula binaries ([Download](https://github.com/slackhq/nebula/releases))

### Installation
```bash
# Clone the repository
git clone https://github.com/iSeeWaves/nebula-gui.git
cd nebula-gui

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate security keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" > .env
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env

# Start backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

### First Login

- URL: `http://localhost:5173`
- Username: `admin`
- Password: `Admin123!`

⚠️ **Change the default password immediately!**

---

## 📖 Documentation

### User Guide

1. **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
2. **[User Manual](docs/USER_GUIDE.md)** - How to use Nebula GUI
3. **[API Documentation](docs/API.md)** - REST API reference
4. **[Configuration](docs/CONFIGURATION.md)** - Advanced configuration options

### For Developers

1. **[Development Setup](docs/DEVELOPMENT.md)** - Setting up dev environment
2. **[Architecture](docs/ARCHITECTURE.md)** - System design and components
3. **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
4. **[API Integration](docs/API_INTEGRATION.md)** - Integrate with other systems

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)               │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │Dashboard │  Certs   │  Setup   │ Monitor  │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
                       │ HTTP/REST
┌─────────────────────────────────────────────────┐
│              Backend (FastAPI)                  │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │   Auth   │   API    │ Business │  Queue   │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│            Core Services                        │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ Nebula   │  Crypto  │   DB     │  Logger  │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
```

### Tech Stack

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

**Backend:**
- FastAPI
- SQLAlchemy
- Pydantic
- Python-Jose (JWT)
- Cryptography

**Database:**
- SQLite (default)
- PostgreSQL (production ready)

---

## 🚀 Deployment

### Docker Deployment
```bash
# Using Docker Compose
docker-compose up -d
```

### Manual Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production deployment guide.

### Cloud Deployment

- [DigitalOcean Guide](docs/deploy/DIGITALOCEAN.md)
- [AWS Guide](docs/deploy/AWS.md)
- [Google Cloud Guide](docs/deploy/GCP.md)

---

## 🔒 Security

Nebula GUI takes security seriously:

- 🔐 **Encrypted Storage**: Private keys encrypted at rest (AES-256 Fernet)
- 🛡️ **Authentication**: JWT with configurable expiration
- 📋 **Audit Logging**: Complete audit trail of all actions
- 🚫 **Rate Limiting**: Protection against brute force and DDoS
- 🔒 **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- 🔑 **RBAC**: Role-based access control
- 🚪 **Session Management**: Secure session handling with lockout

**Security Best Practices:**
1. Change default admin password immediately
2. Use strong passwords (8+ chars, mixed case, numbers, special chars)
3. Enable 2FA (coming soon)
4. Keep software updated
5. Use HTTPS in production
6. Regular security audits

**Reporting Security Issues:**  
Please report security vulnerabilities to: iseewaves.pk@gmail.com

---

## 🤝 Contributing

We love contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write tests for new features
- Update documentation
- Keep commits atomic and meaningful

---

## 🗺️ Roadmap

### Version 1.1 (Q1 2026)
- [ ] Desktop system tray applications (Windows, macOS, Linux)
- [ ] Two-factor authentication (2FA)
- [ ] Certificate auto-renewal
- [ ] Bulk operations

### Version 1.2 (Q2 2026)
- [ ] Mobile apps (native iOS/Android)
- [ ] Smart split tunneling
- [ ] Network templates
- [ ] Advanced firewall rules

### Version 2.0 (Q3 2026)
- [ ] Multi-tenancy support
- [ ] LDAP/Active Directory integration
- [ ] Advanced analytics & reporting
- [ ] API v2 with webhooks

See [ROADMAP.md](docs/ROADMAP.md) for detailed plans.

---

## 📊 Comparison

| Feature | Nebula GUI | Tailscale | ZeroTier | WireGuard UI |
|---------|-----------|-----------|----------|--------------|
| **Self-Hosted** | ✅ | ❌ | ❌ | ✅ |
| **One-Click Setup** | ✅ | ✅ | ⚠️ | ❌ |
| **Web Interface** | ✅ | ✅ | ✅ | ✅ |
| **Mobile Apps** | ✅ | ✅ | ✅ | ⚠️ |
| **Audit Logging** | ✅ | ✅ | ⚠️ | ❌ |
| **Multi-User** | ✅ | ✅ | ✅ | ⚠️ |
| **RBAC** | ✅ | ✅ | ⚠️ | ❌ |
| **Open Source** | ✅ | ❌ | ❌ | ✅ |
| **Price (10 devices)** | **Free** | $60/mo | $29/mo | Free |

---

## 📄 License

**Proprietary License**

Copyright © 2025 **iSeeWaves (Private) Limited**. All rights reserved.

This software and associated documentation files (the "Software") are the proprietary property of iSeeWaves (Private) Limited.

### Terms of Use

**PERMISSION IS GRANTED** to any person obtaining a copy of this Software to:
- ✅ Use the Software for personal, educational, or commercial purposes
- ✅ Copy and distribute the Software in its original form
- ✅ Modify the Software for personal or internal business use

**RESTRICTIONS:**
- ❌ The Software may NOT be sold, sublicensed, or redistributed for profit without explicit written permission from iSeeWaves (Private) Limited
- ❌ Modified versions of the Software may NOT be distributed publicly without proper attribution and acknowledgment of iSeeWaves (Private) Limited as the original author
- ❌ The Software's name, logo, and branding may NOT be used to endorse or promote derivative products without written permission

### Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL iSeeWaves (Private) Limited BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Attribution

All copies or substantial portions of the Software must retain the following copyright notice:
```
Copyright © 2025 iSeeWaves (Private) Limited
https://github.com/iSeeWaves
```

### Contact

For licensing inquiries, commercial use, or permissions:
- **Email**: iseewaves.pk@gmail.com
- **Website**: linkedin.com/company/iseewaves
- **GitHub**: https://github.com/iSeeWaves

---

## 🙏 Acknowledgments

- [Nebula](https://github.com/slackhq/nebula) - The amazing overlay network project by Slack
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [React](https://react.dev/) - UI library
- Developer: [Raja Abdullah Nasir](https://github.com/rajaabdullahnasir)
- All our [contributors](https://github.com/iSeeWaves/nebula-gui/graphs/contributors)

---

## 👨‍💻 Development Team

**Company:** [iSeeWaves (Private) Limited](https://github.com/iSeeWaves)

**Lead Developer:** [Raja Abdullah Nasir](https://github.com/rajaabdullahnasir)

---

## 💬 Community

- **Website**: [iseewaves.com](https://www.linkedin.com/company/iseewaves)
- **GitHub**: [github.com/iSeeWaves](https://github.com/iSeeWaves)
- **Email**: iseewaves.pk@gmail.com
- **Issues**: [Report Issues](https://github.com/iSeeWaves/nebula-gui/issues)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=iSeeWaves/nebula-gui&type=Date)](https://star-history.com/#iSeeWaves/nebula-gui&Date)


---

<div align="center">

**Developed with ❤️ by iSeeWaves (Private) Limited**

**Lead Developer:** [Raja Abdullah Nasir](https://github.com/rajaabdullahnasir)

[Company Profile](https://github.com/iSeeWaves) • [Documentation](https://docs.iseewaves.com) • [Support](mailto:support@iseewaves.com)

---

© 2025 iSeeWaves (Private) Limited. All rights reserved.

</div>
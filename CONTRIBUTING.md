# Contributing to Nebula GUI

First off, thank you for considering contributing to Nebula GUI! 🎉

**Developed by [iSeeWaves (Private) Limited](https://github.com/iSeeWaves)**

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. We are committed to providing a welcoming and inspiring community for all.

### Our Standards

- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When reporting bugs, include:**
- Use GitHub Issues with `bug` label
- Clear and descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Screenshots/recordings if applicable
- Environment details:
  - OS and version
  - Python version
  - Node.js version
  - Browser (for frontend issues)
  - Nebula version

**Example:**
```
**Bug Description:** Certificate generation fails with AES error

**Steps to Reproduce:**
1. Go to Certificates page
2. Click "Create CA"
3. Fill in all fields
4. Click Submit

**Expected:** CA certificate created successfully
**Actual:** Error: "AES encryption failed"

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11.2
- Backend: v1.0.0
```

### Suggesting Enhancements

We love feature suggestions! 

**When suggesting enhancements:**
- Use GitHub Issues with `enhancement` label
- Provide clear use cases
- Explain why this would be useful to users
- Include mockups or examples if possible
- Consider implementation complexity

### Pull Requests

We actively welcome your pull requests!

**Process:**

1. **Fork the repository**
   ```bash
   git clone https://github.com/iSeeWaves/nebula-gui.git
   cd nebula-gui
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow coding standards (see below)
   - Add comments for complex logic
   - Update documentation if needed

4. **Add tests**
   ```bash
   # Backend tests
   cd backend && pytest tests/test_your_feature.py
   
   # Frontend tests
   cd frontend && npm test
   ```

5. **Run linters**
   ```bash
   # Python
   cd backend
   black .
   flake8 .
   mypy .
   
   # JavaScript
   cd frontend
   npm run lint
   npm run format
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m 'Add amazing feature: brief description'
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Open a Pull Request**
   - Go to the [repository](https://github.com/iSeeWaves/nebula-gui)
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Description of changes
     - Related issue numbers
     - Testing performed
     - Screenshots (for UI changes)

### Development Setup

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- Git

**Backend Setup:**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dev dependencies (pytest, black, etc.)

# Setup environment
cp .env.example .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env

# Run migrations (if applicable)
alembic upgrade head

# Run tests
pytest

# Run with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Format code
npm run format

# Build for production
npm run build
```

### Coding Standards

**Python (Backend):**
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all functions
- Write comprehensive docstrings (Google style)
- Maximum line length: 100 characters
- Use `black` for code formatting
- Use `flake8` for linting
- Use `mypy` for type checking

**Example:**
```python
from typing import Optional

def create_certificate(
    name: str,
    ip_address: str,
    groups: Optional[list[str]] = None
) -> dict:
    """
    Create a new host certificate.
    
    Args:
        name: Certificate common name
        ip_address: IP address to assign
        groups: Optional list of groups
        
    Returns:
        Dictionary containing certificate details
        
    Raises:
        ValueError: If IP address is invalid
    """
    # Implementation
    pass
```

**JavaScript/React (Frontend):**
- Use ESLint + Prettier configuration provided
- Use functional components with hooks
- Prefer `const` over `let`, avoid `var`
- Use meaningful variable names (no single letters except in loops)
- Write JSDoc comments for complex functions
- Use Tailwind CSS utility classes
- Keep components small and focused

**Example:**
```javascript
/**
 * Certificate creation form component
 * @param {Function} onSubmit - Callback when form is submitted
 * @param {boolean} loading - Whether form is in loading state
 */
const CertificateForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    name: '',
    ipAddress: '',
    groups: []
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

### Commit Message Guidelines

Good commit messages help maintain project history.

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add two-factor authentication support

Implement TOTP-based 2FA for user accounts.
Adds QR code generation and verification endpoints.

Closes #123

---

fix(certificates): resolve AES encryption error

Fix key derivation in certificate encryption module.
Previously caused failures with certain key lengths.

Fixes #456

---

docs(readme): update installation instructions

Add Docker setup steps and troubleshooting section
```

**Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line max 72 characters
- Reference issues and PRs in footer
- Explain "why" not just "what" in the body

### Testing

Quality code requires good tests!

**Backend Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success
```

**Frontend Testing:**
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Testing Guidelines:**
- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test edge cases and error conditions
- Use descriptive test names
- Mock external dependencies

### Documentation

Good documentation is crucial!

**When to update docs:**
- Adding new features
- Changing API endpoints
- Modifying configuration options
- Updating dependencies

**What to document:**
- API endpoints and parameters
- Configuration options
- Environment variables
- Complex algorithms or logic
- User-facing features

## Project Structure

```
nebula-gui/
├── backend/
│   ├── api/           # FastAPI application
│   ├── core/          # Core business logic
│   ├── models/        # Database models
│   ├── services/      # Service layer
│   ├── tests/         # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── utils/       # Utility functions
│   ├── public/
│   └── package.json
├── docs/              # Documentation
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Review Process

All submissions require review before merging.

**Review checklist:**
- ✅ Code follows style guidelines
- ✅ Tests are included and passing
- ✅ Documentation is updated
- ✅ Commit messages are clear
- ✅ No merge conflicts
- ✅ PR description is complete

**Review timeline:**
- Initial review: 2-3 business days
- Follow-up reviews: 1-2 business days

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Added to GitHub contributors page

## License

By contributing, you agree that your contributions will be licensed under the project's Proprietary License, with ownership retained by iSeeWaves (Private) Limited.

## Questions or Need Help?

Don't hesitate to reach out!

- **GitHub Issues**: [Create an issue](https://github.com/iSeeWaves/nebula-gui/issues)
- **GitHub Discussions**: [Join discussion](https://github.com/iSeeWaves/nebula-gui/discussions)
- **Email**: dev@iseewaves.com
- **Company**: [iSeeWaves (Private) Limited](https://github.com/iSeeWaves)

## Additional Resources

- [README.md](README.md) - Project overview
- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)

---

Thank you for contributing to Nebula GUI! 🙏

**© 2025 iSeeWaves (Private) Limited. All rights reserved.**

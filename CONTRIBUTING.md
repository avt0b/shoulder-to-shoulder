# Contributing to Shoulder-to-Shoulder

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## 📖 Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code.

- Be respectful and inclusive
- Welcome newcomers and help them get oriented
- Focus on what is best for the community
- Report unacceptable behavior to project maintainers

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork Graf140/shoulder-to-shoulder
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/shoulder-to-shoulder.git
   cd shoulder-to-shoulder
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Graf140/shoulder-to-shoulder.git
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature develop
   ```

## 🔧 Development Setup

See [.github/DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

Quick start:
```bash
# Copy environment variables
cp .env.example .env

# Start services with Docker Compose
docker-compose up -d

# Install dependencies (if developing locally)
pip install -e .

# Run tests
pytest backend/ -v
npm run test
```

## ✏️ Making Changes

### Commit Messages

Follow Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Dependency, build, CI changes

**Examples:**
```
feat(user_service): add profile endpoint

fix(notification_service): handle null values in scheduler

docs: update API documentation

chore(deps): update Python dependencies
```

### Branch Naming

```
feature/description           # New features
fix/description              # Bug fixes
docs/description             # Documentation
refactor/description         # Refactoring
chore/description            # Maintenance
```

## 📤 Submitting Changes

### Before Creating a PR

- [ ] Code compiles without errors
- [ ] All tests pass locally
- [ ] No sensitive data in commits
- [ ] Code follows project standards
- [ ] Commit messages are descriptive

### Creating a Pull Request

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Push your changes**
   ```bash
   git push origin your-branch-name
   ```

3. **Create PR on GitHub**
   - Use the PR template
   - Fill all required sections
   - Link related issues
   - Request reviewers

### PR Requirements

- ✅ All CI checks pass
- ✅ At least one approval
- ✅ No conflicts with base branch
- ✅ Updated tests
- ✅ Updated documentation

## 💻 Coding Standards

### Python

Follow **PEP 8** and **PEP 257**:

```python
"""Module docstring."""

from typing import Optional

def function_name(param: str) -> Optional[str]:
    """Add docstring describing function.

    Args:
        param: Parameter description

    Returns:
        Return value description
    """
    pass


class ClassName:
    """Class docstring."""

    def __init__(self):
        """Initialize the class."""
        pass

    def method(self) -> None:
        """Method description."""
        pass
```

**Linting:**
```bash
ruff check backend/
black backend/
pyright backend/
```

### Frontend

Follow **ESLint** and **Prettier** rules:

```typescript
// Use TypeScript
interface User {
  id: number;
  name: string;
}

// Add JSDoc comments
/**
 * Fetch user by ID
 * @param id - User ID
 * @returns Promise<User>
 */
async function getUser(id: number): Promise<User> {
  return fetch(`/api/users/${id}`).then(r => r.json());
}
```

**Linting:**
```bash
npm run lint
npm run format
```

### Docker

- Use slim images
- Minimize layers
- Cache dependencies
- Follow best practices

### Docs

- Use Markdown formatting
- Add code examples
- Include links
- Keep up to date

## 🧪 Testing

### Python Tests

```bash
# All tests
pytest backend/ -v

# Specific service
pytest backend/user_service/tests -v

# With coverage
pytest backend/ --cov=backend/ --cov-report=html

# Specific test
pytest backend/user_service/tests/test_auth.py::test_login -v
```

### Frontend Tests

```bash
cd frontend/authorization

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

### Test Requirements

- Minimum **80% code coverage**
- Tests must pass locally
- No flaky tests
- Descriptive test names
- Test edge cases

## 🔄 Pull Request Process

1. **Fork and branch**
   ```
   your-fork/feature-branch
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update docs

3. **Test locally**
   ```bash
   pytest backend/ -v
   npm run test
   ```

4. **Push and create PR**
   - Reference issues (#123)
   - Fill PR template
   - Request review

5. **Address feedback**
   - Make changes
   - Push updates
   - GitHub will auto-update PR

6. **Merge**
   - Maintainer merges PR
   - Branch auto-deletes

## 📚 Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## ❓ Questions?

- Check [Discussions](https://github.com/Graf140/shoulder-to-shoulder/discussions)
- Open an [Issue](https://github.com/Graf140/shoulder-to-shoulder/issues)
- Check existing documentation

---

**Thank you for contributing! 🎉**

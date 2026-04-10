# GitHub Configuration

This directory contains all GitHub-related configuration and documentation for the Shoulder-to-Shoulder project.

## 📁 Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflows
│   ├── ci.yml             # Code quality and testing
│   ├── build.yml          # Docker image building
│   ├── deploy.yml         # Production deployment
│   └── dependencies.yml   # Dependency management
├── ISSUE_TEMPLATE/        # Issue templates
│   ├── bug_report.md
│   ├── feature_request.md
│   ├── task.md
│   ├── documentation.md
│   └── config.yml
├── WORKFLOWS.md           # Workflows documentation
├── DEVELOPMENT.md         # Development guide
└── README.md              # This file
```

## 🔄 Workflows

### Available Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | Push, PR | Code quality, tests, linting |
| **Build** | Push (main/develop) | Build Docker images |
| **Deploy** | Tag v*, manual | Production deployment |
| **Dependencies** | Schedule (weekly) | Dependency updates & vulnerability scan |

**📖 Read:** [WORKFLOWS.md](WORKFLOWS.md) for detailed information

## 📝 Issue Templates

- **Bug Report**: Report bugs and issues
- **Feature Request**: Suggest new features
- **Task**: General tasks and chores
- **Documentation**: Documentation improvements

## 🚀 Development

**📖 Read:** [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Local setup
- Development workflow
- Testing procedures
- Git commands
- CI/CD troubleshooting

## 🤝 Contributing

**📖 Read:** [../CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code of conduct
- Commit message format
- PR process
- Coding standards
- Testing requirements

## 🔐 Secrets Configuration

Required GitHub Secrets (Settings → Secrets and variables):

```
SLACK_WEBHOOK_URL       # For Slack notifications
PROD_DATABASE_URL       # Production database
DOCKER_USERNAME         # Docker Hub (optional)
DOCKER_PASSWORD         # Docker Hub (optional)
```

## 📊 Branch Protection

Recommended branch protection rules:

**main:**
- ✅ Require pull request reviews (1)
- ✅ Require status checks (CI must pass)
- ✅ Require branches up to date
- ✅ Include administrators

**develop:**
- ✅ Require pull request reviews (1)
- ✅ Require status checks
- ✅ Allow auto-merge

## 🎯 Standard Labels

Recommended GitHub labels:

| Label | Color | Purpose |
|-------|-------|---------|
| `bug` | Red | Bug reports |
| `enhancement` | Green | Feature requests |
| `documentation` | Blue | Documentation |
| `security` | Orange | Security issues |
| `dependencies` | Purple | Dependency updates |
| `task` | Yellow | General tasks |
| `help wanted` | Gray | Looking for help |
| `good first issue` | Light green | Good for newcomers |
| `wontfix` | Gray | Won't be fixed |

## 📞 Quick Links

- [Actions Tab](https://github.com/Graf140/shoulder-to-shoulder/actions)
- [Pull Requests](https://github.com/Graf140/shoulder-to-shoulder/pulls)
- [Issues](https://github.com/Graf140/shoulder-to-shoulder/issues)
- [Discussions](https://github.com/Graf140/shoulder-to-shoulder/discussions)
- [Projects](https://github.com/Graf140/shoulder-to-shoulder/projects)

## 🔗 Related Files

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [README.md](../README.md) - Project overview
- [.gitignore](../.gitignore) - Git ignore rules
- [pyproject.toml](../pyproject.toml) - Python config
- [docker-compose.yml](../docker-compose.yml) - Docker setup

---

**Last updated:** 2024-04-09

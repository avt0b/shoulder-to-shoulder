# GitHub Actions Workflows

Этот документ описывает все GitHub Actions workflows, используемые в проекте Shoulder-to-Shoulder.

## 📋 Обзор Workflows

### 1. **CI - Code Quality & Tests** (`ci.yml`)

Запускается на push и pull requests в ветки: `main`, `develop`, `notifications`

**Задачи:**
- ✅ Python линтинг (Ruff, Black)
- ✅ Type checking (Pyright)
- ✅ Unit тесты с coverage
- ✅ Frontend линтинг (ESLint, Type check)
- ✅ Security сканирование (Trivy)

**Services:**
- PostgreSQL 16
- Redis 7
- NATS 2

**Trigger:**
```yaml
- Push в main, develop, notifications
- Pull requests
- Изменения в backend/, frontend/, workflows
```

---

### 2. **Build & Push Docker Images** (`build.yml`)

Собирает и публикует Docker образы в GitHub Container Registry (GHCR)

**Образы:**
- `shoulder-to-shoulder-user_service`
- `shoulder-to-shoulder-notification_service`
- `shoulder-to-shoulder-event_service`
- `shoulder-to-shoulder-admin_service`
- `shoulder-to-shoulder-frontend`

**Tags:**
- `develop` (по ветке)
- `main` (по ветке)
- `sha-<commit>` (по коммиту)
- `latest` (только для main)
- `v*` (по git tag)

**Trigger:**
```yaml
- Push в main или develop
- Workflow dispatch (ручной запуск)
```

---

### 3. **Deploy to Production** (`deploy.yml`)

Развертывание приложения в staging и production окружения

**Окружения:**
- **Staging**: Развертывание при push в develop
- **Production**: Развертывание при push тага v*

**Задачи:**
- ✅ Развертывание контейнеров
- ✅ Smoke тесты
- ✅ Integration тесты
- ✅ Database миграции
- ✅ Создание Release Notes
- ✅ Rollback при ошибке
- ✅ Slack уведомления

**Trigger:**
```yaml
- Push тага v* (production)
- Push в develop (staging)
- Manual dispatch
```

---

### 4. **Dependency Check & Updates** (`dependencies.yml`)

Проверка уязвимостей в зависимостях и создание PR для обновлений

**Задачи:**
- ✅ Safety check (Python)
- ✅ pip-audit (Python)
- ✅ npm audit (Frontend)
- ✅ Автоматическое обновление зависимостей
- ✅ Создание GitHub Issues для уязвимостей
- ✅ Создание PR с обновлениями

**Schedule:**
```yaml
# Каждый понедельник в 9 AM UTC
0 9 * * 1
```

**Trigger:**
```yaml
- Schedule (по расписанию)
- Manual dispatch
```

---

## 🚀 Как использовать

### Ручной запуск workflow

```bash
# GitHub CLI
gh workflow run ci.yml
gh workflow run build.yml
gh workflow run deploy.yml

# Через веб-интерфейс
GitHub → Actions → Выбрать workflow → Run workflow
```

### Просмотр логов

```bash
# GitHub CLI
gh run list
gh run view <run_id> --log

# Веб-интерфейс
GitHub → Actions → Workflow → Click run
```

---

## 🔐 Требуемые Secrets

Установите в GitHub Settings → Secrets and variables → Actions:

```yaml
# Docker Registry (необязательно, если используется ghcr.io с GITHUB_TOKEN)
DOCKER_USERNAME: <username>
DOCKER_PASSWORD: <token>

# Slack уведомления
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/...

# Production окружение
PROD_DATABASE_URL: postgresql://...
PROD_API_KEY: ...
```

---

## 📊 CI/CD Flow

```
┌─────────────────────┐
│   Git Push/PR       │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  CI Pipeline │
    │  (Tests)     │
    └──────┬───────┘
           │
      ┌────┴────┐
      │          │
    ✅ OK     ❌ FAIL
      │          │
      ▼          ▼
   Build    Comment PR
   Images   with errors
      │
      ▼
┌─────────────┐
│ GHCR Push   │
└──────┬──────┘
       │
       ▼
  ┌─────────┐
  │ Tag v*? │
  └────┬────┘
       │
   ✅ YES (Release)
       │
       ▼
  ┌───────────┐
  │ Deploy    │
  │ Production│
  └───────────┘
```

---

## 📝 Branch Strategy

```
main (production)
  ↑
  │ merge + tag v*
  │
develop (staging)
  ↑
  │ merge PR
  │
feature/* (CI tests only)
  ↑
  │ PR to develop
  │
notifications (special branch for notification_service)
  ↑
  │ merge to develop
```

---

## ✅ Best Practices

### 1. **Commit Messages**
```
feat: add new feature
fix: fix bug
docs: update docs
chore: update dependencies
ci: update workflows
```

### 2. **PR Checklist**
- ✅ Tests pass locally
- ✅ No linting errors
- ✅ Code reviewed
- ✅ Documentation updated

### 3. **Tagging для Release**
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 🐛 Troubleshooting

### Build fails with "Connection refused"
```
Решение: Проверить интернет и доступ к Docker Hub
```

### Tests timeout
```
Решение: Увеличить timeout в workflow или оптимизировать тесты
```

### Deployment fails
```
Решение: Проверить secrets, доступ к серверу, логи
```

### GHCR push fails
```
Решение: Проверить GITHUB_TOKEN permissions
Settings → Actions → General → Workflow permissions → Read and write
```

---

## 📚 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Login Action](https://github.com/docker/login-action)
- [Create Pull Request Action](https://github.com/peter-evans/create-pull-request)
- [Slack GitHub Action](https://github.com/slackapi/slack-github-action)

---

## 📞 Questions?

Для вопросов или предложений по workflows создайте Issue с меткой `ci`.

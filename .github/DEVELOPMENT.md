# Development Workflow Guide

## Локальная разработка

### 1. Setup окружения

```bash
# Клонируем репо
git clone https://github.com/Graf140/shoulder-to-shoulder.git
cd shoulder-to-shoulder

# Создаем .env файл
cp .env.example .env

# Запускаем проект
docker-compose up -d

# Проверяем статус
docker-compose ps
```

### 2. Ветвление

```bash
# Создаем feature ветку
git checkout -b feature/your-feature develop

# Или для hotfix
git checkout -b hotfix/your-fix main
```

### 3. Разработка

```bash
# Вносим изменения
# ...

# Коммитим
git add .
git commit -m "feat: your feature description"

# Pushим
git push origin feature/your-feature
```

### 4. Pull Request

1. Откройте PR в GitHub
2. Заполните описание (используйте PR шаблон)
3. Дождитесь CI успеха
4. Запросите review
5. После одобрения - merge

---

## 📦 Release Process

### Версионирование

Используется **Semantic Versioning**: `v{MAJOR}.{MINOR}.{PATCH}`

```
v1.0.0  - Major: breaking changes
v1.1.0  - Minor: new features
v1.0.1  - Patch: bug fixes
```

### Создание Release

```bash
# 1. Обновляем версию (обновите в файлах)
# - pyproject.toml
# - package.json (frontend)
# - CHANGELOG.md

# 2. Коммитим изменения
git add .
git commit -m "chore: bump version to v1.2.0"

# 3. Создаем tag
git tag -a v1.2.0 -m "Release version 1.2.0

Major features:
- Feature 1
- Feature 2

Bug fixes:
- Fix 1
"

# 4. Пушим
git push origin develop
git push origin v1.2.0
```

После push тага:
- ✅ CI тесты запустятся
- ✅ Docker образы соберутся
- ✅ Развертывание в production
- ✅ Release Notes создадутся автоматически

---

## 🔄 Merge Strategy

### main → production
```
main branch:
  - Только stable releases
  - Tagged версии (v*)
  - Автоматический deploy в production
```

### develop → staging
```
develop branch:
  - Рабочая версия на staging
  - PR-based workflow
  - CI тесты обязательны
```

### feature/*
```
feature branches:
  - Создаются из develop
  - CI тесты запускаются
  - PR для merge в develop
```

### notifications (special)
```
notifications branch:
  - Для разработки notification_service
  - Мержится в develop
  - Особый workflow
```

---

## 🧪 Локальное тестирование

### Python тесты

```bash
# Все тесты
pytest backend/ -v

# С coverage
pytest backend/ --cov=backend/ --cov-report=html

# Конкретный модуль
pytest backend/user_service/tests -v

# С параллелизацией
pytest backend/ -n auto
```

### Frontend тесты

```bash
cd frontend/authorization

# Unit тесты
npm run test

# E2E тесты
npm run test:e2e

# Линтинг
npm run lint

# Format check
npm run format:check
```

### Docker Compose тестирование

```bash
# Проверить связность сервисов
docker-compose exec user_service curl http://notification_service:8001/health

# Логи
docker-compose logs -f user_service

# Вход в контейнер
docker-compose exec user_service bash

# Перестарт сервиса
docker-compose restart user_service
```

---

## 📋 Чек-лист перед коммитом

```
Code Quality:
  ☐ Нет синтаксических ошибок
  ☐ Все импорты используются
  ☐ Нет hardcoded значений

Tests:
  ☐ Unit тесты проходят
  ☐ Coverage >= 80%
  ☐ Нет flaky тестов

Documentation:
  ☐ Docstrings добавлены
  ☐ Comments для сложной логики
  ☐ README обновлен (если нужно)

Security:
  ☐ Нет уязвимостей в зависимостях
  ☐ No secrets in code
  ☐ Proper error handling

Performance:
  ☐ N+1 queries отсутствуют
  ☐ No memory leaks
  ☐ DB indexes добавлены
```

---

## 🔧 Команды для разработки

### Docker Compose

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перестроение
docker-compose build --no-cache

# Логи
docker-compose logs -f

# Shell в контейнер
docker-compose exec <service> bash

# Выполнить команду
docker-compose exec <service> python -m pytest

# Удалить volumes
docker-compose down -v
```

### Git

```bash
# Статус
git status

# Diff
git diff
git diff --cached

# История
git log --oneline -10
git log --graph --all

# Отмена
git restore <file>
git reset HEAD <file>
git revert <commit>

# Rebase
git rebase -i develop
git rebase --continue

# Clean up
git branch -d <branch>
git push origin --delete <branch>
```

### Python/Pip

```bash
# Обновить зависимости
uv pip compile pyproject.toml --upgrade

# Установить в editable mode
pip install -e .

# Проверить версии
pip list

# Cleanup
pip cache purge
```

---

## 📊 CI/CD Status

Посмотреть статус всех workflows:

```bash
# GitHub CLI
gh run list --limit 20
gh run view <run_id>

# Or in GitHub UI
GitHub → Actions → Workflows
```

---

## 🚨 Emergency Procedures

### Откат в production

```bash
# 1. Найти коммит для отката
git log --oneline main | head -20

# 2. Откатиться
git revert <commit_hash>

# 3. Push (это создаст новый коммит)
git push origin main

# 4. Workflow запустится автоматически

# ЛИЛ если нужно откатиться к конкретной версии:
git tag -a v1.0.0-rollback -m "Rollback to v1.0.0"
git push origin v1.0.0-rollback
```

### Отключить CI

```
В коммите используйте:
  [skip ci]
  [ci skip]

Пример:
git commit -m "docs: update readme [skip ci]"
```

### Пересоздать workflow

```bash
# GitHub CLI
gh workflow run ci.yml --ref develop --inputs env=staging

# Or в веб-интерфейсе
GitHub → Actions → Workflow → Run workflow
```

---

## 📚 Полезные ссылки

- [Git Book](https://git-scm.com/book)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Pytest Docs](https://docs.pytest.org/)

---

## 💬 Questions or Issues?

1. Проверьте документацию в `.github/WORKFLOWS.md`
2. Создайте Issue в GitHub
3. Спросите в chat

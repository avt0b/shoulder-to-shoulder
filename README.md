# 🤝 Плечом к плечу
> Мобильное приложение для коллективных уличных тренировок с нулевым психологическим барьером

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: MVP](https://img.shields.io/badge/Status-MVP-orange)](README.md)
[![Microservices](https://img.shields.io/badge/Architecture-Microservices-brightgreen)](README.md)

## 🎯 О проекте
«Плечом к плечу» решает не проблему лени, а проблему **страха осуждения и одиночества** при выходе на бесплатные спортплощадки. Приложение позволяет за 2 клика найти компанию для тренировки, получить безопасный маршрут и попасть в среду, где ценят поддержку, а не результат.

📍 **Пилот:** г. Орёл
👥 **ЦА:** 18–35 лет, новички, интроверты, жители спальных районов

---

## 🏗 Микросервисная архитектура

### Сервисы
| Сервис | Порт | Описание |
|:---|:---:|:---|
| **user_service** | 8000 | Управление пользователями, профилями, рейтингами |
| **notification_service** | 8001 | Отправка уведомлений, расписание |
| **event_service** | 8002 | Управление сборами и участниками |
| **admin_service** | 8003 | Административная панель |
| **maps_service** | 8004 | Работа с географическими данными |
| **frontend** | 3000 | Vue.js приложение |

### Инфраструктура
| Компонент | Технология | Порт |
|:---|:---|:---:|
| База данных | PostgreSQL 16 | 5432 |
| Кэш | Redis 7 | 6379 |
| Message Broker | NATS 2 (JetStream) | 4222 |

---

## 🚀 Быстрый старт

### Требования
- **Docker & Docker Compose**: [Установка](https://docs.docker.com/get-docker/)
- **Make** (опционально): Для удобных команд
- **Python 3.12+** (для локальной разработки)

### Запуск всех сервисов

```bash
# Запустить все контейнеры в фоне
make up

# Или без Make
docker-compose up -d
```

Сервисы будут доступны:
- **Swagger UI**: http://localhost:8000/docs (User Service)
- **Frontend**: http://localhost:3000
- **NATS Monitor**: http://localhost:8222

### Разработка с hot-reload

```bash
# Запустить с автоперезагрузкой при изменении кода
make dev

# Или
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Остановка сервисов

```bash
make down
```

---

## 📋 Доступные команды Make

```bash
make help              # Показать все команды
make build             # Собрать образы
make up                # Запустить сервисы (фон)
make down              # Остановить сервисы
make dev               # Разработка с hot-reload
make logs              # Показать логи
make logs-follow       # Следить за логами
make status            # Статус сервисов и health-checks
make restart           # Перезапустить все
make clean             # Удалить контейнеры и volumes
make bash-USER         # Shell в user_service (и другие сервисы)
make migrate-user      # Миграции БД
```

---

## 🏢 Структура проекта

```
shoulder-to-shoulder/
├── backend/
│   ├── user_service/
│   │   ├── app/              # FastAPI приложение
│   │   ├── Dockerfile        # Образ сервиса
│   │   ├── pyproject.toml     # Зависимости
│   │   └── .dockerignore
│   ├── notification_service/  # Уведомления
│   ├── event_service/         # Сборы и события
│   ├── admin_service/         # Админ-панель
│   └── maps_service/          # Геоданные
├── frontend/
│   └── authorization/         # Vue.js интерфейс
├── docker-compose.yml         # Production конфиг
├── docker-compose.dev.yml     # Development перегрузки
├── Makefile                   # Управление сервисами
├── .env.example              # Переменные окружения
└── README.md                 # Этот файл
```

---

## 🔧 Конфигурация

### Переменные окружения

Скопируйте `.env.example` → `.env`:

```bash
cp .env.example .env
```

**Основные переменные:**

```env
# Сервис
ENVIRONMENT=development
SECRET_KEY=your-secret-key-change-in-production

# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/shoulder_to_shoulder_db

# Redis
REDIS_URL=redis://redis:6379/0

# NATS Message Broker
NATS_URL=nats://nats:4222
```

### Для production

Обновите переменные в `.env`:
- `ENVIRONMENT=production`
- `SECRET_KEY=` - сгенерируйте надежный ключ
- `DATABASE_URL=` - используйте управляемую БД
- Используйте HTTPS для всех сервисов

---

## 🗄️ База данных

### Первый запуск

Миграции применяются автоматически при запуске. Для явного запуска:

```bash
make migrate-user
make migrate-event
make migrate-notif
```

### Сброс БД (WARNING: удалит все данные)

```bash
make db-reset
```

### Доступ к PostgreSQL

```bash
make bash-postgres
# Или
docker-compose exec postgres psql -U postgres -d shoulder_to_shoulder_db
```

---

## 📡 NATS Message Broker

### Мониторинг

Откройте: http://localhost:8222

### События в системе

```
workout.completed      → User Service обновляет надёжность
empathy.awarded        → User Service добавляет points эмпатии
notification.created   → Notification Service создал уведомление
notification.sent      → Уведомление отправлено
```

---

## 🧪 Тестирование и линтинг

```bash
# Форматирование кода
make format

# Линтинг
make lint
```

---

## 🐛 Отладка

### Логи конкретного сервиса

```bash
docker-compose logs user_service -f
```

### Вход в shell контейнера

```bash
make bash-USER    # user_service
make bash-EVENT   # event_service
```

### Health checks

```bash
make status
```

---

## 📚 API Documentation

После запуска сервисов:

| Сервис | Swagger |
|:---|:---|
| User Service | http://localhost:8000/docs |
| Notification Service | http://localhost:8001/docs |
| Event Service | http://localhost:8002/docs |
| Admin Service | http://localhost:8003/docs |
| Maps Service | http://localhost:8004/docs |

---

## 🚀 Развёртывание

### Docker Hub / private registry

```bash
# Собрать образы с тегом
docker build -t your-registry/user-service:latest backend/user_service

# Запушить
docker push your-registry/user-service:latest

# В docker-compose использовать
image: your-registry/user-service:latest
```

### Kubernetes (примерная структура)

```bash
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/nats-deployment.yaml
kubectl apply -f k8s/user-service-deployment.yaml
# ...
```

### Yandex Cloud, AWS, или другие

Используйте CI/CD pipeline:
1. GitHub Actions / GitLab CI для сборки образов
2. Push в реестр
3. Обновление в целевом окружении (Helm, docker-compose, Kubernetes)

---

## 📖 Технологический стек

| Слой | Технология |
|:---|:---|
| **API Framework** | FastAPI 0.135+ |
| **ASGI Server** | Uvicorn 0.44+ |
| **ORM** | SQLAlchemy 2.0+ |
| **Database** | PostgreSQL 16 + asyncpg |
| **Cache** | Redis 7 |
| **Message Broker** | NATS 2 JetStream |
| **Auth** | JWT + bcrypt |
| **Validation** | Pydantic 2.12+ |
| **Frontend** | Vue.js 3, Vite |
| **Container** | Docker & Docker Compose |

---

## 🤝 Вклад в проект

1. Создайте ветку: `git checkout -b feature/new-feature`
2. Коммитьте изменения: `git commit -m "Add new feature"`
3. Пушьте в репо: `git push origin feature/new-feature`
4. Откройте Pull Request

---

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 👥 Контакты

📧 **Email**: team@example.com
🔗 **Website**: https://plecho-k-plecho.ru (пример)
💬 **Telegram**: @example_bot (пример)

---

**Last updated**: 2026-04-09
**Maintainer**: DevOps & Backend Team

# 🏛️ Архитектура сервисов

## Микросервисная архитектура

Проект использует микросервисную архитектуру с асинхронной коммуникацией через NATS JetStream.

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (Frontend)                        │
│                      Vue.js @ :3000                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Microservices (FastAPI/Uvicorn)                  │
├──────────────────┬──────────────────┬──────────────┬────────┤
│  User Service    │ Notification Svc │ Event Svc    │ Maps   │
│  :8000           │ :8001            │ :8002        │ :8004  │
└────────┬─────────┴────────┬─────────┴──────┬───────┴───┬────┘
         │                  │                │           │
         │ NATS Events      │                │           │
         │ JetStream        │                │           │
┌────────▼──────────────────▼────────────────▼───────────▼────┐
│                   NATS Message Broker                        │
│                   nats://nats:4222                           │
└────────┬──────────────────┬────────────────┬────────────────┘
         │                  │                │
         │                  │                │
┌────────▼──────┐ ┌─────────▼──────┐ ┌──────▼───────┐
│  PostgreSQL   │ │     Redis      │ │   FastAPI   │
│  Port: 5432   │ │  Port: 6379    │ │   Status    │
└───────────────┘ └────────────────┘ └─────────────┘
```

## Сервисы

### 1. **User Service** (Port: 8000)
**Отвественность:** Управление пользователями, профилями, рейтингами, бейджами

**Endpoints:**
- `GET/POST /api/v1/users` - CRUD пользователей
- `GET /api/v1/users/{id}/profile` - Профиль пользователя
- `GET /api/v1/users/{id}/rating` - Рейтинг (Эмпатия + Надёжность)
- `POST /api/v1/users/{id}/badges` - Выдать бейдж

**NATS Publishers:**
- `user.created` - Новый пользователь
- `user.updated` - Обновление профиля

**NATS Subscribers:**
- `workout.completed` - Обновить надёжность
- `empathy.awarded` - Добавить points эмпатии

**Database:**
- `users` - основные данные
- `user_profiles` - расширенная информация
- `user_ratings` - рейтинги и метрики
- `badges` - бейджи пользователей

---

### 2. **Notification Service** (Port: 8001)
**Ответственность:** Управление уведомлениями, расписание отправок

**Endpoints:**
- `POST /api/v1/notifications/create-notif` - Создать уведомление
- `GET /api/v1/notifications/` - Все уведомления
- `GET /api/v1/notifications/user/{user_id}` - Уведомления юзера
- `POST /api/v1/go-notif` - Callback от шедулера

**Background:**
- Scheduler каждые 10 сек проверяет pending уведомления
- Когда time наступает → отправляет на gateway

**NATS Publishers:**
- `notification.created` - Создано уведомление
- `notification.sent` - Отправлено

**Database:**
- `notifications` - хранилище уведомлений
- `notification_schedule` - расписание

---

### 3. **Event Service** (Port: 8002)
**Ответственность:** Управление сборами (тренировками), участниками, местами

**Endpoints:**
- `GET/POST /api/v1/events` - События
- `POST /api/v1/events/{id}/join` - Присоединиться к сбору
- `POST /api/v1/events/{id}/leave` - Покинуть сбор
- `GET /api/v1/events/{id}/participants` - Участники

**NATS Publishers:**
- `event.created` - Новое событие
- `event.started` - Событие началось
- `event.completed` - Событие завершено

**Database:**
- `events` - события/сборы
- `event_participants` - участники с их статусом

---

### 4. **Admin Service** (Port: 8003)
**Ответственность:** Административная панель, модерация, аналитика

**Endpoints:**
- `GET /api/v1/admin/stats` - Статистика
- `GET /api/v1/admin/reports` - Отчёты
- `POST /api/v1/admin/moderate` - Модерация контента

**Database:**
- Доступ ко всем таблицам для аналитики

---

### 5. **Maps Service** (Port: 8004)
**Ответственность:** Управление местами, освещением, маршрутами

**Endpoints:**
- `GET /api/v1/locations` - Список мест
- `POST /api/v1/locations` - Добавить место
- `GET /api/v1/routes` - Расчёт маршрута

**Database:**
- `locations` - тренировочные площадки
- `location_attributes` - освещение, доступность и т.д.

---

## Асинхронная коммуникация (NATS)

### Основные события

```
workout.completed
├─ [Source] Event Service
├─ [Subscribe] User Service
└─ [Action] Увеличить reliability_score

empathy.awarded
├─ [Source] User Service или Event Service
├─ [Subscribe] User Service (обновить rating)
└─ [Action] Добавить empathy points

notification.created
├─ [Source] Any Service
├─ [Subscribe] Notification Service
└─ [Action] Сохранить и запланировать отправку

event.started / event.completed
├─ [Source] Event Service
├─ [Subscribe] User Service
└─ [Action] Обновить статистику пользователя
```

### Использование NATS в коде

**Publish event:**
```python
await nats_client.publish("event.created", payload)
```

**Subscribe to events:**
```python
await nats_client.subscribe("workout.completed", handler_func)
```

---

## Database Schema

### Shared PostgreSQL (все сервисы)

```sql
-- User Service tables
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    is_active BOOLEAN,
    created_at TIMESTAMP
);

CREATE TABLE user_ratings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    reliability_score FLOAT,
    empathy_score FLOAT
);

-- Event Service tables
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    location_id BIGINT,
    created_by BIGINT REFERENCES users(id),
    status VARCHAR,  -- PENDING, ACTIVE, COMPLETED
    scheduled_at TIMESTAMP
);

CREATE TABLE event_participants (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT REFERENCES events(id),
    user_id BIGINT REFERENCES users(id),
    status VARCHAR
);

-- Notification Service tables
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    message TEXT,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    status VARCHAR
);

-- Maps Service tables
CREATE TABLE locations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    illumination BOOLEAN,
    equipment_type VARCHAR
);
```

---

## Deployment Strategy

### Development
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
```bash
# Build images
docker build -t registry/user-service:1.0.0 backend/user_service
docker build -t registry/notif-service:1.0.0 backend/notification_service
# ... остальные

# Push to registry
docker push registry/user-service:1.0.0
docker push registry/notif-service:1.0.0
# ...

# Deploy
docker stack deploy -c docker-compose.prod.yml s2s
```

---

## Monitoring & Observability

### Health Checks
Каждый сервис имеет `/health` endpoint

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
# ...
```

### Logs
```bash
docker-compose logs user_service -f
docker-compose logs notification_service -f
```

### NATS Monitoring
http://localhost:8222 - Default NATS monitoring dashboard

---

## Масштабирование

Микросервисная архитектура позволяет:

1. **Горизонтальное масштабирование** - запустить несколько экземпляров одного сервиса
2. **Независимое развёртывание** - обновлять сервисы отдельно
3. **Асинхронная обработка** - NATS позволяет обрабатывать нагрузку в фоне
4. **Caching** - Redis для频繁запрашиваемых данных

### Example: Scale User Service
```bash
docker-compose up --scale user_service=3
```

---

## Security

- ✅ JWT authentication для API endpoints
- ✅ Bcrypt для хеширования паролей
- ✅ HTTPS в production (через reverse proxy)
- ✅ Database credentials в .env (не в коде)
- ✅ CORS настройки
- ✅ Rate limiting (опционально)

---

## Tech Stack Summary

| Layer | Tech | Version |
|:---|:---|:---|
| Framework | FastAPI | >=0.135.3 |
| ASGI | Uvicorn | >=0.44.0 |
| ORM | SQLAlchemy | >=2.0.49 |
| Database | PostgreSQL | 16-alpine |
| Cache | Redis | 7-alpine |
| Message Broker | NATS | 2-alpine |
| Container | Docker | Latest |
| Orchestration | Docker Compose | 3.9 |

---

**Last Updated:** 2026-04-09

# Gateway Service

API Gateway для микросервисной архитектуры. Обеспечивает:

- **Авторизацию** через JWT токены
- **Агрегацию данных** из разных сервисов
- **Маршрутизацию** запросов через HTTP
- **CORS** поддержку

## Структура

```
gateway/
├── main.py                      # FastAPI приложение
├── config.py                    # Конфигурация
├── core/
│   ├── security.py             # JWT токены
│   └── http_client.py          # HTTP клиент
├── api/v1/endpoints/router.py  # API маршруты
└── GATEWAY_ARCHITECTURE.md     # Подробная документация
```

## API Endpoints

### Агрегированные endpoints (`/api/v1/aggregated/`)

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/profile` | Профиль текущего пользователя |
| GET | `/nearby-places` | Места и мероприятия рядом |
| GET | `/user-meetups` | Мероприятия пользователя |
| GET | `/user-events` | События пользователя |
| GET | `/dashboard` | Полная информация (профиль, статистика, недавние элементы) |

### Системные endpoints

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/health` | Статус Gateway и HTTP клиента |
| GET | `/` | Информация о сервисе |

## Использование

### 1. Получение токена

Запратите в user_service для получения JWT токена.

### 2. Использование токена

```bash
curl -H "Authorization: Bearer <your_token>" \
  http://gateway:8000/api/v1/aggregated/profile
```

### 3. Примеры ответов

**GET `/api/v1/aggregated/profile`:**
```json
{
  "user_id": 123,
  "username": "john_doe",
  "scopes": ["read", "write"],
  "profile": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**GET `/api/v1/aggregated/dashboard`:**
```json
{
  "user": {
    "id": 123,
    "username": "john_doe",
    "profile": {...}
  },
  "stats": {
    "meetups_count": 5,
    "events_count": 3
  },
  "recent_meetups": [...],
  "recent_events": [...]
}
```

## Настройка

Создайте файл `.env` в директории gateway:

```env
APP_NAME=Gateway Service
APP_VERSION=1.0.0
ENVIRONMENT=dev
DEBUG=true

API_V1_PREFIX=/api/v1

USER_SERVICE_URL=http://localhost:8001
FORUM_SERVICE_URL=http://localhost:8002
EVENT_SERVICE_URL=http://localhost:8003
MAPS_SERVICE_URL=http://localhost:8004

HTTP_TIMEOUT=5.0

JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

CORS_ORIGINS=*
```

## Запуск

```bash
cd backend/gateway

# Установка зависимостей
pip install -e .

# Запуск сервиса
uvicorn main:app --port 8000 --reload
```

Документация API: http://localhost:8000/docs

## HTTP Endpoints сервисов

Gateway обращается к следующим endpoints сервисов:

- `GET /api/v1/users/{user_id}` → user_service
- `GET /api/v1/meetups/user/{user_id}` → forum_service
- `GET /api/v1/meetups/search?lat,lng,radius_m` → forum_service
- `GET /api/v1/places/search/nearby?lat,lng,radius` → maps_service
- `GET /api/v1/events?limit,offset,host_id` → event_service

## Архитектура

Подробное описание архитектуры и принципа работы в файле [GATEWAY_ARCHITECTURE.md](GATEWAY_ARCHITECTURE.md).

## Добавление новых endpoints

1. Откройте `api/v1/endpoints/router.py`
2. Добавьте новый endpoint с использованием `get_current_user` зависимости
3. Используйте `http_client` методы для обращения к микросервисам
4. Агрегируйте и обработайте результаты
5. Верните JSON ответ

Пример в [GATEWAY_ARCHITECTURE.md](GATEWAY_ARCHITECTURE.md#добавление-новых-endpoints).

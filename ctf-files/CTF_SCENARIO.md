# 🕵️ CTF СЦЕНАРИЙ: Operation Shoulder Takeover

## 📖 ЛОР

**Год:** 2026  
**Место:** Орёл, Россия  
**Организация:** S2S Sports — платформа для коллективных участников

В спортивном сообществе распространяются слухи о коррупции. Региональный комитет по спорту подозревает, что должностные лица S2S Sports используют платформу для отмывочных схем:
- Фальшивые "события для тренировок" создаются для перевода денег
- Администраторы удаляют доказательства о своих действиях
- Система рейтинга манипулируется в пользу определённых пользователей

**Ваша роль:** Вы — белые хакеры, нанятые главой комитета по спорту для проведения углубленного пентеста платформы S2S Sports. Ваша задача:

1. **Реконнект:** Найти токены доступа разработчиков и конфигурационные утечки
2. **Начальный доступ:** Обойти аутентификацию или получить токен простого пользователя
3. **Боковое движение:** Получить доступ к закрытым функциям сервис-администратора
4. **Привилегия эскалейшн:** Добраться до учётной записи superuser
5. **Следы атак:** Найти доски объявлений и конфиденциальные данные, подтверждающие коррупцию

---

## 🎯 ФИНАЛЬНАЯ ЦЕЛЬ

Собрать 7-10 флагов, которые вместе составляют доказательства:
- Коррупционная схема (внутренние сообщения администраторов)
- Манипулирование рейтингом
- Несанкционированные изменения в системе
- Доступ к конфиденциальным данным пользователей

---

## 🔍 ЭТАПЫ АТАКИ

### Этап 1: Разведка (Reconnaissance)

**Название:** "Изучение архитектуры"

**Задача:** Получить подробное представление об архитектуре системы. Какие микросервисы работают? Какие endpoints доступны? Что можно узнать об используемых технологиях?

**Вектор:** OSINT + API enumeration
- Обращение к `/health` endpoints находят все микросервисы
- Обращение к `/docs` выдаёт OpenAPI schemas
- Обращение к `/` показывает информацию о версиях сервисов
- Анализ CORS заголовков выдаёт информацию об allowed origins

**Флаг:** `FLAG{arch_enumeration_completed_gateway_admin_service_found}`

**Реалистичность:** В production часто забывают отключить автоматическую документацию OpenAPI на публичных endpoints.

---

### Этап 2: Поиск уязвимостей в конфигурации

**Название:** "Broken Configuration Exposed"

**Задача:** Найти конфигурационные файлы, которые содержат полезную информацию (default credentials, debug mode, уязвимые настройки).

**Вектор:** Information Disclosure via Error Messages + Debug Endpoints
- Обращение к несуществующему path выдаёт stack trace с информацией о структуре кода
- На dev environments часто остаётся debug=true
- Errors содержат SQL syntax или database information
- Health check endpoints могут выдавать информацию о internal состоянии (которые сервисы запущены, где БД и т.д.)

**Флаг:** `FLAG{debug_error_messages_exposed_db_version_8_6_detected}`

**Реалистичность:** Очень распространённая уязвимость — забыли отключить debug mode или error tracbacks.

---

### Этап 3: Анонимная регистрация

**Название:** "Creating Fake Identity"

**Задача:** Зарегистрировать обычного пользователя без верификации. Получить токен доступа.

**Вектор:** Weak Authentication Policy
- `/api/v1/auth/register` endpoint доступен без аутентификации
- Внутри системы нет проверки на real phone number (смс верификация не требуется)
- Можно регистрировать несколько аккаунтов с одного IP

**Флаг:** `FLAG{registered_fake_user_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9_base64_payload}`

**Подсказки:**
- Легкая: POST /api/v1/auth/register с phone_number, password, email
- Средняя: Используемые телефонные номера не валидируются (можно использовать +1234567890)
- Сложная: Токен содержит user_id в поле "sub", используйте его для следующих шагов

**Реалистичность:** Многие приложения не требуют верификацию номера на регистрации для ускорения onboarding.

---

### Этап 4: Горизонтальное расширение прав (IDOR)

**Название:** "Peeping at Other Profiles"

**Задача:** Получить доступ к приватным данным другого пользователя через уязвимость IDOR (Insecure Direct Object References).

**Вектор:** IDOR в User Profile Retrieval
- `/api/v1/users/{user_id}` endpoint может возвращать публичный профиль
- Однако `/api/v1/users/me` возвращает полный профиль текущего пользователя
- Если перехватить/подделать токен с другим user_id, можно получить их полные данные
- Или: используйте перебор UUID для поиска администраторского профиля

**Флаг:** `FLAG{admin_profile_accessed_email_admin@s2s_sports.local_phone_+79991234567}`

**Подсказки:**
- Легкая: Попробуйте изменить UUID в URL с вашего профиля на другой
- Средняя: UUID первого администратора часто 00000000-0000-0000-0000-000000000001 или сгенерирован в порядке создания
- Сложная: Используйте информацию из других endpoints (например, host_id из event) чтобы найти userID админа

**Обоснование реалистичности:** UUIDs предсказуемы, если они генерируются в порядке создания. IDOR часто появляется из-за отсутствия проверки владения ресурсом.

---

### Этап 5: Утечка информации через обработку ошибок

**Название:** "Error Messages Tell Secrets"

**Задача:** Используя error messages, узнать какие пользователи существуют в системе.

**Вектор:** Authentication Bypass via Username Enumeration
- `/api/v1/auth/login` возвращает разные ошибки для:
  - "User not found" vs
  - "Invalid password"
- Это позволяет перечислить всех пользователей системы

**Флаг:** `FLAG{admin_user_enumerated_admin_email_exists_in_system}`

**Подсказки:**
- Легкая: Попробуйте логиниться с разными номерами телефонов и проанализируйте ошибки
- Средняя: "User does not exist" ошибка возвращается для других кодов, чем "Invalid password"
- Сложная: Используйте этот метод чтобы найти все администраторские аккаунты

**Обоснование реалистичности:** Информационные утечки через error messages — это классическая ошибка аутентификации.

---

### Этап 6: Cache Poisoning в Media Service

**Название:** "Файлы других людей в моей папке"

**Задача:** Используя path traversal в параметре file_name, получить доступ к файлам другого пользователя.

**Вектор:** Path Traversal через недостаточную валидацию file_name
```
GET /api/v1/media/avatar/{owner_id}/{file_name:path}
```

Параметр `:path` позволяет использовать `/`, что открывает возможность для traversal:
```
GET /api/v1/media/avatar/00000000-0000-0000-0000-000000000002/../00000000-0000-0000-0000-000000000001/avatar.png
```

Это позволяет получить файлы других пользователей!

**Флаг:** `FLAG{path_traversal_admin_photo_accessed_contained_bank_account}`

**Подсказки:**
- Легкая: Используйте `../` чтобы подняться в директорию выше
- Средняя: File_name в URL может быть любой — попробуйте разные комбинации owner_id
- Сложная: MinIO хранит файлы как `avatar/{owner_id}/filename.ext`, используйте `../../` для доступа к другим owner_id

**Обоснование реалистичности:** Даже с защитой от path traversal в основном приложении, MinIO может обрабатывать пути с `../` иначе.

---

### Этап 7: SSRF через NATS Message Bus

**Название:** "Internal Service Communication Hijacking"

**Задача:** Event Service использует NATS для валидации токенов. Можно ли отправить поддельное сообщение через NATS и получить доступ без проверки?

**Вектор:** Server-Side Request Forgery (SSRF) + NATS Message Injection
- Event Service подписана на topic "auth.validate_token"
- Он отправляет запрос: `{"token": user_token}`
- Ответ от User Service обрабатывается без дополнительной валидации
- Если перехватить NATS подписку или внедрить поддельный ответ, можно подделать аутентификацию

**Флаг:** `FLAG{nats_message_spoofed_admin_token_created_without_validation}`

**Подсказки:**
- Легкая: Подключитесь к NATS серверу и подпишитесь на "auth.validate_token"
- Средняя: Отправьте поддельный ответ с "ok": true и role: superuser
- Сложная: Используйте jettison или NATS CLI для взаимодействия с message bus

**Обоснование реалистичности:** Async message buses часто не имеют аутентификации/авторизации между внутренними сервисами.

---

### Этап 8: JWT Token Manipulation

**Название:** "None Algorithm Exploit"

**Задача:** JWT токен использует HS256, но можно ли подделать токен, если узнать SECRET_KEY (или изменить algorithm на "none")?

**Вектор:** JWT Key Confusion Attack
- Если вы узнали SECRET_KEY из конфигурации или error message
- Можно создать свой JWT с любым user_id и role: superuser
- Некоторые библиотеки допускают algorithm: "none", что полностью обходит подпись

**Флаг:** `FLAG{jwt_token_signed_with_none_algorithm_role_changed_to_superuser}`

**Подсказки:**
- Легкая: Декодируйте JWT используя jwt.io и посмотрите структуру
- Средняя: Попробуйте изменить algorithm на "none" и удалить подпись
- Сложная: Используйте PyJWT или другую библиотеку чтобы создать токен с неправильной/усеченной подписью

**Обоснование реалистичности:** Некоторые реализации JWT библиотек имеют ошибки в обработке algorithm поля.

---

### Этап 9: Race Condition в Event Joining

**Название:** "Double Participation Exploit"

**Задача:** Event имеет max_participants, но есть race condition при вступлении. Нескольким пользователям может позволить присоединиться одновременно, даже если лимит исчерпан.

**Вектор:** Race Condition in Business Logic
```python
# Event Service:
async def join_event(user_id, event_id):
    event = await repo.get_by_id(event_id)
    if len(event.participants) >= event.max_participants:
        raise ValueError("Event is full")  # Check
    await repo.add_participant(event_id, user_id)  # Act (Time-of-Check-Time-of-Use)
```

Если двое одновременно проверяют лимит, оба увидят, что есть место!

**Флаг:** `FLAG{race_condition_exploited_event_overloaded_by_2_extra_users}`

**Подсказки:**
- Легкая: Создайте event с max_participants=1
- Средняя: Отправьте 3+ одновременных POST запроса на /events/{id}/join
- Сложная: Используйте Apache JMeter или custom скрипт с asyncio для отправки запросов в один момент времени

**Обоснование реалистичности:** Race conditions в бизнес-логике часто упускаются при тестировании.

---

### Этап 10: Privilege Escalation через Admin Panel Access

**Название:** "Stealing Admin Secrets from Responses"

**Задача:** Admin endpoints возвращают полную информацию о пользователях. Если получить superuser токен, можно выгрузить всю БД.

**Вектор:** Privilege Escalation + Information Disclosure
- `/api/v1/admin/users` возвращает list всех пользователей с их ролями
- Этот endpoint проверяет только через JWT `role == superuser`
- Если получить superuser токен (через предыдущие этапы), можно выгрузить все данные

**Флаг:** `FLAG{admin_user_list_exported_found_secret_admin_account_and_password_hash}`

**Подсказки:**
- Легкая: Используйте superuser токен для запроса GET /api/v1/admin/users
- Средняя: Ответ содержит email и hash пароля для всех пользователей
- Сложная: Используйте john the ripper или hashcat чтобы крэкнуть один из получспешных хешей

**Обоснование реалистичности:** Admin endpoints часто возвращают слишком много информации и полагаются только на JWT проверку.

---

### Этап 11: Lateral Movement - Hijacking Event Management

**Название:** "Modifying Tournaments for Personal Gain"

**Задача:** Используя superuser права, изменить параметры события так чтобы получить финансовое преимущество.

**Вектор:** Privilege Escalation + Business Logic Manipulation
- POST /api/v1/events/{event_id} позволяет изменить описание, место, участников
- Как superuser, можно создавать فальшивые события для отмывки денег
- Или изменять уже существующие события чтобы отменить их и вернуть деньги

**Флаг:** `FLAG{event_modified_entry_fee_increased_from_0_to_10000_rubles}`

**Подсказки:**
- Легкая: Обновите событие с PUT /api/v1/events/{event_id}
- Средняя: Измените fee_amount на большую сумму
- Сложная: Система должна записать audit log о изменениях, но если логов нет или они удаляемы — это проблема

**Обоснование реалистичности:** Финансовые manipulations через изменение параметров событий — это реальная бизнес-логика уязвимость.

---

### Этап 12: Unmasking Anonymous Events

**Название:** "Breaking Event Anonymity"

**Задача:** Some events помечены как "anonymous", но во время check-in система все равно записывает photo_url. Можно ли найти фотографии участников анонимных событий?

**Вектор:** Information Leakage despite Privacy Controls
- Field `anonymous: boolean` в модели Event
- Но в таблице `event_participants` есть `photo_url TEXT`
- Даже если event anonymous, участники могут загружать фото при check-in
- Это создаёт связь между анонимным событием и photo URL, которая может быть связана через время/место

**Флаг:** `FLAG{anonymous_event_participants_identified_through_photo_metadata_and_timestamps}`

**Подсказки:**
- Легкая: Получите all participants анонимного события через API
- Средняя: Получите photo_url для каждого участника
- Сложная: Используйте EXIF data из фотографий чтобы определить местоположение и время съёмки

**Обоснование реалистичности:** Anonymous mode часто неполностью реализован и оставляет следы через связанные данные.

---

### Этап 13: Badge System Manipulation

**Название:** "Forging Achievements"

**Задача:** Badge система используется для рейтинга пользователей. Admin может награждать badges через NATS message "admin.user.award_badge". Можно ли отправить поддельное сообщение?

**Вектор:** Message Bus Impersonation + Privilege System Bypass
```python
# NATS message:
await nc.publish("admin.user.award_badge", 
    json.dumps({"user_id": "...", "badge_type": "gold"})
)
```

Если NATS не требует аутентификацию между сервисами, можно отправить поддельное награждение.

**Флаг:** `FLAG{badge_admin_award_injected_through_nats_user_rating_spoofed}`

**Подсказки:**
- Легкая: Подключитесь к NATS и отправьте сообщение на topic "admin.user.award_badge"
- Средняя: Формат сообщения: {"user_id": "<uuid>", "badge_type": "<badge_type>"}
- Сложная: После injection проверьте что rating пользователя изменился через API

**Обоснование реалистичности:** Message buses в микросервисной архитектуре часто не имеют inter-service authentication.

---

### Этап 14: Database Query Injection через Location Service

**Название:** "Spatial Query Manipulation"

**Задача:** Maps Service использует PostGIS для пространственных запросов. Есть ли возможность для SQL injection сквозь параметры geolocation?

**Вектор:** SQL Injection in Spatial Queries
```python
# get_nearby_places принимает lat, lon и радиус
# Если параметры не санитизированы:
query = f"""
SELECT * FROM places 
WHERE ST_DWithin(
    location, 
    ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), 
    {radius}
)
"""
```

Если параметры берутся из URL без валидации, можно внедрить SQL:

```
GET /api/v1/places/nearby?lat=55.7558&lon=37.6173&radius=2000 OR 1=1
```

**Флаг:** `FLAG{sql_injection_in_spatial_query_database_error_revealed_admin_table_names}`

**Подсказки:**
- Легкая: Попробуйте добавить `OR 1=1` к параметру radius
- Средняя: Используйте `UNION SELECT` чтобы выгрузить данные из других таблиц
- Сложная: Используйте TIME-BASED BLIND SQL injection если ошибки не выводятся

**Обоснование реалистичности:** PostGIS запросы часто составляются через string formatting вместо prepared statements.

---

### Этап 15: Notification Service - Email Template Injection

**Название:** "Server-Side Template Injection"

**Задача:** Notification Service отправляет email уведомления. Если использует Jinja2 или другой template engine, можно внедрить код.

**Вектор:** Server-Side Template Injection (SSTI)
- Notification Service берёт параметры (например, display_name пользователя)
- Если они используются в email template: `Hello {{ display_name }}!`
- Можно внедрить: `{{ 7 * 7 }}` чтобы увидеть 49 в email
- Или: `{{ __import__('os').system('whoami') }}` для RCE

**Флаг:** `FLAG{ssti_in_email_template_command_execution_confirmed_whoami_output_uid=0}`

**Подсказки:**
- Легкая: Загрегистрируйте пользователя с display_name=`{{ 7 * 7 }}`
- Средняя: Получите email notification и проверьте содержит ли она "49"
- Сложная: Используйте более сложные SSTI payload для RCE

**Обоснование реалистичности:** SSTI часто появляется когда user-controlled data используется в template engine.

---

### Этап 16: Deserialization Attack через Event Data

**Название:** "Pickle Gadget Chain"

**Задача:** Event Service сохраняет данные о событиях. Если использует pickle для сериализации, можно создать malicious payload.

**Вектор:** Insecure Deserialization
```python
# Если где-то в коде:
import pickle
event_data = pickle.loads(untrusted_data)  # УЯЗВИМО!
```

Pickle позволяет выполнять произвольный Python код при десериализации.

**Флаг:** `FLAG{pickle_deserialization_rce_achieved_reverse_shell_established}`

**Подсказки:**
- Легкая: Создайте malicious pickled object используя ysoserial.py (Python版)
- Средняя: Передайте объект через параметр которого будет десериализирован
- Сложная: Используйте gadget chains чтобы достичь RCE

**Обоснование реалистичности:** Insecure deserialization — это OWASP Top 10 уязвимость.

---

### Этап 17: Data Exfiltration через Backup Files

**Название:** "Finding Leaked Database Backups"

**Задача:** Разработчики иногда сохраняют SQL dump файлы на сервере. Можно ли их найти через path traversal?

**Вектор:** Exposed Backup Files + Path Traversal
- Media Service endpoint для получения файлов по пути
- Путём перехода в директории выше можно достичь `/var/backups/` или `/home/backup/`
- Найти `postgres_backup_2026-01-15.sql` или похожие файлы
- Выгрузить их содержимое

**Флаг:** `FLAG{database_backup_exposed_credentials_admin_password_found_in_sql_dump}`

**Подсказки:**
- Легкая: Используйте path traversal чтобы подняться в корень
- Средняя: Попробуйте common backup locations: /backups/, /dumps/, ../../backups/
- Сложная: Найденный SQL dump содержит INSERT с паролями

**Обоснование реалистичности:** Backup файлы часто забывают удалять или они хранятся с неправильными permissions.

---

### Этап 18: Lateral Movement - Admin API Access from Compromised Service

**Название:** "Internal Service Takeover"

**Задача:** Если вы скомпрометировали один микросервис (например, Media Service), можно ли использовать его для доступа к Admin Service?

**Вектор:** Compromised Internal Service as Stepping Stone
- Все сервисы находятся в одной Docker network (s2s_network)
- Они могут взаимодействовать напрямую (например, media_service может обращаться к admin_service по http://s2s_admin_service:8003)
- Если не требуется аутентификация между сервисами, можно напрямую обращаться к admin endpoints
- Или можно перехватить трафик между сервисами

**Флаг:** `FLAG{internal_service_admin_api_accessed_without_authentication_inside_docker_network}`

**Подсказки:**
- Легкая: Используйте DNS имена сервисов внутри Docker network
- Средняя: Отправьте POST запрос to http://admin_service:8003/api/v1/admin/users от compromised service
- Сложная: Network policies и firewall rules между сервисами отсутствуют

**Обоснование реалистичности:** Микросервисная архитектура часто недостаточно защищена при взаимодействии между сервисами.

---

### Этап 19: Zero-Day in Frontend Reflected XSS

**Название:** "DOM-based XSS via Location Parameter"

**Задача:** Frontend приложение отображает пользовательский input без санации. Если вставить JavaScript payload в параметр, он выполнится.

**Вектор:** Reflected XSS
- Frontend получает параметр `?search=<user_input>`
- Отображает его без HTML encoding: `<h1>Results for: {searchParam}</h1>`
- Можно отправить: `?search=<img src=x onerror="fetch('/api/v1/users/me')">`
- Браузер выполнит JavaScript и получит данные пользователя

**Флаг:** `FLAG{reflected_xss_executed_user_cookies_and_tokens_exfiltrated}`

**Подсказки:**
- Легкая: Создайте URL с XSS payload и отправьте админу
- Средняя: Payload должен быть URL encoded
- Сложная: Используйте cookie stealing чтобы получить session tokens

**Обоснование реалистичности:** XSS уязвимости в React приложениях остаются актуальны, особенно если используется dangerouslySetInnerHTML.

---

### Этап 20: Chained Attack - Complete System Compromise

**Название:** "Operation Shoulder Takeover - Final Phase"

**Задача:** Используя все полученные знания, создать полную цепь атак:
1. Зарегистрироваться как обычный пользователь
2. Найти admin профиль через IDOR
3. Получить superuser токен (через JWT manipulation или NATS injection)
4. Выгрузить всех пользователей
5. Найти финансовые транзакции в database backup
6. Изменить события для отмывки денег
7. Создать audit trail стирание

**Вектор:** Multi-stage Attack Chain

**Флаг:** `FLAG{complete_system_compromise_audit_logs_cleared_backdoor_installed_on_admin_db}`

**Подсказки:**
- Легкая: Следуйте всем предыдущим этапам по порядку
- Средняя: Создайте скрипт который автоматизирует несколько шагов
- Сложная: Найдите способ остаться в системе даже после логин компрометированного аккаунта

**Обоснование реалистичности:** Реальные взломы редко используют одиночную уязвимость — всегда это цепь действий.

---

## 🛠️ ТЕХНИЧЕСКИЕ ДЕТАЛИ ДЛЯ ОРГАНИЗАТОРОВ

### Размещение флагов

| Этап | Флаг | Расположение | Получение |
|------|------|--------------|-----------|
| 1 | `FLAG{arch_enumeration_completed_gateway_admin_service_found}` | Response от `/health` endpoints | GET /gateway:8005/health и другие сервисы |
| 2 | `FLAG{debug_error_messages_exposed_db_version_8_6_detected}` | Stack trace при ошибке | GET /invalid_path, посмотреть error message |
| 3 | `FLAG{registered_fake_user_token_...}` | JWT в response POST /auth/register | POST /api/v1/auth/register |
| 4 | `FLAG{admin_profile_accessed_...}` | Response от admin profile | GET /api/v1/users/{admin_uuid} |
| 5 | `FLAG{admin_user_enumerated_...}` | Error message при login | POST /api/v1/auth/login |
| 6 | `FLAG{path_traversal_admin_photo_accessed_...}` | File retrieved через path traversal | GET /api/v1/media/avatar/{id}/../../../admin/photo.png |
| 7 | `FLAG{nats_message_spoofed_admin_token_created...}` | Created token через NATS injection | Directly interact with NATS |
| 8 | `FLAG{jwt_token_signed_with_none_algorithm_...}` | Создаваемый токен | Modify JWT locally и use |
| 9 | `FLAG{race_condition_exploited_event_overloaded...}` | Event с нарушенным max_participants | Multiple simultaneous requests |
| 10 | `FLAG{admin_user_list_exported_found_secret...}` | Response от /admin/users | GET /api/v1/admin/users |
| 11 | `FLAG{event_modified_entry_fee_increased...}` | Modified event data | PUT /api/v1/events/{event_id} |
| 12 | `FLAG{anonymous_event_participants_identified...}` | Photo metadata | Access participant photos + EXIF |
| 13 | `FLAG{badge_admin_award_injected_through_nats...}` | Modified user rating | NATS message injection + check rating |
| 14 | `FLAG{sql_injection_in_spatial_query_...}` | Database error | GET /api/v1/places/nearby?lat=55 OR 1=1 |
| 15 | `FLAG{ssti_in_email_template_...}` | Email content с результатом | Email notification |
| 16 | `FLAG{pickle_deserialization_rce_achieved...}` | RCE output | Custom pickled payload |
| 17 | `FLAG{database_backup_exposed_credentials...}` | SQL dump content | Path traversal to /backups/ |
| 18 | `FLAG{internal_service_admin_api_accessed...}` | Admin API response | Internal Docker network request |
| 19 | `FLAG{reflected_xss_executed_user_cookies...}` | Stolen tokens/cookies | XSS payload in URL |
| 20 | `FLAG{complete_system_compromise_...}` | Comprehensive proof | All previous stages combined |

### Настройка уязвимостей

#### Этап 1: Оставить debug endpoints открытыми
```bash
# В docker-compose.yml, убедиться что все /health endpoints доступны
# В .env установить ENVIRONMENT=development для включения debug трассировки
```

#### Этап 2: Включить error traceback
```python
# В core/config.py:
DEBUG = True  # Включить для development
```

#### Этап 3: Отключить верификацию номера телефона
```python
# В auth_service.py закомментировать или отключить:
# await self.send_verification_sms(phone_number)
# await self.verify_sms_code(phone_number, code)
```

#### Этап 6: Оставить path traversal в media service
```python
# В media.py НЕ добавлять проверку:
# file_name = os.path.normpath(file_name)
# if '..' in file_name:
#     raise HTTPException(400, "Invalid path")
```

#### Этап 7: Оставить NATS без аутентификации
```yaml
# В docker-compose.yml:
nats:
  command: ["-js", "-m", "8222"]  # Без --auth flag
```

#### Этап 8: Использовать слабый SECRET_KEY
```python
# В .env:
SECRET_KEY=CHANGE_ME_GENERATE_64_RANDOM_CHARS  # Default слабый ключ
```

### Ожидаемое время прохождения

- **Beginner path (этапы 1-5):** 2-3 часа
- **Intermediate path (этапы 1-10):** 4-6 часов
- **Advanced path (этапы 1-15):** 8-12 часов
- **Expert path (этапы 1-20):** 16+ часов

### Необходимые инструменты

**Стандартные:**
- curl, wget
- Postman, Insomnia
- Burp Suite Community Edition
- JWT decoder (jwt.io)

**Git-based:**
- jq (JSON query)
- python3 + PyJWT
- nats-cli (для взаимодействия с NATS)

**Advanced:**
- Apache JMeter (для race conditions)
- SQLMap (для SQLi)
- Wireshark (для network analysis)
- nmap (для reconnaissance)
- john the ripper (для cracking хешей)

### Лог-система для отслеживания

```python
# Добавить в каждый сервис:
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)

# Логировать:
- Все попытки аутентификации
- Все запросы к privileged endpoints
- Все изменения в БД
- Все NATS сообщения (в режиме debug)
```

### Scoring System

```
Этап 1: 10 баллов (разведка)
Этап 2: 15 баллов (информационная утечка)
Этап 3: 20 баллов (начальный доступ)
Этап 4: 25 баллов (IDOR)
Этап 5: 15 баллов (username enumeration)
Этап 6: 30 баллов (path traversal)
Этап 7: 35 баллов (SSRF via NATS)
Этап 8-20: 40+ баллов каждый

TOTAL: 500+ баллов
```

---

## 📋 КОНТРОЛЬНЫЙ СПИСОК ДЛЯ ОРГАНИЗАТОРОВ

- [ ] Убедитесь что все микросервисы запущены и здоровы
- [ ] Проверьте что default SECRET_KEY используется  
- [ ] Отключите SMS верификацию в auth service
- [ ] Оставьте debug mode включённым
- [ ] Убедитесь что NATS не требует аутентификацию
- [ ] Создайте несколько test пользователей с разными ролями (superuser, moderator, user)
- [ ] Создайте test события с разными параметрами
- [ ] Загрузите test файлы в MinIO
- [ ] Создайте database backup файл в доступной директории
- [ ] Установите time limit для CTF (обычно 8-12 часов)
- [ ] Подготовьте Discord/Telegram канал для подсказок
- [ ] Создайте таблицу лидеров для отслеживания прогресса

---

## 🎓 ОБУЧАЮЩИЕ МОМЕНТЫ

Каждый этап преподаёт:
1. **OSINT & Reconnaissance** — как собирать информацию о системе
2. **Authentication & Authorization** — слабые точки в аутентификации
3. **API Security** — IDOR, parameter manipulation
4. **Micro-services Security** — inter-service communication risks
5. **Data Protection** — encryption, sanitization
6. **Business Logic** — race conditions, workflow exploitation
7. **Infrastructure** — network segmentation, secrets management

---

## 🚀 ВОЗМОЖНЫЕ РАСШИРЕНИЯ

- Добавить Kubernetes deployment для более сложной архитектуры
- Добавить frontend-based атаки (XSS, CSRF)
- Добавить криптографические уязвимости (weak algorithms, key derivation)
- Добавить timing attacks на password hashing
- Добавить cloud-based attacks (AWS bucket misconfiguration, etc)


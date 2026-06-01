# 🤝 Плечом к плечу — Архитектура проекта | Орловское ФСП

> Микросервисная архитектура приложения для коллективных уличных тренировок

**Версия:** 1.0  
**Дата:** Июнь 2026  
**Статус:** Prototype

---

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Фронтенд-приложение](#фронтенд-приложение)
4. [Микросервисы](#микросервисы)
5. [Поток данных](#поток-данных)
6. [API Endpoints](#api-endpoints)
7. [Инфраструктура](#инфраструктура)

---

## 🎯 Обзор проекта

### Назначение
«Плечом к плечу» — приложение для поиска компании единомышленников для бесплатных спортивных тренировок на уличных площадках. Решает проблему психологического барьера и одиночества при выходе на спорт.

### Ключевые функции
- 🗺️ **Карта доступного спорта** — библиотека бесплатных спортплощадок с фильтрацией
- 👥 **Сбор «Не один»** — создание и вступление в группы из 2–10 участников
- 📊 **Рейтинг участников** — метрики эмпатии и надежности
- 🚶 **Совместные маршруты** — безопасный путь до спота с синхронизацией
- 🎭 **Анонимные встречи** — форматы для интровертов

### Масштаб
- **Пилот:** г. Орёл
- **Целевая аудитория:** 18–35 лет, новички, интроверты
- **Модель:** Бесплатная, социальная, c верификацией

---

## 🏗️ Архитектура системы

```mermaid
graph TB
    subgraph Frontend["🌐 Фронтенд (Vue 3 + Vite)"]
        App["App.vue"]
        Pages["Pages<br/>MainPage<br/>EventsPage<br/>MapLight<br/>Profile<br/>Rating"]
        Components["Components<br/>Reusable UI<br/>Forms<br/>Cards<br/>Modal"]
        API["API Client<br/>Fetch API<br/>URL Proxy"]
        Stores["State Management<br/>localStorage<br/>navigationStore"]
    end

    subgraph Gateway["🚪 Gateway/Proxy (Port 8000)"]
        GW["API Gateway<br/>CORS Handler<br/>Route Aggregator"]
    end

    subgraph Services["🔧 Микросервисы (FastAPI)"]
        UserService["👤 User Service (8000)<br/>• Аутентификация<br/>• Профили пользователей<br/>• Рейтинг & Badges<br/>• Матчинг"]
        EventService["📅 Event Service (8002)<br/>• CRUD Events<br/>• Управление участниками<br/>• Статусы встреч<br/>• Фото после встреч"]
        MapsService["🗺️ Maps Service (8004)<br/>• Библиотека мест<br/>• Маршруты (OSRM)<br/>• Геопоиск<br/>• Освещение & фильтры"]
        MediaService["📂 Media Service (8006)<br/>• Upload в S3/MinIO<br/>• Генерация presigned URLs<br/>• Управление аватарами<br/>• Кэширование медиа"]
        AdminService["🎛️ Admin Service<br/>• Модерация контента<br/>• Управление местами<br/>• Аналитика<br/>• Блокировка пользователей"]
        NotificationService["🔔 Notification Service<br/>• Push-уведомления<br/>• Email отправка<br/>• SMS интеграция<br/>• Scheduling"]
        AIService["🤖 AI Service<br/>• Обработка фото встреч<br/>• Распознавание лиц<br/>• Валидация места<br/>• Рекомендации"]
    end

    subgraph MessageQueue["📨 Асинхронная коммуникация"]
        NATS["NATS Server<br/>Event Bus<br/>Pub/Sub"]
    end

    subgraph Database["🗄️ Хранилище данных"]
        PostgreSQL["PostgreSQL<br/>+ PostGIS<br/>• Users & Auth<br/>• Events & Participants<br/>• Places & Routes<br/>• Media metadata"]
        MinIO["MinIO S3<br/>• Avatars<br/>• Event photos<br/>• Files"]
        Redis["Redis<br/>• Cache<br/>• Sessions<br/>• Rate limiting"]
    end

    subgraph External["🌍 Внешние сервисы"]
        OSRM["OSRM API<br/>Маршрутизация"]
        Maps["Leaflet.js<br/>Картография"]
        Google["Google API<br/>Геолокация"]
    end

    subgraph DevOps["⚙️ Инфраструктура"]
        Docker["Docker<br/>Контейнеризация"]
        Compose["Docker Compose<br/>Оркестрация"]
    end

    %% Frontend to Services
    App -->|REST| GW
    Pages -->|REST| API
    API -->|proxy| GW
    Stores -->|sync| API
    
    %% Gateway to Services
    GW -->|port8000| UserService
    GW -->|port8002| EventService
    GW -->|port8004| MapsService
    GW -->|port8006| MediaService
    GW -->|admin| AdminService
    GW -->|notify| NotificationService
    
    %% Inter-Service Communication
    UserService -->|pub-sub| NATS
    EventService -->|pub-sub| NATS
    MediaService -->|pub-sub| NATS
    NotificationService -->|sub| NATS
    AIService -->|sub| NATS
    AdminService -->|sub| NATS
    
    %% Database connections
    UserService -->|SQL| PostgreSQL
    EventService -->|SQL| PostgreSQL
    MapsService -->|SQL| PostgreSQL
    MediaService -->|SQL| PostgreSQL
    AdminService -->|SQL| PostgreSQL
    
    %% Media storage
    MediaService -->|S3| MinIO
    
    %% Caching
    UserService -->|cache| Redis
    EventService -->|cache| Redis
    MapsService -->|cache| Redis
    
    %% External APIs
    MapsService -->|API| OSRM
    Pages -->|Leaflet| Maps
    App -->|Geolocation| Google
    
    %% DevOps
    Docker -.->|deploy| Services
    Compose -.->|orchest| Docker
    
    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef service fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef db fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef infra fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class Frontend frontend
    class UserService,EventService,MapsService,MediaService,AdminService,NotificationService,AIService service
    class PostgreSQL,MinIO,Redis db
    class OSRM,Maps,Google external
    class Docker,Compose infra
```

---

## 🌐 Фронтенд-приложение

### Технологический стек
- **Framework:** Vue 3 (Composition API)
- **Builder:** Vite
- **Routing:** Vue Router
- **Cartography:** Leaflet.js
- **Styling:** Tailwind CSS + Custom CSS
- **Storage:** localStorage (для синхронизации между вкладками)
- **API Client:** Fetch API (с логированием)

### Структура папок

```
frontend/app/src/
├── components/          # Vue компоненты
│   ├── MainPage.vue     # Главная страница с картой и встречами
│   ├── EventsPage.vue   # Список всех встреч + создание
│   ├── MapLight.vue     # Полноэкранная карта с навигацией
│   ├── Profile.vue      # Профиль пользователя
│   ├── Rating.vue       # Рейтинг пользователей
│   └── ...
├── views/               # Page views
├── router/              # Vue Router конфигурация
├── stores/              # Состояние (navigationStore)
├── api/                 # API клиент
│   └── index.js         # Экспорт authApi, mediaGetApi
├── config.js            # Конфигурация API URLs
└── style.css            # Глобальные стили
```

### Ключевые страницы

#### 1. **MainPage** (/)
Главная страница с:
- Профилем пользователя (аватар, score эмпатии)
- Мини-картой с текущим местоположением
- Списком "Ваши встречи" (joined events)
- Интересными фактами (carousel каждые 3 минуты)
- Кнопкой "Создать встречу"

**Отправляемые запросы:**
```
GET /api/v1/users/me              # Загрузка профиля
GET /api/v1/users/me/rating       # Рейтинг пользователя
GET /api/v1/places                # Список мест для встреч
GET /api/v1/events                # События пользователя
```

#### 2. **EventsPage** (/events)
Страница со всеми встречами:
- Табы фильтрации (все, бег, йога, силовая, воркаут)
- Список встреч с картами участников
- Кнопка вступления/выхода
- Модалка создания встречи

**Отправляемые запросы:**
```
GET /api/v1/events                # Все события
POST /api/v1/events               # Создание события
POST /api/v1/events/{id}/join     # Вступление
POST /api/v1/events/{id}/leave    # Выход
```

#### 3. **MapLight** (/map)
Полноэкранная интерактивная карта:
- Слой мест (спортплощадки)
- Маршруты между точками
- Навигация GPS с лайв-трекингом
- Фильтры по типу места, освещению, шуму

**Отправляемые запросы:**
```
GET /api/v1/places                # Места на карте
GET /api/v1/routes/build?from=X&to=Y  # Построение маршрута
POST /api/v1/events/{id}/photo    # Загрузка фото после встречи
```

#### 4. **Profile** (/profile)
Профиль с:
- Аватаром пользователя
- Редактируемыми данными (имя, описание)
- Историей встреч
- Бейджами и достижениями
- Загрузкой аватара

**Отправляемые запросы:**
```
GET /api/v1/users/me              # Загрузка профиля
PUT /api/v1/users/me              # Обновление профиля
POST /api/v1/media/upload-url     # Получение presigned URL
POST (to S3)                      # Загрузка файла
```

#### 5. **Rating** (/rating)
Рейтинг пользователей:
- Топ по эмпатии
- Топ по надежности
- История взаимодействий

**Отправляемые запросы:**
```
GET /api/v1/users/me/rating       # Мой рейтинг
GET /api/v1/users/[id]            # Профиль другого пользователя
GET /api/v1/users                 # Список всех пользователей
```

### API Client (`api/index.js`)

Экспортирует несколько объектов:

```javascript
// Аутентификация & профиль
authApi.register(data)             // Регистрация
authApi.login(data)                // Логин
authApi.getProfile()               // Загрузка профиля
authApi.updateProfile(data)        // Обновление профиля
authApi.getRating()                // Рейтинг пользователя
authApi.getBadges()                // Бейджи
authApi.getPublicProfile(userId)   // Профиль другого юзера
authApi.getUploadUrl(...)          // Presigned URL для S3
authApi.uploadToS3({...})          // Загрузка в S3

// Медиа
mediaGetApi.getMediaUrl(category, userId, fileName)
mediaGetApi.getDirectUrl(...)

// Helper функции
toProxyUrl(url)                    // Конверт IP в localhost
normalizePhone(phone)              // Нормализация телефона
```

---

## ⚙️ Микросервисы

### 1️⃣ User Service (Port 8000)

**Назначение:** Управление пользователями, аутентификация, рейтинг

**Основные модели:**
- `User` — базовый пользователь (phone, password, display_name, email)
- `UserProfile` — расширенный профиль (bio, avatar_url, interests)
- `UserRating` — метрики (empathy_score, reliability_score, badges)
- `Badge` — достижения (verified, top_empath, reliable и т.д.)

**API Endpoints:**
```
POST   /api/v1/auth/register                    # Регистрация по телефону
POST   /api/v1/auth/login                       # Логин
GET    /api/v1/users/me                         # Текущий пользователь
PUT    /api/v1/users/me                         # Обновление профиля
GET    /api/v1/users/me/rating                  # Рейтинг
GET    /api/v1/users/me/badges                  # Бейджи пользователя
GET    /api/v1/users/me/contact                 # Контактная информация
PUT    /api/v1/users/me/contact                 # Обновление контактов
GET    /api/v1/users/{id}                       # Профиль конкретного пользователя
GET    /api/v1/users                            # Список всех пользователей
POST   /api/v1/users/me/theme                   # Сохранение темы
GET    /api/v1/matches/workout-requests         # Запросы на встречи
POST   /api/v1/matches/workout-requests         # Создание запроса
POST   /api/v1/matches/respond                  # Ответ на запрос
```

**Взаимодействие с другими сервисами:**
- **Event Service** — отслеживание встреч и обновление рейтинга
- **Media Service** — загрузка аватара
- **NATS** — публикация событий (user_created, rating_updated, badge_earned)

**База данных:**
```sql
-- Основные таблицы
users (id, phone_number, password_hash, display_name, email, created_at)
user_profiles (user_id, bio, avatar_url, interests, preferences)
user_ratings (user_id, empathy_score, reliability_score, total_workouts)
badges (user_id, badge_type, earned_at)
workout_requests (id, from_user_id, to_user_id, status, created_at)
```

---

### 2️⃣ Event Service (Port 8002)

**Назначение:** Управление встречами (events) и участниками

**Основные модели:**
- `Event` — встреча (name, type, date, time, spot_id, host_id, max_participants, anonymous)
- `EventParticipant` — участник встречи (event_id, user_id, status, photo_url, joined_at)

**API Endpoints:**
```
GET    /api/v1/events                           # Все события
GET    /api/v1/events?filter=my_joined          # Мои встречи
POST   /api/v1/events                           # Создать событие
GET    /api/v1/events/{id}                      # Детали события
PUT    /api/v1/events/{id}                      # Обновить событие
DELETE /api/v1/events/{id}                      # Удалить событие
POST   /api/v1/events/{id}/join                 # Присоединиться
POST   /api/v1/events/{id}/leave                # Выйти из встречи
GET    /api/v1/events/{id}/participants         # Список участников
POST   /api/v1/events/{id}/photo                # Загрузить фото после встречи
```

**Взаимодействие с другими сервисами:**
- **User Service** — валидация user_id, получение рейтинга
- **Maps Service** — валидация spot_id
- **Media Service** — загрузка фото встреч
- **NATS** — публикация (event_created, event_joined, photo_uploaded)

**База данных:**
```sql
events (
    id, name, description, type, date, time, level,
    host_id, spot_id, custom_lat, custom_lng, custom_address,
    max_participants, status, anonymous, quiet_companion,
    created_at, updated_at
)

event_participants (
    id, event_id, user_id, status, photo_url,
    joined_at, photo_uploaded_at, verified_attendance
)
```

---

### 3️⃣ Maps Service (Port 8004)

**Назначение:** Картография, библиотека мест, маршруты

**Основные модели:**
- `Place` (SportsGround) — спортплощадка (name, lat, lon, address, activity_type, emoji, lighting, noise_level)
- `Route` — сохраненные маршруты (start_point, end_point, distance, duration, coordinates)

**API Endpoints:**
```
GET    /api/v1/places                           # Все спортплощадки
GET    /api/v1/places?activity=running&limit=5 # Фильтрованные места
POST   /api/v1/places                           # Добавить место (пользователь)
GET    /api/v1/places/{id}                      # Детали места
PUT    /api/v1/places/{id}                      # Обновить место
DELETE /api/v1/places/{id}                      # Удалить место

GET    /api/v1/routes/build?from=X,Y&to=A,B   # Построить маршрут (OSRM)
GET    /api/v1/routes?start_id=1&end_id=2     # Маршрут между местами
POST   /api/v1/routes                          # Сохранить маршрут
GET    /api/v1/routes/{id}                     # Получить сохраненный маршрут
```

**Внешние зависимости:**
- **OSRM** (Open Source Routing Machine) — маршрутизация
- **PostGIS** — геопространственные запросы

**База данных:**
```sql
sports_grounds (
    id, name, address, lat, lon, activity_type,
    emoji, lighting_quality, noise_level, accessibility,
    user_submitted, verified, created_at, updated_at
)

routes (
    id, start_point_lat, start_point_lon,
    end_point_lat, end_point_lon,
    distance_meters, duration_seconds,
    coordinates_geojson, osrm_response,
    created_at
)
```

---

### 4️⃣ Media Service (Port 8006)

**Назначение:** Управление медиа файлами (S3/MinIO), авторизованная загрузка

**Основные модели:**
- `MediaFile` — метаданные файла (owner_id, file_name, file_path, size, content_type, purpose, uploaded_at)

**API Endpoints:**
```
POST   /api/v1/media/upload-url                 # Получить presigned POST URL для S3
GET    /api/v1/avatar/{owner_id}/{file_name}   # Получить аватар
GET    /api/v1/event/{event_id}/{file_name}    # Получить фото встречи
GET    /api/v1/media/{id}                       # Метаданные файла
DELETE /api/v1/media/{id}                       # Удалить файл
```

**Взаимодействие с другими сервисами:**
- **S3/MinIO** — хранилище файлов
- **User Service** — валидация owner_id
- **Event Service** — валидация event_id

**Поток загрузки:**
1. Frontend запрашивает presigned URL: `POST /upload-url`
2. Media Service генерирует URL с подписью S3
3. Frontend загружает файл напрямую в S3 (обход бэкенда)
4. Frontend уведомляет Media Service: `POST /avatar/complete`
5. Media Service сохраняет метаданные в БД

**База данных:**
```sql
media_files (
    id, owner_id, event_id, file_name, file_path,
    file_size, content_type, purpose (avatar/event_photo/...),
    uploaded_at, deleted_at
)
```

---

### 5️⃣ Admin Service

**Назначение:** Модерация контента, управление системой

**Функционал:**
- Одобрение/отклонение новых мест
- Блокировка/разблокировка пользователей
- Удаление/скрытие событий
- Просмотр аналитики
- Управление бейджами

**API Endpoints:**
```
GET    /api/v1/admin/pending-places             # Места на модерации
PUT    /api/v1/admin/places/{id}/approve        # Одобрить место
DELETE /api/v1/admin/places/{id}/reject         # Отклонить место

GET    /api/v1/admin/users/{id}                 # Информация о пользователе
POST   /api/v1/admin/users/{id}/block           # Заблокировать
POST   /api/v1/admin/users/{id}/unblock         # Разблокировать

GET    /api/v1/admin/analytics                  # Статистика
GET    /api/v1/admin/events/{id}/verify         # Верифицировать встречу
```

---

### 6️⃣ Notification Service

**Назначение:** уведомления и коммуникация

**Каналы:**
- Push-уведомления
- Email
- SMS (опционально)
- In-app messages

**События для оповещения:**
- Пользователь присоединился к встрече
- Встреча отменена
- Начинается совместный маршрут
- Новый активный рейтинг
- Бейдж получен

**Интеграция:**
- Подписывается на NATS события
- Использует очередь для отправки

---

### 7️⃣ AI Service (будущее)

**Назначение:** Обработка фото и аналитика

**Функционал:**
- Распознавание лиц на фото встреч
- Валидация места (проверка что встреча была там)
- Рекомендации встреч на основе истории
- Обнаружение аномалий

---

## 📨 Поток данных

### Сценарий: Пользователь создает встречу

```mermaid
sequenceDiagram
    participant User as "🧑 Пользователь"
    participant Frontend as "🌐 Фронтенд (Vue)"
    participant Gateway as "🚪 Gateway"
    participant EventSvc as "📅 Event Service"
    participant MapsSvc as "🗺️ Maps Service"
    participant UserSvc as "👤 User Service"
    participant NATS as "📨 NATS"
    participant NotifSvc as "🔔 Notification"
    participant DB as "🗄️ PostgreSQL"

    User->>Frontend: Открывает EventsPage и нажимает кнопку
    Frontend->>Frontend: Загружает места с API
    Frontend->>Gateway: GET places endpoint
    Gateway->>MapsSvc: Request places
    MapsSvc->>DB: Query sports grounds
    DB-->>MapsSvc: Place data
    MapsSvc-->>Gateway: Response data
    Gateway-->>Frontend: Success

    Frontend->>User: Shows form
    User->>Frontend: Fills form and submits

    Frontend->>Frontend: Validates form
    Frontend->>Gateway: POST events endpoint

    Gateway->>UserSvc: Validate user
    UserSvc->>DB: Query user data
    DB-->>UserSvc: User record
    UserSvc-->>Gateway: OK

    Gateway->>MapsSvc: Validate spot ID
    MapsSvc->>DB: Query spot data
    DB-->>MapsSvc: Spot record
    MapsSvc-->>Gateway: OK

    Gateway->>EventSvc: POST create event
    EventSvc->>DB: Insert event
    DB-->>EventSvc: Event created

    EventSvc->>DB: Insert participant
    DB-->>EventSvc: Done

    EventSvc->>NATS: Publish event created

    NATS-->>NotifSvc: Subscribe message
    NotifSvc->>UserSvc: Get user friends
    NotifSvc->>NotifSvc: Send notifications

    EventSvc-->>Gateway: 201 Created
    Gateway-->>Frontend: Success

    Frontend->>Frontend: Save to localStorage
    Frontend->>User: Show success message
```

### Сценарий: Пользователь присоединяется к встрече

```mermaid
sequenceDiagram
    participant User as "🧑 Пользователь"
    participant Frontend as "🌐 Фронтенд"
    participant EventSvc as "📅 Event Service"
    participant NotifSvc as "🔔 Notification"
    participant NATS as "📨 NATS"

    User->>Frontend: Opens page and joins event
    Frontend->>EventSvc: POST join event
    EventSvc->>EventSvc: Validate slots and user
    EventSvc->>EventSvc: Add participant
    EventSvc->>NATS: Publish event joined

    NATS-->>NotifSvc: Subscribe message
    NotifSvc->>NotifSvc: Send notification

    EventSvc-->>Frontend: Success response
    Frontend->>Frontend: Update UI
    Frontend->>User: Show success
```

### Сценарий: Пользователь строит маршрут на карте

```mermaid
sequenceDiagram
    participant User as "🧑 Пользователь"
    participant Frontend as "🌐 MapLight.vue"
    participant MapsSvc as "🗺️ Maps Service"
    participant OSRM as "🛣️ OSRM API"
    participant Leaflet as "🗺️ Leaflet"

    User->>Frontend: Open MapLight and build route
    Frontend->>Frontend: Show form
    User->>Frontend: Select start and end points

    Frontend->>MapsSvc: GET build route
    MapsSvc->>OSRM: GET route for pedestrian
    Note over MapsSvc,OSRM: Request routing API
    OSRM-->>MapsSvc: Route coordinates
    MapsSvc->>MapsSvc: Parse response
    MapsSvc-->>Frontend: Route data

    Frontend->>Leaflet: Draw route
    Frontend->>User: Show route on map

    User->>Frontend: Start navigation
    Frontend->>Frontend: Start GPS tracking
    Frontend->>Frontend: Draw user marker
    loop Every 2 seconds
        Frontend->>Frontend: Get position
        Frontend->>Frontend: Update marker
        Frontend->>Frontend: Update distance
        Frontend->>User: Show remaining
    end

    User->>Frontend: End navigation
    Frontend->>Frontend: Stop GPS
    Frontend->>Frontend: Clear route
    Frontend->>User: Show completion
```

---

## 🔌 API Endpoints

### Frontend → Gateway / Services

| Метод | Endpoint | Service | Description |
|:---:|:---|:---|:---|
| **Authentication** | | | |
| POST | `/api/v1/auth/register` | User | Регистрация по телефону |
| POST | `/api/v1/auth/login` | User | Логин |
| POST | `/api/v1/auth/logout` | User | Выход |
| **User Management** | | | |
| GET | `/api/v1/users/me` | User | Текущий пользователь |
| PUT | `/api/v1/users/me` | User | Обновление профиля |
| GET | `/api/v1/users/{id}` | User | Профиль другого |
| GET | `/api/v1/users/me/rating` | User | Рейтинг |
| GET | `/api/v1/users/me/badges` | User | Бейджи |
| GET | `/api/v1/users` | User | Все пользователи |
| **Events** | | | |
| GET | `/api/v1/events` | Event | Все события |
| POST | `/api/v1/events` | Event | Создать событие |
| GET | `/api/v1/events/{id}` | Event | Детали события |
| PUT | `/api/v1/events/{id}` | Event | Обновить событие |
| DELETE | `/api/v1/events/{id}` | Event | Удалить событие |
| POST | `/api/v1/events/{id}/join` | Event | Присоединиться |
| POST | `/api/v1/events/{id}/leave` | Event | Выйти |
| POST | `/api/v1/events/{id}/photo` | Event/Media | Загрузить фото встречи |
| **Places** | | | |
| GET | `/api/v1/places` | Maps | Все спортплощадки |
| POST | `/api/v1/places` | Maps | Добавить место |
| GET | `/api/v1/places/{id}` | Maps | Детали места |
| PUT | `/api/v1/places/{id}` | Maps | Обновить место |
| DELETE | `/api/v1/places/{id}` | Maps | Удалить место |
| **Routes** | | | |
| GET | `/api/v1/routes/build` | Maps | Построить маршрут (OSRM) |
| POST | `/api/v1/routes` | Maps | Сохранить маршрут |
| GET | `/api/v1/routes/{id}` | Maps | Получить маршрут |
| **Media** | | | |
| POST | `/api/v1/media/upload-url` | Media | Получить presigned URL |
| GET | `/api/v1/avatar/{owner_id}/{file_name}` | Media | Аватар |
| GET | `/api/v1/event/{event_id}/{file_name}` | Media | Фото встречи |

---

## ⚙️ Инфраструктура

### Docker Compose Setup

```yaml
version: '3.9'

services:
  # Базовая инфраструктура
  postgres:
    image: postgres:15-alpine
    ports: [5432:5432]
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_INITDB_ARGS: -c shared_preload_libraries=postgis-3

  redis:
    image: redis:7-alpine
    ports: [6379:6379]

  minio:
    image: minio/minio:latest
    ports: [9000:9000, 9001:9001]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

  nats:
    image: nats:2.9-alpine
    ports: [4222:4222]

  # Backend сервисы
  user-service:
    build: ./backend/user_service
    ports: [8000:8000]
    depends_on: [postgres, nats]
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/users
      NATS_URL: nats://nats:4222

  event-service:
    build: ./backend/event_service
    ports: [8002:8002]
    depends_on: [postgres, nats]
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/events
      NATS_URL: nats://nats:4222

  maps-service:
    build: ./backend/maps_service
    ports: [8004:8004]
    depends_on: [postgres]
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/maps
      OSRM_URL: http://osrm:5000

  media-service:
    build: ./backend/media_service
    ports: [8006:8006]
    depends_on: [minio, postgres]
    environment:
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin

  # Frontend (Vite dev server)
  frontend:
    build: ./frontend/app
    ports: [5173:5173]
    volumes:
      - ./frontend/app/src:/app/src
    command: npm run dev
```

### Переменные окружения (`.env`)

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# NATS
NATS_URL=nats://nats:4222

# MinIO S3
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=shoulder-to-shoulder

# OSRM
OSRM_URL=http://osrm:5000

# API
API_PORT=8000
FRONTEND_URL=http://localhost:5173
```

### Развертывание

```bash
# Запуск production
docker-compose -f docker-compose.yml up -d --build

# Logs
docker-compose logs -f [service-name]

# Остановка
docker-compose down
```

---

## 📊 Ключевые метрики & KPI

| Метрика | Описание | Источник |
|:---|:---|:---|
| **User Engagement** | | |
| DAU | Daily Active Users | User Service logs |
| Event Creation Rate | События/день | Event Service |
| Join Rate | Средний процент вступлений | Event Service |
| **Rating System** | | |
| Avg Empathy Score | Средний рейтинг эмпатии | User Service |
| Reliability Score | Показатель надежности | User Service |
| Badge Distribution | Распределение достижений | User Service |
| **Map Coverage** | | |
| Total Places | Убежденные спортплощадки | Maps Service |
| UGC Places | Места от пользователей | Maps Service |
| Routes Built | Построено маршрутов | Maps Service |
| **System Health** | | |
| API Response Time | Среднее время ответа | Logs/Monitoring |
| Error Rate | % failed requests | Logs/Monitoring |
| Uptime | Доступность сервисов | Monitoring |

---

## 🔐 Безопасность

### Authentication
- JWT токены с TTL 24 часа
- Refresh tokens для долгосрочных сессий
- Хеширование паролей (bcrypt)

### Authorization
- Role-based access control (RBAC)
- User, Admin, Moderator roles
- Проверка прав перед каждым запросом

### Data Protection
- HTTPS в production
- CORS настроен на фронтенд URL
- SQL injection protection (ORM)
- Rate limiting на API endpoints

### User Privacy
- Анонимные встречи (опция)
- Скрытие контактных данных
- GDPR compliance (удаление данных)
- Шифрование sensitive данных

---

## 🤝 Контрибьютинг

Проект open-source. Очень ценим вклад от комьюнити!

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/shoulder-to-shoulder.git
cd shoulder-to-shoulder

# Установка зависимостей
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Docker setup
docker-compose -f docker-compose.dev.yml up -d --build

# Frontend
cd frontend/app
npm install
npm run dev
```
---

**Версия документации:** 1.0  
**Последнее обновление:** Июнь 2026  
**Статус:** Prototype 🚀

# 📡 API для микросервиса карт

**Base URL:** `http://localhost:3000/api/v1`

Все ответы в формате JSON. При ошибке — HTTP-статус + `{ "error": "описание" }`.

---

## 🔀 Эндпоинты

### 1. Все места (карта)

```
GET /places
```

**Query-параметры (фильтры, все опциональны):**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `activity_type` | `string` | Тип: `running`, `strength`, `yoga`, `calisthenics` |
| `noise_level` | `string` | Шум: `quiet`, `moderate`, `loud` |
| `lit` | `boolean` | Только освещённые |
| `lockers` | `boolean` | Только с раздевалками |
| `benches` | `boolean` | Только со скамейками |

**Ответ `200 OK`:**
```json
{
  "places": [
    {
      "id": 1,
      "name": "Парк Победы",
      "description": "Отличное место для утренних пробежек.",
      "lat": 52.9690,
      "lng": 36.0820,
      "rating": 4.7,
      "emoji": "🏃",
      "category": "park",
      "activityType": "running",
      "noiseLevel": "moderate",
      "lit": true,
      "lockers": false,
      "benches": true,
      "address": "ул. Комсомольская, Орёл",
      "image": "https://...",
      "gallery": ["https://...", "https://...", "https://..."]
    }
  ]
}
```

---

### 2. Одно место

```
GET /places/{id}
```

**Ответ `200 OK`:** — объект Place (как выше)

**`404 Not Found`:** `{ "error": "Место не найдено" }`

---

### 3. Маршрут (прокси OSRM)

```
GET /route?start_lat=52.9651&start_lng=36.0785&end_lat=52.9690&end_lng=36.0820
```

**Ответ `200 OK`:**
```json
{
  "distance": 1250,
  "duration": 900,
  "geometry": { "type": "LineString", "coordinates": [[36.0785, 52.9651], ...] },
  "steps": [
    { "instruction": "Идите на север", "distance": 200, "duration": 150 }
  ]
}
```

---

### 4. Ближайшие места

```
GET /places/nearby?lat=52.9651&lng=36.0785&radius=2000
```

**Ответ `200 OK`:** — массив Place с полем `distance`, отсортированный по возрастанию.

---

### 5. Мои мероприятия (MainPage)

```
GET /meetups/my
```

**Ответ `200 OK`:**
```json
{
  "meetups": [
    {
      "id": 1,
      "name": "Вечернее кардио",
      "time": "19:00",
      "locationShort": "Парк",
      "location": "Парк Победы, ул. Комсомольская",
      "level": "Новичок",
      "description": "Лёгкое кардио.",
      "type": "Бег",
      "quietCompanion": false,
      "participants": 3,
      "maxParticipants": 5,
      "isJoined": true,
      "avatars": ["https://..."],
      "moreCount": 2
    }
  ]
}
```

---

### 6. Записаться на мероприятие (MainPage)

```
POST /meetups/{id}/join
```

**Тело:** `{ "user_id": 1 }`

**Ответ `200 OK`:** `{ "success": true, "participants": 4, "maxParticipants": 5 }`

**`400`:** `{ "error": "Нет свободных мест" }`
**`409`:** `{ "error": "Вы уже записаны" }`

---

### 7. Отписаться от мероприятия (MainPage)

```
DELETE /meetups/{id}/leave?user_id=1
```

**Ответ `200 OK`:** `{ "success": true, "participants": 3, "maxParticipants": 5 }`

**`404`:** `{ "error": "Вы не записаны" }`

---

### 8. Все мероприятия (вкладка Ивенты)

```
GET /events
```

**Ответ `200 OK`:**
```json
{
  "events": [
    {
      "id": 1,
      "name": "Утренняя пробежка",
      "emoji": "🏃",
      "date": "Сегодня",
      "time": "07:00",
      "locationShort": "Парк Победы",
      "location": "Парк Победы, ул. Комсомольская",
      "description": "Лёгкий бег.",
      "level": "Новичок",
      "type": "running",
      "quietCompanion": false,
      "participants": 5,
      "maxParticipants": 10,
      "isJoined": false,
      "avatars": ["https://..."],
      "moreCount": 3
    }
  ]
}
```

---

### 9. Создать мероприятие

```
POST /events
```

**Тело:**
```json
{
  "name": "Вечерняя пробежка",
  "date": "2026-04-10",
  "time": "19:00",
  "locationId": 1,
  "locationShort": "Парк Победы",
  "location": "Парк Победы, ул. Комсомольская",
  "level": "Новичок",
  "type": "running",
  "quietCompanion": false,
  "description": "",
  "maxParticipants": 10,
  "user_id": 1
}
```

**Ответ `201 Created`:** `{ "event": { ... } }`

---

### 10. Записаться на мероприятие (Ивенты)

```
POST /events/{id}/join
```

**Тело:** `{ "user_id": 1 }`

**Ответ `200 OK`:** `{ "success": true, "participants": 6, "maxParticipants": 10 }`

---

### 11. Отписаться от мероприятия (Ивенты)

```
DELETE /events/{id}/leave?user_id=1
```

**Ответ `200 OK`:** `{ "success": true, "participants": 5, "maxParticipants": 10 }`

---

## 📋 Сводная таблица

| # | Метод | Эндпоинт | Статус |
|---|-------|----------|--------|
| 1 | `GET` | `/places` | ✅ Нужно |
| 1b | `GET` | `/places?filters` | ✅ Нужно |
| 2 | `GET` | `/places/{id}` | ⏳ Опционально |
| 3 | `GET` | `/route` | ⏳ Опционально |
| 4 | `GET` | `/places/nearby` | ⏳ Опционально |
| 5 | `GET` | `/meetups/my` | ✅ Нужно |
| 6 | `POST` | `/meetups/{id}/join` | ✅ Нужно |
| 7 | `DELETE` | `/meetups/{id}/leave` | ✅ Нужно |
| 8 | `GET` | `/events` | ✅ Нужно |
| 9 | `POST` | `/events` | ✅ Нужно |
| 10 | `POST` | `/events/{id}/join` | ✅ Нужно |
| 11 | `DELETE` | `/events/{id}/leave` | ✅ Нужно |

---

## 💡 Минимальный старт

Реализовать **5 эндпоинтов**:

| # | Эндпоинт | Зачем |
|---|----------|-------|
| 1 | `GET /places` | Карта с маркерами |
| 5 | `GET /meetups/my` | Карточки на главной |
| 6 | `POST /meetups/{id}/join` | Записаться с главной |
| 7 | `DELETE /meetups/{id}/leave` | Отписаться с главной |
| 8 | `GET /events` | Вкладка Ивенты |

Остальное — по мере развития.

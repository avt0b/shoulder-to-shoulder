# 📡 API для микросервиса карт

**Base URL:** `http://localhost:3000/api/v1`

Все ответы в формате JSON. При ошибке — HTTP-статус + `{ "error": "описание" }`.

---

## 1. Получить все места

```
GET /places
```

**Запрос:** без тела

**Ответ `200 OK`:**
```json
{
  "places": [
    {
      "id": 1,
      "name": "Парк Победы",
      "description": "Отличное место для утренних пробежек и групповых тренировок. Ровные дорожки, скамейки.",
      "lat": 52.9690,
      "lng": 36.0820,
      "rating": 4.7,
      "emoji": "🏃",
      "category": "park",
      "address": "ул. Комсомольская, Орёл",
      "image": "https://...",
      "gallery": [
        "https://...",
        "https://...",
        "https://..."
      ]
    }
  ]
}
```

---

## 2. Получить одно место

```
GET /places/{id}
```

**Запрос:** `id` в пути

**Ответ `200 OK`:**
```json
{
  "place": {
    "id": 1,
    "name": "Парк Победы",
    "description": "Отличное место...",
    "lat": 52.9690,
    "lng": 36.0820,
    "rating": 4.7,
    "emoji": "🏃",
    "category": "park",
    "address": "ул. Комсомольская, Орёл",
    "image": "https://...",
    "gallery": ["https://...", "https://...", "https://..."]
  }
}
```

**Ответ `404 Not Found`:**
```json
{
  "error": "Место не найдено"
}
```

---

## 3. Построить маршрут

```
GET /route?start_lat=52.9651&start_lng=36.0785&end_lat=52.9690&end_lng=36.0820
```

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `start_lat` | `number` | Широта точки старта |
| `start_lng` | `number` | Долгота точки старта |
| `end_lat` | `number` | Широта точки назначения |
| `end_lng` | `number` | Долгота точки назначения |

**Ответ `200 OK`:**
```json
{
  "distance": 1250,
  "duration": 900,
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [36.0785, 52.9651],
      [36.0790, 52.9655],
      [36.0820, 52.9690]
    ]
  },
  "steps": [
    {
      "instruction": "Идите на север по ул. Ленина",
      "distance": 200,
      "duration": 150
    },
    {
      "instruction": "Поверните направо на ул. Комсомольская",
      "distance": 1050,
      "duration": 750
    }
  ]
}
```

> **Примечание:** можно проксировать OSRM: `https://router.project-osrm.org/route/v1/foot/{lng1},{lat1};{lng2},{lat2}?steps=true&geometries=geojson&overview=full`

**Ответ `400 Bad Request`** (не удалось построить маршрут):
```json
{
  "error": "Не удалось построить маршрут"
}
```

---

## 4. Ближайшие места

```
GET /places/nearby?lat=52.9651&lng=36.0785&radius=2000
```

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `lat` | `number` | Широта текущей позиции |
| `lng` | `number` | Долгота текущей позиции |
| `radius` | `number` | Радиус поиска в метрах (по умолчанию 2000) |

**Ответ `200 OK`:**
```json
{
  "places": [
    {
      "id": 1,
      "name": "Парк Победы",
      "description": "...",
      "lat": 52.9690,
      "lng": 36.0820,
      "rating": 4.7,
      "emoji": "🏃",
      "category": "park",
      "address": "ул. Комсомольская, Орёл",
      "image": "https://...",
      "gallery": ["https://...", "https://...", "https://..."],
      "distance": 450
    }
  ]
}
```

> Массив отсортирован по возрастанию `distance` (расстояние в метрах от точки запроса).

---

## 5. Мои мероприятия

```
GET /meetups/my
```

**Запрос:** без тела (позже добавить авторизацию)

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
      "participants": 3,
      "maxParticipants": 5,
      "isJoined": true,
      "avatars": [
        "https://...",
        "https://..."
      ],
      "moreCount": 2
    },
    {
      "id": 2,
      "name": "Основы калистеники",
      "time": "20:30",
      "locationShort": "Уличная арена",
      "location": "Стадион «Центральный»",
      "level": "Открыто",
      "participants": 1,
      "maxParticipants": 8,
      "isJoined": false,
      "avatars": [
        "https://..."
      ],
      "moreCount": 4
    }
  ]
}
```

> Сейчас `user_id` не передаётся — можно захардкодить `user_id = 1` для теста. Позже добавим JWT-токен.

---

## 6. Записаться на мероприятие

```
POST /meetups/{id}/join
```

**Тело запроса:**
```json
{
  "user_id": 1
}
```

**Ответ `200 OK`:**
```json
{
  "success": true,
  "participants": 4,
  "maxParticipants": 5
}
```

**Ответ `400 Bad Request`** (мест нет):
```json
{
  "error": "Нет свободных мест"
}
```

**Ответ `409 Conflict`** (уже записан):
```json
{
  "error": "Вы уже записаны на это мероприятие"
}
```

---

## 7. Отписаться от мероприятия

```
DELETE /meetups/{id}/leave?user_id=1
```

**Запрос:** `user_id` в query-параметре, `id` в пути

**Ответ `200 OK`:**
```json
{
  "success": true,
  "participants": 3,
  "maxParticipants": 5
}
```

**Ответ `404 Not Found`:**
```json
{
  "error": "Вы не записаны на это мероприятие"
}
```

---

## 📋 Краткая сводка

| # | Метод | Эндпоинт | Что делает |
|---|-------|----------|------------|
| 1 | `GET` | `/places` | Все места для карты |
| 2 | `GET` | `/places/{id}` | Одно место |
| 3 | `GET` | `/route` | Маршрут (прокси OSRM) |
| 4 | `GET` | `/places/nearby` | Ближайшие места |
| 5 | `GET` | `/meetups/my` | Мои мероприятия |
| 6 | `POST` | `/meetups/{id}/join` | Записаться |
| 7 | `DELETE` | `/meetups/{id}/leave` | Отписаться |

## 💡 Минимальный старт

Для начала достаточно реализовать **эндпоинты 1 и 5**:
- `GET /places` — верни 2-3 места с координатами Орла
- `GET /meetups/my` — верни 2 заглушки-мероприятия

Остальное добавим по мере развития.

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
      "activityType": "running",
      "noiseLevel": "moderate",
      "lit": true,
      "lockers": false,
      "benches": true,
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

**Поля объекта Place:**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `number` | Уникальный ID |
| `name` | `string` | Название места |
| `description` | `string` | Краткое описание |
| `lat` | `number` | Широта (координаты) |
| `lng` | `number` | Долгота (координаты) |
| `rating` | `number` | Рейтинг (0-5) |
| `emoji` | `string` | Эмодзи-иконка (🏃🏋️🧘💪) |
| `category` | `string` | Категория: `park`, `stadium`, `river`, `playground` |
| `activityType` | `string` | Тип активности: `running`, `strength`, `yoga`, `calisthenics` |
| `noiseLevel` | `string` | Уровень шума: `quiet`, `moderate`, `loud` |
| `lit` | `boolean` | Освещённая территория |
| `lockers` | `boolean` | Есть раздевалки |
| `benches` | `boolean` | Есть скамейки |
| `address` | `string` | Адрес |
| `image` | `string` | URL главного изображения |
| `gallery` | `string[]` | Массив URL фотографий (3 шт) |

---

## 1b. Фильтрация мест

```
GET /places?activity_type=running&noise_level=quiet&lit=true&lockers=true&benches=true
```

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `activity_type` | `string` | Фильтр по типу: `running`, `strength`, `yoga`, `calisthenics` |
| `noise_level` | `string` | Фильтр по шуму: `quiet`, `moderate`, `loud` |
| `lit` | `boolean` | Только освещённые (`true`) |
| `lockers` | `boolean` | Только с раздевалками (`true`) |
| `benches` | `boolean` | Только со скамейками (`true`) |

> Все параметры опциональны. Если не переданы — возвращаются все места.
> Фильтры комбинируются (AND).

**Ответ `200 OK`:**
```json
{
  "places": [
    {
      "id": 3,
      "name": "Набережная Оки",
      "description": "Живописный маршрут вдоль реки...",
      "lat": 52.9670,
      "lng": 36.0680,
      "rating": 4.8,
      "emoji": "🧘",
      "category": "river",
      "activityType": "yoga",
      "noiseLevel": "quiet",
      "lit": false,
      "lockers": false,
      "benches": true,
      "address": "Набережная Оки, Орёл",
      "image": "https://...",
      "gallery": ["https://...", "https://...", "https://..."]
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
      "description": "Лёгкое кардио для разогрева.",
      "type": "Бег",
      "quietCompanion": false,
      "participants": 3,
      "maxParticipants": 5,
      "isJoined": true,
      "avatars": [
        "https://...",
        "https://..."
      ],
      "moreCount": 2
    }
  ]
}
```

> Сейчас `user_id` не передаётся — можно захардкодить `user_id = 1` для теста. Позже добавим JWT-токен.

---

## 5b. Все встречи (для вкладки «Все встречи»)

```
GET /meetups
```

**Запрос:** без тела

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
      "description": "Лёгкое кардио для разогрева.",
      "type": "Бег",
      "quietCompanion": false,
      "participants": 3,
      "maxParticipants": 5,
      "isJoined": true,
      "avatars": ["https://..."],
      "moreCount": 2
    },
    {
      "id": 2,
      "name": "Основы калистеники",
      "time": "20:30",
      "locationShort": "Уличная арена",
      "location": "Стадион «Центральный»",
      "level": "Открыто",
      "description": "Изучаем базовые элементы.",
      "type": "Гимнастика",
      "quietCompanion": false,
      "participants": 1,
      "maxParticipants": 8,
      "isJoined": false,
      "avatars": ["https://..."],
      "moreCount": 4
    }
  ]
}
```

**Поля объекта Meetup:**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `number` | Уникальный ID |
| `name` | `string` | Название мероприятия |
| `time` | `string` | Время (например `19:00`) |
| `locationShort` | `string` | Краткое место для карточки |
| `location` | `string` | Полное место |
| `level` | `string` | Уровень: `Новичок`, `Средний`, `Продвинутый`, `Открыто` |
| `description` | `string` | Описание мероприятия |
| `type` | `string` | Тип: `Бег`, `Пауэрлифтинг`, `Растяжка`, `Гимнастика` |
| `quietCompanion` | `boolean` | Пометка «Тихий компаньон» |
| `participants` | `number` | Сколько уже записано |
| `maxParticipants` | `number` | Максимум участников |
| `isJoined` | `boolean` | Записан ли текущий пользователь |
| `avatars` | `string[]` | URL аватарок участников (до 3) |
| `moreCount` | `number` | Сколько ещё участников (показать как `+N`) |

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

## 8. Все мероприятия (Ивенты)

```
GET /events
```

**Запрос:** без тела

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
      "description": "Лёгкий бег трусцой по парку. Темп разговорный.",
      "level": "Новичок",
      "type": "Пробежка",
      "participants": 5,
      "maxParticipants": 10,
      "isJoined": false,
      "avatars": [
        "https://...",
        "https://..."
      ],
      "moreCount": 3
    }
  ]
}
```

**Поля объекта Event:**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `number` | Уникальный ID |
| `name` | `string` | Название мероприятия |
| `emoji` | `string` | Эмодзи-иконка (🏃💪🧘🔥🤸) |
| `date` | `string` | Дата (например `Сегодня`, `Завтра`, `2026-04-10`) |
| `time` | `string` | Время (например `07:00`) |
| `locationShort` | `string` | Краткое название места |
| `location` | `string` | Полное описание места |
| `description` | `string` | Описание мероприятия |
| `level` | `string` | Уровень: `Новичок`, `Средний`, `Продвинутый`, `Открыто для всех` |
| `type` | `string` | Тип: `Тренировка`, `Пробежка`, `Йога`, `Растяжка` |
| `participants` | `number` | Сколько уже записано |
| `maxParticipants` | `number` | Максимум участников |
| `isJoined` | `boolean` | Записан ли текущий пользователь |
| `avatars` | `string[]` | URL аватарок участников (до 3) |
| `moreCount` | `number` | Сколько ещё участников (показать как `+N`) |

---

## 9. Получить одно мероприятие

```
GET /events/{id}
```

**Запрос:** `id` в пути

**Ответ `200 OK`:**
```json
{
  "event": {
    "id": 1,
    "name": "Утренняя пробежка",
    "emoji": "🏃",
    "date": "Сегодня",
    "time": "07:00",
    "locationShort": "Парк Победы",
    "location": "Парк Победы, ул. Комсомольская",
    "description": "Лёгкий бег трусцой по парку.",
    "level": "Новичок",
    "type": "Пробежка",
    "participants": 5,
    "maxParticipants": 10,
    "isJoined": false,
    "avatars": ["https://...", "https://..."],
    "moreCount": 3
  }
}
```

**Ответ `404 Not Found`:**
```json
{
  "error": "Мероприятие не найдено"
}
```

---

## 10. Создать мероприятие

```
POST /events
```

**Тело запроса:**
```json
{
  "name": "Вечерняя пробежка",
  "date": "2026-04-10",
  "time": "19:00",
  "locationId": 1,
  "locationShort": "Парк Победы",
  "location": "Парк Победы, ул. Комсомольская",
  "level": "Новичок",
  "description": "Бег трусцой после работы",
  "maxParticipants": 10,
  "user_id": 1
}
```

**Ответ `201 Created`:**
```json
{
  "event": {
    "id": 6,
    "name": "Вечерняя пробежка",
    "emoji": "🏃",
    "date": "2026-04-10",
    "time": "19:00",
    "locationShort": "Парк Победы",
    "location": "Парк Победы, ул. Комсомольская",
    "description": "Бег трусцой после работы",
    "level": "Новичок",
    "type": "Пробежка",
    "participants": 1,
    "maxParticipants": 10,
    "isJoined": true,
    "avatars": ["https://..."],
    "moreCount": 0
  }
}
```

---

## 11. Записаться на мероприятие

```
POST /events/{id}/join
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
  "participants": 6,
  "maxParticipants": 10
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

## 12. Отписаться от мероприятия

```
DELETE /events/{id}/leave?user_id=1
```

**Запрос:** `user_id` в query-параметре, `id` в пути

**Ответ `200 OK`:**
```json
{
  "success": true,
  "participants": 5,
  "maxParticipants": 10
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
| 5 | `GET` | `/meetups/my` | Мои мероприятия (главная) |
| 6 | `POST` | `/meetups/{id}/join` | Записаться (главная) |
| 7 | `DELETE` | `/meetups/{id}/leave` | Отписаться (главная) |
| 8 | `GET` | `/events` | Все мероприятия (вкладка Ивенты) |
| 9 | `GET` | `/events/{id}` | Одно мероприятие |
| 10 | `POST` | `/events` | Создать мероприятие |
| 11 | `POST` | `/events/{id}/join` | Записаться (Ивенты) |
| 12 | `DELETE` | `/events/{id}/leave` | Отписаться (Ивенты) |

## 💡 Минимальный старт

Для начала достаточно реализовать **эндпоинты 1, 5 и 8**:
- `GET /places` — верни 2-3 места с координатами Орла
- `GET /meetups/my` — верни 2 заглушки-мероприятия (главная страница)
- `GET /events` — верни 3-5 заглушек-мероприятий (вкладка Ивенты)

Остальное добавим по мере развития.

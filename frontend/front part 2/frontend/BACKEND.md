# 🛠 Backend Developer Guide

## О проекте

Мобильное приложение на **Vue 3 + Leaflet** для поиска спортивных мест и групповых тренировок в городе Орёл.

Фронтенд уже имеет **mock-данные** и fallback на `localStorage`. Бэкенд нужен для замены заглушек реальными данными.

---

## 📁 Структура фронтенда

```
app/
├── src/
│   ├── components/
│   │   ├── MainPage.vue    # Главная: мини-карта + мои встречи + создание
│   │   ├── MapLight.vue    # Полноэкранная карта + фильтры мест
│   │   └── EventsPage.vue  # Вкладка «Ивенты»: все встречи + создание
│   ├── App.vue             # Роутинг: MainPage ↔ EventsPage ↔ MapLight
│   ├── config.js           # API URL, OSRM URL, debug-флаги
│   ├── style.css           # Глобальные CSS-переменные (Material Design)
│   └── main.js
└── package.json
```

---

## 🔌 API Endpoints

Полная документация — **[API.md](API.md)**. Ниже — обзор для бэкендера.

### Места (Places)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/places` | Все места (с опциональными фильтрами) |
| `GET` | `/places/{id}` | Одно место |
| `GET` | `/places/nearby` | Ближайшие места по координатам |

**Фильтры для `/places`:**
- `activity_type` — `running`, `strength`, `yoga`, `calisthenics`
- `noise_level` — `quiet`, `moderate`, `loud`
- `lit`, `lockers`, `benches` — boolean-флаги

**Поля Place:**
```typescript
{
  id: number
  name: string
  description: string
  lat: number        // широта
  lng: number        // долгота
  rating: number     // 0-5
  emoji: string      // 🏃🏋️🧘💪
  category: string   // park, stadium, river, playground
  activityType: string   // running, strength, yoga, calisthenics
  noiseLevel: string     // quiet, moderate, loud
  lit: boolean       // освещённая территория
  lockers: boolean   // есть раздевалки
  benches: boolean   // есть скамейки
  address: string
  image: string      // URL главного фото
  gallery: string[]  // 3 фото
}
```

---

### Мероприятия (Meetups) — MainPage

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/meetups/my` | Мои встречи (пользователь записан) |
| `POST` | `/meetups/{id}/join` | Записаться |
| `DELETE` | `/meetups/{id}/leave` | Отписаться |

**Поля Meetup:**
```typescript
{
  id: number
  name: string
  time: string           // "19:00"
  locationShort: string
  location: string
  level: string          // Новичок, Средний, Продвинутый, Открыто
  description: string
  type: string           // Бег, Пауэрлифтинг, Растяжка, Гимнастика
  quietCompanion: boolean
  participants: number
  maxParticipants: number
  isJoined: boolean
  avatars: string[]      // до 3 URL
  moreCount: number
}
```

---

### Ивенты (Events) — EventsPage

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/events` | Все встречи |
| `POST` | `/events` | Создать встречу |
| `POST` | `/events/{id}/join` | Записаться |
| `DELETE` | `/events/{id}/leave` | Отписаться |

**Поля Event:**
```typescript
{
  id: number
  name: string
  emoji: string           // 🏃🏋️🧘🔥🤸
  date: string            // "Сегодня", "Завтра", "2026-04-10"
  time: string            // "07:00"
  locationShort: string
  location: string
  description: string
  level: string           // Новичок, Средний, Профи, Открыто для всех
  type: string            // running, powerlifting, stretching, gymnastics
  quietCompanion: boolean
  participants: number
  maxParticipants: number
  isJoined: boolean
  avatars: string[]
  moreCount: number
}
```

**Тело POST /events:**
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

---

### Маршруты (OSRM)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/route` | Построить маршрут (прокси OSRM) |

Можно проксировать: `https://router.project-osrm.org/route/v1/foot/{lng1},{lat1};{lng2},{lat2}`

---

## 🔐 Авторизация

Сейчас `user_id` передаётся в теле (`user_id: 1`) или query-параметре.
Позже добавим JWT-токен. Пока можно захардкодить `user_id = 1`.

---

## 📱 Как фронтенд использует API

### Загрузка данных

```js
// MapLight.vue — места на карту
const res = await fetch('http://localhost:3000/api/v1/places')
const data = await res.json()
places.value = data.places
addPlaceMarkers()

// MainPage.vue — мои встречи
const res = await fetch('http://localhost:3000/api/v1/meetups/my')
myMeetups.value = (await res.json()).meetups

// EventsPage.vue — все встречи
const res = await fetch('http://localhost:3000/api/v1/events')
allEvents.value = (await res.json()).events
```

### Fallback

Если API недоступен — фронтенд использует:
1. `localStorage` (сохранённые данные)
2. Mock-данные (захардкоженные заглушки)

Это позволяет тестировать UI без бэкенда.

---

## 🗺 Координаты

**Центр Орла:** `[52.9651, 36.0785]`

**OSRM формат:** `[долгота, широта]` → `[lng, lat]`

---

## 💡 Рекомендации

1. **База данных** — PostgreSQL / SQLite / MongoDB — на ваш выбор
2. **Хранение фото** — URL-ссылки или загрузка на сервер
3. **Эмодзи** — хранить как строки
4. **Категории** — `park`, `stadium`, `river`, `playground` — можно расширять
5. **Типы активности** — `running`, `strength`, `yoga`, `calisthenics`

---

## 🚀 Запуск фронтенда

```bash
cd app
npm install
npm run dev
```

Сервер на `http://localhost:5173`

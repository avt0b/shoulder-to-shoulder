# Frontend API Requirements

Документ составлен по текущему фронтенду в `frontend/src`.

Базовый URL берется из переменной окружения:

```env
VITE_API_URL=http://localhost:8000
```

Все запросы отправляются с `Content-Type: application/json`.

Для приватных ручек фронтенд автоматически добавляет JWT:

```http
Authorization: Bearer <access_token>
```

При ответе `401` фронтенд удаляет токен и редиректит пользователя на `/login`.

## Краткий список ручек

| Метод | Ручка | Нужна авторизация | Где используется |
| --- | --- | --- | --- |
| `POST` | `/api/auth/login` | Нет | Страница логина |
| `GET` | `/api/team/me` | Да | Дашборд команды |
| `POST` | `/api/flags/submit` | Да | Форма отправки флага |
| `GET` | `/api/submissions` | Да | Последние попытки на дашборде |
| `GET` | `/api/scoreboard` | Да | Таблица лидеров, автообновление каждые 15 секунд |

## Общий формат ошибок

Фронтенду удобнее получать ошибки в таком формате:

```json
{
  "message": "Invalid credentials",
  "status": 401
}
```

Минимально важное поле: `message`.

Сейчас часть frontend-кода также допускает `detail`, но в UI в нескольких местах читается именно `message`, например при отправке флага:

```ts
err.response?.data?.message || 'Failed to submit flag'
```

Рекомендация: либо отдавать `message` на backend, либо на frontend добавить нормализацию `detail -> message`.

## `POST /api/auth/login`

Логин команды. После успешного ответа фронтенд сохраняет `access_token` в Zustand persist storage и переходит на `/dashboard`.

### Request

```json
{
  "team_name": "team_alpha",
  "password": "secret-password"
}
```

### Request fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `team_name` | `string` | Да | Название команды |
| `password` | `string` | Да | Пароль команды |

### Success response

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Response fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `access_token` | `string` | Да | JWT, который frontend будет отправлять в `Authorization` |
| `token_type` | `string` | Нет | Можно отдавать `bearer`; frontend сейчас использует только `access_token` |

### Ошибки

```json
{
  "message": "Invalid credentials",
  "status": 401
}
```

Ожидаемые статусы: `401`, `422`.

## `GET /api/team/me`

Возвращает данные текущей команды для верхней карточки на дашборде.

### Headers

```http
Authorization: Bearer <access_token>
```

### Success response

```json
{
  "id": "6c8a4ab2-d70b-4a59-88b0-2edc36e392e4",
  "name": "team_alpha",
  "score": 350,
  "rank": 4
}
```

### Response fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `id` | `string` | Да | UUID команды |
| `name` | `string` | Да | Название команды |
| `score` | `number` | Да | Текущие очки |
| `rank` | `number` | Да | Место команды в рейтинге |

### Ошибки

Ожидаемые статусы: `401`, `404`.

## `POST /api/flags/submit`

Отправка найденного флага.

После успешного ответа frontend показывает alert на 5 секунд и очищает поле ввода.

### Headers

```http
Authorization: Bearer <access_token>
```

### Request

```json
{
  "flag": "CTF{example_flag}"
}
```

### Request fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `flag` | `string` | Да | Текст флага |

### Success response: правильный флаг

```json
{
  "success": true,
  "message": "Correct flag",
  "points": 100
}
```

### Success response: неправильный флаг

```json
{
  "success": false,
  "message": "Wrong flag",
  "points": null
}
```

### Success response: уже решено

```json
{
  "success": false,
  "message": "Challenge already solved",
  "points": null
}
```

### Response fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `success` | `boolean` | Да | Определяет цвет alert на frontend |
| `message` | `string` | Да | Текст, который показывается пользователю |
| `points` | `number \| null` | Нет | Если значение есть и оно не `0`, frontend покажет `+N points` |

### Ошибки

Ожидаемые статусы: `401`, `422`.

Важно: для неправильного флага лучше возвращать `200` с `success: false`, чтобы frontend показал понятное сообщение как результат проверки, а не как сетевую ошибку.

## `GET /api/submissions`

История попыток текущей команды. Используется на дашборде в блоке `Recent Submissions`.

### Headers

```http
Authorization: Bearer <access_token>
```

### Success response

```json
[
  {
    "id": "b289cf6f-0927-4b85-b598-4d8048a49fd0",
    "flag": "CTF{example_flag}",
    "correct": true,
    "created_at": "2026-06-02T18:45:12.123456Z"
  },
  {
    "id": "087d9ddb-1c1f-4da9-9fb2-9e55857f1a03",
    "flag": "CTF{wrong}",
    "correct": false,
    "created_at": "2026-06-02T18:40:03.000000Z"
  }
]
```

### Response item fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `id` | `string` | Да | UUID попытки |
| `flag` | `string` | Да | Отправленный флаг, показывается в UI |
| `correct` | `boolean` | Да | Показывает бейдж `Correct` или `Wrong` |
| `created_at` | `string` | Да | ISO datetime, frontend парсит через `new Date(created_at)` |

### Ошибки

Ожидаемые статусы: `401`.

Рекомендация: отдавать последние попытки в порядке от новых к старым. Во frontend написано `Your last flag attempts`, отдельной сортировки там нет.

## `GET /api/scoreboard`

Таблица лидеров. Frontend автоматически обновляет запрос каждые 15 секунд.

### Headers

```http
Authorization: Bearer <access_token>
```

### Success response

```json
[
  {
    "rank": 1,
    "team_name": "team_alpha",
    "score": 900
  },
  {
    "rank": 2,
    "team_name": "team_beta",
    "score": 750
  }
]
```

### Response item fields

| Поле | Тип | Обязательное | Комментарий |
| --- | --- | --- | --- |
| `rank` | `number` | Да | Место команды |
| `team_name` | `string` | Да | Название команды |
| `score` | `number` | Да | Очки команды |

### Ошибки

Ожидаемые статусы: `401`.

Рекомендация: отдавать список уже отсортированным по месту/очкам. Во frontend отдельной сортировки нет.

## Что фронтенду пока не нужно

По текущему коду frontend не запрашивает:

- список задач/challenges;
- описание задачи;
- категории задач;
- регистрацию команды;
- logout-ручку;
- refresh token;
- профиль пользователя отдельно от команды;
- админские CRUD-ручки.

Если появится страница задач, понадобится отдельный контракт для списка challenges и статуса решенности.


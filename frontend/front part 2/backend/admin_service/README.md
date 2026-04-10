Для запуска:
Создать .env
Поменять в .env enviroment с develop на production
Если будем разворачивать тесты в докере, то на testing
Создать БД user_service_db
Закинуть туда db.sql
ОБЯЗАТЕЛЬНО запустить NATS

uv run uvicorn backend.admin_service.app.main:app --reload --port 8004

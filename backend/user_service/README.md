Ксюш, для тебя расписываю
Для запуска:
Создать .env
Поменять в .env enviroment с develop на production
Если будем разворачивать тесты в докере, то на testing
Создать БД user_service_db
Закинуть туда db.sql

Запуститься
uvicorn backend.user_service.app.main:app --host 0.0.0.0 --port 8000 --reload
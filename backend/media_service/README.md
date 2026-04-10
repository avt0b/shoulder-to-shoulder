
uv run uvicorn backend.media_service.app.main:app --port 8006
minio.exe server D:\data-for-minio --console-address ":9001" --license D:/minio.license
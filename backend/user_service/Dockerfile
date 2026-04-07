FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./pyproject.toml

RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -e .

COPY backend/user_service/app ./app

ENV PYTHONPATH=/app \
    ENVIRONMENT=development \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.user_service.app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]
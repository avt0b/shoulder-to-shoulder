FROM python:3.12-slim

WORKDIR /shoulder-to-shoulder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project dependencies
COPY pyproject.toml ./pyproject.toml

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi[standard] \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    alembic \
    asyncpg \
    psycopg2-binary \
    pydantic[email] \
    pydantic-settings \
    python-dotenv \
    python-jose[cryptography] \
    passlib[bcrypt] \
    bcrypt \
    nats-py \
    python-multipart \
    httpx \
    redis

# Create package structure for absolute imports
RUN mkdir -p /shoulder-to-shoulder/backend/user_service \
    && touch /shoulder-to-shoulder/backend/__init__.py \
    && ln -s /shoulder-to-shoulder/backend/user_service/app /shoulder-to-shoulder/app

# Copy application code
COPY . /shoulder-to-shoulder/backend/user_service

# Set environment variables
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/shoulder-to-shoulder

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.user_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

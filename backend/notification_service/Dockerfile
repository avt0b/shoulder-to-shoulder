FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project dependencies
COPY pyproject.toml .

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
    httpx \
    redis \
    APScheduler

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

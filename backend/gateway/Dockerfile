FROM python:3.12-slim

ARG APP_HOME=/shoulder-to-shoulder
ARG SERVICE_MODULE=backend.gateway.main:app
ARG SERVICE_PORT=8005
ARG UV_SYNC_EXTRA=

ENV APP_HOME=${APP_HOME} \
    SERVICE_MODULE=${SERVICE_MODULE} \
    SERVICE_PORT=${SERVICE_PORT} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=${APP_HOME} \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/shoulder-to-shoulder-venv \
    PATH=/opt/shoulder-to-shoulder-venv/bin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY backend ./backend
COPY main.py ./main.py

RUN if [ -n "${UV_SYNC_EXTRA}" ]; then pip install --no-cache-dir ${UV_SYNC_EXTRA}; fi

EXPOSE ${SERVICE_PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=5 \
    CMD curl -fsS "http://localhost:${SERVICE_PORT}/health" || exit 1

CMD ["sh", "-lc", "exec /opt/shoulder-to-shoulder-venv/bin/python -m uvicorn ${SERVICE_MODULE} --host 0.0.0.0 --port ${SERVICE_PORT}"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

RUN mkdir -p /app/uploads

CMD ["sh", "-c", "python -m uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]

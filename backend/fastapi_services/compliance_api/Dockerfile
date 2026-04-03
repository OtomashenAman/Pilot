FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first for layer caching
COPY backend/fastapi_services/compliance_api/requirements.txt /app/requirements.txt
RUN if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; \
    else pip install fastapi uvicorn[standard] celery psycopg[binary] redis sqlalchemy pydantic; fi

# Copy service code
COPY backend/fastapi_services/compliance_api /app

EXPOSE 8000

# Healthcheck assumes a /health endpoint exists; harmless if not used by compose
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "if [ -f app/main.py ]; then uvicorn app.main:app --host 0.0.0.0 --port 8000; elif [ -f main.py ]; then uvicorn main:app --host 0.0.0.0 --port 8000; else python -m http.server 8000; fi"]

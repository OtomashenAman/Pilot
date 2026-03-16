FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; else pip install fastapi uvicorn[standard]; fi

COPY . /app

EXPOSE 8001

# Expected app entrypoint: app.main:app
# Override with FASTAPI_APP_MODULE if needed.
ENV FASTAPI_APP_MODULE=app.main:app

CMD ["sh", "-c", "uvicorn ${FASTAPI_APP_MODULE} --host 0.0.0.0 --port 8001"]

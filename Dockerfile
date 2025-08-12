# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the entire backend directory (Django project)
COPY backend /app

# Environment defaults
ENV DJANGO_SETTINGS_MODULE=backend.settings \
    PORT=8000 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers 3 --threads 4 --timeout 60"

EXPOSE 8000

COPY --chmod=755 backend/build.sh /app/build.sh
COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application"]



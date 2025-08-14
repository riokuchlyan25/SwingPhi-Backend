# Docker Containerization Documentation

## Overview

This document provides comprehensive information about the Docker containerization setup for the Swing Phi Backend Django application. The project uses Docker for both development and production deployments, with support for PostgreSQL database integration.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Dockerfile Analysis](#dockerfile-analysis)
3. [Docker Compose Setup](#docker-compose-setup)
4. [Environment Configuration](#environment-configuration)
5. [Development Workflow](#development-workflow)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Architecture Overview

The Docker setup consists of two main services:
- **Web Service**: Django application running with Gunicorn
- **Database Service**: PostgreSQL database for data persistence

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │ Database Service│
│   (Django)      │◄──►│   (PostgreSQL)  │
│   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘
```

## Dockerfile Analysis

### Base Image
```dockerfile
FROM python:3.11-slim AS base
```
- Uses Python 3.11 slim image for smaller size
- Provides a good balance between features and image size

### Environment Variables
```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
```
- `PYTHONDONTWRITEBYTECODE=1`: Prevents Python from writing .pyc files
- `PYTHONUNBUFFERED=1`: Ensures Python output is sent straight to terminal
- `PIP_NO_CACHE_DIR=1`: Reduces image size by not caching pip packages

### System Dependencies
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```
- `build-essential`: Required for compiling Python packages
- `curl`: For health checks and debugging
- `libpq-dev`: PostgreSQL client library for psycopg2

### Application Setup
```dockerfile
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
COPY backend /app
```
- Sets working directory to `/app`
- Installs Python dependencies first (for better layer caching)
- Copies the entire backend directory

### Production Configuration
```dockerfile
ENV DJANGO_SETTINGS_MODULE=backend.settings \
    PORT=8000 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers 3 --threads 4 --timeout 60"
```
- Configures Django settings module
- Sets up Gunicorn with optimized parameters:
  - 3 workers for handling multiple requests
  - 4 threads per worker
  - 60-second timeout

## Docker Compose Setup

### Services Configuration

#### Web Service
```yaml
web:
  build:
    context: .
    dockerfile: Dockerfile
  env_file:
    - .env
  environment:
    - DJANGO_SETTINGS_MODULE=backend.settings
    - DEBUG=${DEBUG:-False}
  ports:
    - "8000:8000"
  depends_on:
    - db
  restart: unless-stopped
  volumes:
    - ./backend:/app
```

**Key Features:**
- Builds from local Dockerfile
- Uses `.env` file for environment variables
- Exposes port 8000
- Depends on database service
- Auto-restart policy
- Volume mount for development (hot reloading)

#### Database Service
```yaml
db:
  image: postgres:16-alpine
  environment:
    - POSTGRES_DB=${POSTGRES_DB:-app}
    - POSTGRES_USER=${POSTGRES_USER:-app}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-app}
  volumes:
    - pgdata:/var/lib/postgresql/data
  ports:
    - "5432:5432"
  restart: unless-stopped
```

**Key Features:**
- Uses PostgreSQL 16 Alpine (lightweight)
- Configurable database credentials via environment variables
- Persistent data storage with named volume
- Exposes port 5432 for external connections

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
POSTGRES_DB=swing_phi_db
POSTGRES_USER=swing_phi_user
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://swing_phi_user:your-secure-password@db:5432/swing_phi_db

# External API Keys (if needed)
OPENAI_API_KEY=your-openai-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
# Add other API keys as needed
```

### Environment Variable Priority
1. Docker Compose environment section
2. `.env` file
3. Default values in docker-compose.yml

## Development Workflow

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Backend
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services:**
   ```bash
   docker-compose up --build
   ```

### Development Commands

#### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up web
```

#### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db

# Follow logs
docker-compose logs -f web
```

#### Execute Commands in Container
```bash
# Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Database access
docker-compose exec db psql -U swing_phi_user -d swing_phi_db
```

#### Rebuild After Changes
```bash
# Rebuild specific service
docker-compose build web

# Rebuild and restart
docker-compose up --build web
```

## Production Deployment

### Render.com Deployment

The project includes a `render.yaml` file for automated deployment on Render.com:

```yaml
services:
  - type: web
    name: swing-phi-backend
    env: python
    plan: free
    buildCommand: ./build.sh
    startCommand: gunicorn wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: ".onrender.com,swingphi-backend.onrender.com"
      - key: DATABASE_URL
        fromDatabase:
          name: swing-phi-db
          property: connectionString
```

### Production Build Process

The `build.sh` script handles production setup:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### Production Considerations

1. **Security:**
   - Set `DEBUG=False` in production
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS` properly
   - Use environment variables for sensitive data

2. **Performance:**
   - Gunicorn workers: 3 (adjust based on CPU cores)
   - Threads per worker: 4
   - Timeout: 60 seconds

3. **Database:**
   - Use managed PostgreSQL service
   - Configure connection pooling
   - Set up regular backups

4. **Monitoring:**
   - Set up health checks
   - Configure logging
   - Monitor resource usage

## Entrypoint Script

The `docker/entrypoint.sh` script handles container initialization:

### Key Functions:
1. **Database Health Check:** Waits for PostgreSQL to be ready
2. **Migrations:** Runs Django migrations automatically
3. **Static Files:** Collects static files for production

### Health Check Logic:
```bash
# Waits up to 60 seconds for database
for i in range(60):
    try:
        db_conn.cursor()
        print('Database ready')
        sys.exit(0)
    except OperationalError:
        print('Database unavailable, waiting...')
        time.sleep(1)
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec web python manage.py dbshell
```

#### 2. Port Conflicts
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :5432

# Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Map host port 8001 to container port 8000
```

#### 3. Permission Issues
```bash
# Fix file permissions
chmod +x docker/entrypoint.sh
chmod +x backend/build.sh
```

#### 4. Build Failures
```bash
# Clean build cache
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all
docker system prune -a
```

#### 5. Memory Issues
```bash
# Check container resource usage
docker stats

# Increase Docker memory limit in Docker Desktop
```

### Debugging Commands

```bash
# Inspect running containers
docker-compose ps

# Execute shell in container
docker-compose exec web bash

# View container details
docker inspect <container-id>

# Check container logs
docker logs <container-id>
```

## Best Practices

### 1. Image Optimization
- Use multi-stage builds for smaller images
- Remove unnecessary files and cache
- Use `.dockerignore` to exclude files

### 2. Security
- Run containers as non-root user
- Use specific image tags (not `latest`)
- Scan images for vulnerabilities
- Keep base images updated

### 3. Development
- Use volume mounts for code changes
- Implement health checks
- Use environment-specific configurations
- Document all environment variables

### 4. Production
- Use production-ready database
- Implement proper logging
- Set up monitoring and alerting
- Use secrets management
- Implement backup strategies

### 5. Performance
- Optimize Dockerfile layers
- Use appropriate base images
- Configure resource limits
- Implement caching strategies

## File Structure

```
Backend/
├── Dockerfile                 # Main container definition
├── docker-compose.yml         # Multi-service orchestration
├── docker/
│   └── entrypoint.sh         # Container initialization script
├── backend/
│   ├── build.sh              # Production build script
│   ├── requirements.txt      # Python dependencies
│   └── ...                   # Django application files
├── render.yaml               # Render.com deployment config
└── .env                      # Environment variables (create this)
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

---

**Note:** This documentation should be updated whenever the Docker configuration changes. Always test changes in a development environment before applying to production.

# 🐳 Docker Deployment Guide

Complete guide for deploying Narrative OS using Docker and Docker Compose.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development Mode](#development-mode)
- [Production Deployment](#production-deployment)
- [Database Management](#database-management)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

---

## Prerequisites

### Required Software

- **Docker:** Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose:** Version 2.0+ (included with Docker Desktop)
- **Git:** For cloning the repository

### System Requirements

**Minimum:**
- 4GB RAM
- 2 CPU cores
- 10GB disk space

**Recommended:**
- 8GB RAM
- 4 CPU cores
- 20GB disk space

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Narrative_OS.git
cd Narrative_OS
```

### 2. Environment Setup

Create `.env` file in the root directory:

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Required environment variables:**

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Environment
ENVIRONMENT=production

# AI APIs (optional but recommended)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database (uses defaults from docker-compose.yml)
DATABASE_URL=postgresql://narrative:narrative@postgres:5432/narrative_os
REDIS_URL=redis://redis:6379/0
```

### 3. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# (Optional) Create admin user
docker-compose exec backend python -m scripts.create_admin
```

### 5. Access Applications

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001 (minioadmin/minioadmin)
- **PostgreSQL:** localhost:5432 (narrative/narrative)

---

## Architecture

### Services Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Narrative OS Stack                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │  Frontend    │────────▶│  Backend     │            │
│  │  Next.js     │         │  FastAPI     │            │
│  │  Port: 3000  │         │  Port: 8000  │            │
│  └──────────────┘         └──────┬───────┘            │
│                                   │                     │
│         ┌────────────────────────┼────────────┐       │
│         │                        │            │       │
│  ┌──────▼──────┐    ┌───────────▼──┐  ┌──────▼─────┐│
│  │ PostgreSQL  │    │    Redis     │  │   MinIO    ││
│  │ + pgvector  │    │   Cache/     │  │  Storage   ││
│  │ Port: 5432  │    │   Queue      │  │  Port:     ││
│  └─────────────┘    │ Port: 6379   │  │  9000/9001 ││
│                     └──────────────┘  └────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Container Details

| Service | Image | Purpose | Ports |
|---------|-------|---------|-------|
| **frontend** | Custom (Node 20) | Next.js UI | 3000 |
| **backend** | Custom (Python 3.11) | FastAPI REST API | 8000 |
| **postgres** | ankane/pgvector | Database with vector search | 5432 |
| **redis** | redis:7-alpine | Caching & task queue | 6379 |
| **minio** | minio/minio | S3-compatible storage | 9000, 9001 |

### Networking

All services are connected via the `narrative_network` bridge network, allowing:
- Internal service discovery by container name
- Isolated communication
- External access via exposed ports

---

## Configuration

### Docker Compose Environment Variables

The `docker-compose.yml` file uses environment variables with defaults:

```yaml
environment:
  SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
  OPENAI_API_KEY: ${OPENAI_API_KEY:-}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
```

**Syntax:** `${VAR_NAME:-default_value}`

### Backend Environment Variables

**Database:**
```bash
DATABASE_URL=postgresql://user:pass@host:port/database
```

**Redis:**
```bash
REDIS_URL=redis://host:port/db
```

**S3/MinIO:**
```bash
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=narrative-storage
```

**AI APIs:**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**CORS:**
```bash
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

### Frontend Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

---

## Development Mode

### Run with Hot Reload

For development, you can mount local directories as volumes for hot reloading:

**Create `docker-compose.dev.yml`:**

```yaml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      target: deps  # Use deps stage only
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev
    environment:
      NODE_ENV: development
```

**Start development stack:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Running Tests in Docker

**Backend tests:**

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=backend --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_orchestration_service.py
```

**Frontend tests:**

```bash
# Run all tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm run test:coverage
```

---

## Production Deployment

### Security Checklist

✅ **Before deploying to production:**

1. **Change default passwords:**
   - PostgreSQL: Update `POSTGRES_PASSWORD`
   - MinIO: Update `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`

2. **Set strong SECRET_KEY:**
   ```bash
   # Generate a secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Configure CORS properly:**
   - Update `CORS_ORIGINS` with your production domain
   - Remove `http://localhost:3000`

4. **Enable HTTPS:**
   - Use reverse proxy (Nginx, Traefik, Caddy)
   - Configure SSL certificates (Let's Encrypt)

5. **Restrict ports:**
   - Don't expose database ports publicly
   - Use internal networking for service communication

### Production docker-compose.prod.yml

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      ENVIRONMENT: production
      SECRET_KEY: ${SECRET_KEY}  # Required in .env
    # Don't mount volumes in production

  frontend:
    restart: always
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
      NODE_ENV: production

  postgres:
    restart: always
    # Don't expose port 5432 externally
    ports: []  # Remove external access

  redis:
    restart: always
    ports: []  # Remove external access

  minio:
    restart: always
    # Only expose console via reverse proxy
```

### Deploy to Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Using Reverse Proxy (Nginx Example)

```nginx
# /etc/nginx/sites-available/narrative-os

upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Database Management

### Backups

**Manual backup:**

```bash
# Backup database
docker-compose exec postgres pg_dump -U narrative narrative_os > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql
```

**Automated backups with cron:**

```bash
# Add to crontab
0 2 * * * cd /path/to/Narrative_OS && docker-compose exec -T postgres pg_dump -U narrative narrative_os | gzip > /backups/narrative_$(date +\%Y\%m\%d).sql.gz
```

### Restore Database

```bash
# Stop backend to prevent connections
docker-compose stop backend

# Drop and recreate database
docker-compose exec postgres psql -U narrative -c "DROP DATABASE narrative_os;"
docker-compose exec postgres psql -U narrative -c "CREATE DATABASE narrative_os;"

# Restore from backup
gunzip -c backup_20260110.sql.gz | docker-compose exec -T postgres psql -U narrative narrative_os

# Restart backend
docker-compose start backend
```

### Run Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Rollback last migration
docker-compose exec backend alembic downgrade -1

# Check current migration version
docker-compose exec backend alembic current

# Create new migration (after model changes)
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since 2026-01-10T10:00:00 backend
```

### Container Status

```bash
# Check running containers
docker-compose ps

# Resource usage
docker stats

# Health checks
docker-compose ps
```

### Monitoring Endpoints

**Backend health:**
```bash
curl http://localhost:8000/health
```

**Database connection:**
```bash
docker-compose exec postgres pg_isready -U narrative
```

**Redis connection:**
```bash
docker-compose exec redis redis-cli ping
```

---

## Troubleshooting

### Common Issues

#### 1. **Port Already in Use**

**Error:** `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Map to different external port
```

#### 2. **Backend Can't Connect to Database**

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Check postgres is healthy
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Wait for health check
docker-compose up -d
```

#### 3. **Frontend Can't Reach Backend**

**Error:** `Failed to fetch from http://localhost:8000`

**Solution:**
```bash
# Check backend is running
docker-compose ps backend

# Check backend health
curl http://localhost:8000/health

# Check CORS settings in backend environment
docker-compose logs backend | grep CORS
```

#### 4. **Out of Memory**

**Error:** Container keeps restarting

**Solution:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 8GB

# Or limit service memory in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### 5. **Build Failures**

**Error:** `ERROR [builder X/Y] ...`

**Solution:**
```bash
# Clean build cache
docker-compose build --no-cache

# Remove all images and rebuild
docker-compose down --rmi all
docker-compose build
docker-compose up -d
```

### Reset Everything

**Complete reset (WARNING: deletes all data):**

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean build
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## Performance Optimization

### 1. **Enable BuildKit**

```bash
# Add to ~/.bashrc or ~/.zshrc
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

### 2. **Use Layer Caching**

Dockerfiles are already optimized with multi-stage builds and proper layer ordering.

### 3. **Resource Limits**

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 4. **Database Connection Pooling**

Backend already uses SQLAlchemy connection pooling. Adjust in code if needed:

```python
# backend/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

### 5. **Redis Caching**

Implement caching for expensive operations:

```python
# Example: Cache AI responses
@router.get("/ai/cached")
async def get_cached_ai_response(prompt: str, redis: Redis = Depends(get_redis)):
    cache_key = f"ai:{hash(prompt)}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await call_ai_api(prompt)
    await redis.setex(cache_key, 3600, json.dumps(result))
    return result
```

---

## Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Scale service (if configured)
docker-compose up -d --scale backend=3

# Update images
docker-compose pull
docker-compose up -d

# Clean up
docker-compose down
docker system prune -a
```

---

## Support

For issues and questions:
- **GitHub Issues:** [Narrative OS Issues](https://github.com/yourusername/Narrative_OS/issues)
- **Documentation:** [Main README](README.md)
- **API Docs:** http://localhost:8000/docs (when running)

---

**Last Updated:** 2026-01-10
**Docker Compose Version:** 3.8
**Tested with:** Docker 24.0+, Docker Compose 2.20+

# Narrative OS - Development Setup

Complete guide to setting up your development environment.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** with npm
- **PostgreSQL 15+** (or use Docker)
- **Redis** (or use Docker)
- **Git**

---

## Quick Start (Recommended)

### 1. Clone and setup infrastructure

```bash
git clone <repository-url>
cd Narrative_OS

# Start databases with Docker
docker-compose up -d postgres redis minio
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
# At minimum, set:
# - LLM_PROVIDER=openai (or anthropic)
# - OPENAI_API_KEY=your_key_here (or ANTHROPIC_API_KEY)

# Run migrations
alembic upgrade head

# Start API server
python main.py
```

API will be available at `http://localhost:8000`

### 3. Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

---

## Manual Setup (Without Docker)

### PostgreSQL

```bash
# Install PostgreSQL with pgvector extension
# macOS:
brew install postgresql pgvector

# Ubuntu:
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-15-pgvector

# Create database
createdb narrative_os
psql narrative_os -c "CREATE EXTENSION vector;"
```

### Redis

```bash
# macOS:
brew install redis
brew services start redis

# Ubuntu:
sudo apt install redis-server
sudo systemctl start redis
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/narrative_os

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Provider (choose one)
LLM_PROVIDER=openai  # or: anthropic, custom
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security
SECRET_KEY=<generate-random-key>

# Storage (optional, for exports)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

**Generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Development Workflow

### Running Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
cd backend
pytest
```

---

## Project Structure

```
Narrative_OS/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── core/
│   │   ├── database/         # DB connection
│   │   ├── llm/              # LLM gateway
│   │   └── models/           # SQLAlchemy models
│   ├── services/
│   │   ├── canon/            # Canon management
│   │   ├── planner/          # Story planning
│   │   ├── draft/            # Prose generation
│   │   ├── qc/               # Quality control
│   │   └── export/           # Export functionality
│   └── main.py               # FastAPI app
├── frontend/                  # Next.js app (coming soon)
├── shared/                    # Shared types
├── infrastructure/            # Deployment configs
└── docs/                      # Documentation
```

---

## Common Issues

### pgvector Extension Missing

```sql
-- Connect to your database
psql narrative_os

-- Install extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Failed

1. Check PostgreSQL is running: `pg_isready`
2. Verify credentials in `.env`
3. Check database exists: `psql -l`

### LLM API Errors

- Verify API keys are correct
- Check account has credits/quota
- Test connection:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## Next Steps

After setup:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Architecture**: See [docs/architecture.md](./architecture.md)
3. **Understand Canon System**: See [docs/canon-system.md](./canon-system.md)
4. **Run Tests**: `pytest` in backend directory
5. **Start Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Support

- **Issues**: https://github.com/your-org/narrative-os/issues
- **Discussions**: https://github.com/your-org/narrative-os/discussions

---

**Happy coding!** 📖✨

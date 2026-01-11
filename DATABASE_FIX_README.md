# Database Fix Guide

## Problem Summary

Your Narrative OS application is experiencing two main issues:

1. **Database Error**: PostgreSQL is receiving connections for a database called "narrative" that doesn't exist. The correct database name is "narrative_os".
2. **Backend Import Error**: The Docker build cache contains old code missing the `get_ai_config` function.
3. **Migration Conflicts**: The PostgreSQL volume contains old schema objects (like the `subscriptiontier` enum) that conflict with new migrations.

## Root Cause

The PostgreSQL volume (`narrative_os_postgres_data`) contains leftover data from a previous run with a different schema. When you run migrations, they encounter duplicate objects and fail.

## Solution

### Option 1: Automated Fix (Recommended)

Run the automated fix script:

**On Windows (PowerShell):**
```powershell
.\fix-database.ps1
```

**On Linux/Mac:**
```bash
./fix-database.sh
```

This script will:
1. Stop all containers
2. Remove the PostgreSQL volume (cleaning old data)
3. Rebuild the backend without cache (picking up new code)
4. Start services and run migrations
5. Show you the status

### Option 2: Manual Fix

If you prefer to do it step-by-step:

```bash
# 1. Stop everything
docker compose down

# 2. Remove the PostgreSQL volume
docker volume rm narrative_os_postgres_data

# 3. Rebuild backend without cache
docker compose build --no-cache backend

# 4. Start just the database services first
docker compose up -d postgres redis minio

# 5. Wait for PostgreSQL to be ready
sleep 10

# 6. Run migrations
docker compose run --rm backend alembic upgrade head

# 7. Start all services
docker compose up -d

# 8. Check status
docker compose ps
docker compose logs backend
```

### Option 3: Quick Fix (Keep Data)

If you want to keep your data and just fix the immediate issues:

```bash
# 1. Stop containers
docker compose down

# 2. Remove only backend container and image
docker rm narrative_backend
docker rmi narrative_os-backend

# 3. Rebuild and start
docker compose build --no-cache backend
docker compose up -d
```

Note: This may not work if there are schema conflicts.

## Verification

After running the fix, verify everything is working:

```bash
# Check all services are running
docker compose ps

# Check backend logs (should show no errors)
docker compose logs backend

# Test the API
curl http://localhost:8000/health
```

You should see:
- All services in "Up" state
- No database connection errors
- Backend starts successfully without import errors

## Prevention

To avoid this in the future:

1. **Use migrations properly**: Always run `alembic upgrade head` after schema changes
2. **Clean volumes when needed**: If you're changing database schemas significantly, remove the volume first
3. **Rebuild without cache**: When code changes aren't picked up, use `--no-cache`

## Troubleshooting

### If the script fails:

1. **Check Docker is running**: `docker ps`
2. **Check for port conflicts**: Make sure ports 5432, 6379, 8000, 9000, 9001, 3000 are available
3. **Check Docker resources**: Ensure Docker has enough memory (at least 4GB recommended)
4. **View logs**: `docker compose logs postgres backend`

### If migrations fail:

If you get migration errors after removing the volume, there might be an issue with the migration files themselves. Check:

```bash
docker compose run --rm backend alembic current
docker compose run --rm backend alembic history
```

## Need Help?

If none of these solutions work, gather these diagnostics:

```bash
docker compose ps
docker compose logs postgres
docker compose logs backend
docker volume ls | grep narrative
```

Then reach out with these logs for further assistance.

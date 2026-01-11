# Fix Database and Backend Issues
# This script will clean up the database and rebuild the backend

Write-Host "Stopping all containers..." -ForegroundColor Yellow
docker compose down

Write-Host "`nRemoving PostgreSQL volume to start fresh..." -ForegroundColor Yellow
docker volume rm narrative_os_postgres_data -ErrorAction SilentlyContinue

Write-Host "`nRebuilding backend without cache..." -ForegroundColor Yellow
docker compose build --no-cache backend

Write-Host "`nStarting services..." -ForegroundColor Yellow
docker compose up -d postgres redis minio

Write-Host "`nWaiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nRunning database migrations..." -ForegroundColor Yellow
docker compose run --rm backend alembic upgrade head

Write-Host "`nStarting all services..." -ForegroundColor Yellow
docker compose up -d

Write-Host "`nSetup complete! Checking service status..." -ForegroundColor Green
docker compose ps

Write-Host "`nBackend logs (checking for errors):" -ForegroundColor Yellow
docker compose logs --tail=50 backend

#!/bin/bash
# Fix Database and Backend Issues
# This script will clean up the database and rebuild the backend

set -e

echo "🛑 Stopping all containers..."
docker compose down

echo "🗑️  Removing PostgreSQL volume to start fresh..."
docker volume rm narrative_os_postgres_data 2>/dev/null || true

echo "🔨 Rebuilding backend without cache..."
docker compose build --no-cache backend

echo "🚀 Starting services..."
docker compose up -d postgres redis minio

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo "📊 Running database migrations..."
docker compose run --rm backend alembic upgrade head

echo "🌟 Starting all services..."
docker compose up -d

echo "✅ Setup complete! Checking service status..."
docker compose ps

echo ""
echo "📝 Backend logs (checking for errors):"
docker compose logs --tail=50 backend

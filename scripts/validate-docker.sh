#!/bin/bash
# Validate Docker setup for Narrative OS

set -e

echo "🐳 Narrative OS - Docker Validation Script"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
echo ""
echo "2. Checking Docker Compose installation..."
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✓${NC} Docker Compose installed: $COMPOSE_VERSION"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${YELLOW}⚠${NC} Using legacy docker-compose: $COMPOSE_VERSION"
    echo -e "${YELLOW}⚠${NC} Consider upgrading to Docker Compose V2"
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}✗${NC} Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Set compose command
if [ -z "$COMPOSE_CMD" ]; then
    COMPOSE_CMD="docker compose"
fi

# Validate docker-compose.yml
echo ""
echo "3. Validating docker-compose.yml syntax..."
if $COMPOSE_CMD config --quiet; then
    echo -e "${GREEN}✓${NC} docker-compose.yml syntax is valid"
else
    echo -e "${RED}✗${NC} docker-compose.yml has syntax errors"
    exit 1
fi

# Check for required files
echo ""
echo "4. Checking required files..."
FILES=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/.dockerignore"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/.dockerignore"
    "frontend/package.json"
    ".env.example"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} Missing: $file"
        exit 1
    fi
done

# Check .env file
echo ""
echo "5. Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    # Check for required variables
    REQUIRED_VARS=("SECRET_KEY" "DATABASE_URL")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env; then
            echo -e "${GREEN}  ✓${NC} $var is set"
        else
            echo -e "${YELLOW}  ⚠${NC} $var not found in .env"
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo -e "${YELLOW}⚠${NC} Copy .env.example to .env and configure it:"
    echo "    cp .env.example .env"
fi

# Check Docker daemon
echo ""
echo "6. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker daemon is running"
else
    echo -e "${RED}✗${NC} Docker daemon is not running"
    echo "    Start Docker Desktop or run: sudo systemctl start docker"
    exit 1
fi

# Check available resources
echo ""
echo "7. Checking system resources..."
TOTAL_MEM=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo "unknown")
if [ "$TOTAL_MEM" != "unknown" ]; then
    MEM_GB=$((TOTAL_MEM / 1024 / 1024 / 1024))
    if [ $MEM_GB -ge 4 ]; then
        echo -e "${GREEN}✓${NC} Available memory: ${MEM_GB}GB"
    else
        echo -e "${YELLOW}⚠${NC} Available memory: ${MEM_GB}GB (recommended: 4GB+)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Could not determine available memory"
fi

# Test build (without actually building)
echo ""
echo "8. Validating Docker build contexts..."
for context in "backend" "frontend"; do
    if [ -d "$context" ]; then
        echo -e "${GREEN}✓${NC} $context/ directory exists"
    else
        echo -e "${RED}✗${NC} Missing directory: $context/"
        exit 1
    fi
done

# Summary
echo ""
echo "==========================================="
echo -e "${GREEN}✓ All validation checks passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure .env file (if not already done):"
echo "     cp .env.example .env"
echo ""
echo "  2. Start the stack:"
echo "     $COMPOSE_CMD up -d"
echo ""
echo "  3. Run database migrations:"
echo "     $COMPOSE_CMD exec backend alembic upgrade head"
echo ""
echo "  4. Access the application:"
echo "     Frontend:  http://localhost:3000"
echo "     Backend:   http://localhost:8000"
echo "     API Docs:  http://localhost:8000/docs"
echo ""
echo "For detailed instructions, see: DOCKER.md"

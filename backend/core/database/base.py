"""
Database connection and session management
Supports both sync (legacy) and async (modern) patterns
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://narrative:narrative@localhost:5432/narrative_os"
)

# Async database URL (replace postgresql:// with postgresql+asyncpg://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# === SYNC ENGINE (Legacy - for existing code) ===
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,  # Changed from NullPool for production
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("SQL_ECHO", "False").lower() == "true"
)

# Sync session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === ASYNC ENGINE (Modern - for new auth code) ===
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true"
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models (shared between sync and async)
Base = declarative_base()


# === DEPENDENCIES ===

def get_db():
    """
    Dependency for FastAPI routes to get sync DB session (legacy)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """
    Dependency for FastAPI routes to get async DB session (modern)
    Use this for all new code, especially auth
    """
    async with AsyncSessionLocal() as session:
        yield session


# === INITIALIZATION ===

def init_db():
    """
    Initialize database - create all tables (sync)
    """
    Base.metadata.create_all(bind=engine)


async def init_async_db():
    """
    Initialize database - create all tables (async)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

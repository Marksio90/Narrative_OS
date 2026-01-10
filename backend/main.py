"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database.base import init_db
import os

# Initialize FastAPI app
app = FastAPI(
    title="Narrative OS API",
    description="AI-powered narrative platform for serious fiction writers",
    version="0.1.0",
)

# CORS configuration
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:8000",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    """
    init_db()
    print("✅ Database initialized")


@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "Narrative OS API",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """
    Health check for monitoring
    """
    return {"status": "healthy"}


# Import routers
from api.routes import canon, contracts, promise_ledger, planner, qc, draft, export, ai_draft, desktop, projects, chapters, voice_fingerprint, consequences, character_arcs
from api.routes import auth, permissions
from api.schemas.user import UserRead, UserCreate

# === Authentication Routes (FastAPI-Users) ===
app.include_router(
    auth.auth_router,
    prefix="/api/auth/jwt",
    tags=["Authentication"]
)
app.include_router(
    auth.register_router,
    prefix="/api/auth",
    tags=["Authentication"]
)
app.include_router(
    auth.users_router,
    prefix="/api/users",
    tags=["Users"]
)
app.include_router(
    auth.reset_password_router,
    prefix="/api/auth",
    tags=["Authentication"]
)
app.include_router(
    auth.verify_router,
    prefix="/api/auth",
    tags=["Authentication"]
)
app.include_router(
    auth.custom_router,
    tags=["Authentication"]
)

# === Permissions & Collaboration ===
app.include_router(
    permissions.router,
    prefix="/api",
    tags=["Permissions"]
)

# === Core Feature Routes ===
app.include_router(desktop.router, prefix="/api/desktop", tags=["Desktop"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(chapters.router, prefix="/api", tags=["Chapters"])
app.include_router(canon.router, prefix="/api/canon", tags=["Canon"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(promise_ledger.router, prefix="/api/promises", tags=["Promise Ledger"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(qc.router, prefix="/api/qc", tags=["Quality Control"])
app.include_router(draft.router, prefix="/api/draft", tags=["Draft Generation"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(ai_draft.router, prefix="/api", tags=["AI Writing Assistant"])
app.include_router(voice_fingerprint.router, prefix="/api/voice", tags=["Voice Fingerprinting"])
app.include_router(consequences.router, prefix="/api/consequences", tags=["Consequence Simulator"])
app.include_router(character_arcs.router, prefix="/api/character-arcs", tags=["Character Arcs"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

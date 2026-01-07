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
from api.routes import canon, contracts, promise_ledger, planner, qc, draft

# Include routers
app.include_router(canon.router, prefix="/api/canon", tags=["Canon"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(promise_ledger.router, prefix="/api/promises", tags=["Promise Ledger"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(qc.router, prefix="/api/qc", tags=["Quality Control"])
app.include_router(draft.router, prefix="/api/draft", tags=["Draft Generation"])

# TODO: Add more routers as they're implemented
# from api.routes import export
# app.include_router(export.router, prefix="/api/export", tags=["Export"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

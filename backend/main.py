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


# Import routers (will be added incrementally)
# from api.routes import canon, planner, draft, qc, export
# app.include_router(canon.router, prefix="/api/canon", tags=["canon"])
# app.include_router(planner.router, prefix="/api/planner", tags=["planner"])
# app.include_router(draft.router, prefix="/api/draft", tags=["draft"])
# app.include_router(qc.router, prefix="/api/qc", tags=["quality"])
# app.include_router(export.router, prefix="/api/export", tags=["export"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

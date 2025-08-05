"""Main FastAPI application."""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from ..core.config import settings
from ..core.database import create_tables
from ..utils.logging import setup_logging
from .routes import flights, analysis, telegram


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Celes.ia API")
    setup_logging()
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Celes.ia API")


# Create FastAPI app
app = FastAPI(
    title="Celes.ia API",
    description="AI-powered flight search and analysis API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Celes.ia API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Include routers
app.include_router(flights.router, prefix="/api/v1/flights", tags=["flights"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["telegram"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug
    )

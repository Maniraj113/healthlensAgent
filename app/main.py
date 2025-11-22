"""FastAPI application for Health Triage Multi-Agent System"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .api.routes import router
from .database import create_db_and_tables


# Configure logging - MUST be done before importing other modules
import sys

# Get root logger and configure it
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

# Create console handler with formatter
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Create file handler
file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
file_handler.setFormatter(formatter)

# Add handlers to root logger
if not root_logger.handlers:
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

# Ensure app loggers propagate
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
logger.propagate = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Create database tables
    logger.info("Starting Health Triage API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    
    create_db_and_tables()
    logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Health Triage API...")


# Create FastAPI application
app = FastAPI(
    title="Health Triage Multi-Agent System",
    description="""
    Production-ready backend + agentic AI system using Google Agent Development Kit (ADK).
    
    Supports frontline health workers in underserved rural India to detect early health risks
    without lab infrastructure.
    
    ## Features
    
    - **Multi-Agent Architecture**: 5 specialized ADK agents for intake, image analysis, 
      clinical reasoning, action planning, and synchronization
    - **Medical Rule Engine**: Evidence-based clinical decision rules for anemia, maternal risk,
      diabetes, malnutrition, and infection
    - **Multilingual Support**: English, Hindi, Tamil, Telugu, Bengali
    - **Offline-First**: Minimal rule-based triage when network unavailable
    - **Image Analysis**: Analyzes conjunctiva, swelling, child arm, and skin photos
    
    ## Endpoints
    
    - `POST /api/v1/analyze`: Analyze patient and get triage recommendations
    - `POST /api/v1/sync`: Sync offline visits
    - `GET /api/v1/visit/{visit_id}`: Retrieve visit record
    - `GET /api/v1/health`: Health check
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
# Configure based on environment
cors_origins = [
    "http://localhost:3000",      # Local frontend dev
    "http://localhost:80",        # Local frontend nginx
    "http://localhost",           # Local frontend nginx (default port)
    "http://127.0.0.1:3000",      # Local loopback
    "http://127.0.0.1:80",        # Local loopback nginx
]

# Add Cloud Run frontend URL if available
if settings.environment == "production":
    # For Cloud Run, allow the frontend service URL
    # This should be set via environment variable
    import os
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        cors_origins.append(frontend_url)
    # Also allow all HTTPS origins in production (more permissive for Cloud Run)
    cors_origins.append("https://*.run.app")
else:
    # Development: allow all origins
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Include API routes
app.include_router(router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Health Triage Multi-Agent System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

"""FastAPI application for Health Triage Multi-Agent System"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .api.routes import router
from .database import create_db_and_tables


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Create database tables
    logger.info("🚀 Starting Health Triage API...")
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🗄️  Database: {settings.database_url}")
    
    create_db_and_tables()
    logger.info("✅ Database tables created")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Health Triage API...")


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

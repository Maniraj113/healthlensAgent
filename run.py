"""Simple script to run the FastAPI server"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  Health Triage Multi-Agent System                        ║
    ║  Powered by Google ADK                                   ║
    ╚══════════════════════════════════════════════════════════╝
    
    🌐 Server starting on http://{settings.host}:{settings.port}
    📚 API Documentation: http://{settings.host}:{settings.port}/docs
    🔧 Environment: {settings.environment}
    
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )

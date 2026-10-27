"""
app/main.py
Root FastAPI application definition, middleware configuration, and router mounting.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, documents, query

# Initialize the main FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A modular, production-ready Retrieval-Augmented Generation (RAG) backend built with FastAPI and ChromaDB.",
    docs_url="/docs",      # Interactive Swagger UI endpoint
    redoc_url="/redoc"     # Alternative documentation format
)

# Configure CORS (Cross-Origin Resource Sharing)
# Allows web browsers and frontend apps to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # In production, replace with specific domains (e.g. ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],     # Allow all HTTP headers
)

# Register our modular feature routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with quick welcome message and documentation links."""
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}!",
        "docs": "/docs",
        "health": "/health"
    }
    
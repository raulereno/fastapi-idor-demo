"""
Main FastAPI application
"""
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.api import api_router
from app.core.middleware import SetAppUserMiddleware, UserIDMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="IDOR vulnerability demonstration and remediation using JWT authentication and authorization middleware",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware for RLS support
app.add_middleware(UserIDMiddleware)
app.add_middleware(SetAppUserMiddleware)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "IDOR vulnerability demonstration with two mitigation strategies",
        "endpoints": {
            "documents": {
                "vulnerable": "/api/v1/documents/vulnerable/{document_id} - IDOR vulnerable endpoint (no auth)",
                "secure": "/api/v1/documents/secure/{document_id} - Mitigation #1: Route-level owner check",
                "rls": "/api/v1/documents/rls/{document_id} - Mitigation #2: PostgreSQL RLS demonstration",
                "my_documents": "/api/v1/documents/secure/me - Get my documents",
                "create": "/api/v1/documents/ - Create document",
                "update": "/api/v1/documents/{document_id} - Update document",
                "delete": "/api/v1/documents/{document_id} - Delete document",
                "setup_demo": "/api/v1/documents/demo/setup - Create demo documents"
            },
            "users": {
                "me": "/api/v1/users/me - Get current user info",
                "list": "/api/v1/users/ - List all users",
                "setup_demo": "/api/v1/users/demo/setup - Create demo users"
            },
            "auth": {
                "register": "/api/v1/auth/register - Register user",
                "login": "/api/v1/auth/login - Login and get JWT token"
            }
        },
        "mitigation_strategies": {
            "strategy_1": "Route-level owner check with JWT authentication",
            "strategy_2": "PostgreSQL Row-Level Security (RLS) with middleware"
        },
        "testing": {
            "test_script": "python test_mitigations.py - Run comprehensive tests",
            "documentation": "/docs - Interactive API documentation"
        }
    } 
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from .core.config import settings
from .core.exceptions import CivicAIException
from .database.connection import init_db
from .schemas.common import HealthResponse
from .ai import ModelLoader
from .services.routing_service import CivicRoutingService
from .api import (
    auth_router,
    users_router,
    incidents_router,
    notifications_router,
    community_router,
    sos_router,
    departments_router,
    ai_router,
    admin_router,
    citizen_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    db = init_db()
    if db:
        try:
            CivicRoutingService.seed_default_departments(db)
            # Seed default admin user if not existing
            from .models.user import User
            from .core.security import get_password_hash
            admin_user = db.query(User).filter(User.email == "admin@civic.ai").first()
            if not admin_user:
                admin_user = User(
                    name="System Administrator",
                    email="admin@civic.ai",
                    phone="9999999999",
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    points=1000,
                    reputation_score=5.0,
                )
                db.add(admin_user)
                db.commit()
        finally:
            db.close()

    # Phase 2: Ensure upload directories exist at startup
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    incidents_upload_dir = os.path.join(upload_dir, "incidents")
    os.makedirs(incidents_upload_dir, exist_ok=True)

    # Phase 5: Initialize AI Model Loader singleton
    ModelLoader.load()

    yield
    # Teardown logic if needed

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Community Emergency & Civic Problem Reporting System - Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware (supports Flutter mobile emulator, simulator, local web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Error Handlers
# ==============================================================================

@app.exception_handler(CivicAIException)
async def civic_exception_handler(request: Request, exc: CivicAIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join([str(loc) for loc in error.get("loc", []) if loc != "body"])
        errors.append({"field": field, "message": error.get("msg")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": errors},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred while processing the request."},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

# ==============================================================================
# Health Check Endpoint
# ==============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
)
def health_check():
    """Verify that backend service is running and responsive."""
    return HealthResponse(status="ok", service="civic-ai-backend")

# ==============================================================================
# Router Registrations
# ==============================================================================

# API v1 Prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(community_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(sos_router, prefix=settings.API_V1_STR)
app.include_router(departments_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(citizen_router, prefix=settings.API_V1_STR)

# Also expose auth, incidents, ai, admin, community, citizen at root level for quick prototyping convenience
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(incidents_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(community_router)
app.include_router(citizen_router)


# ==============================================================================
# Phase 2: Static File Serving — Uploaded Incident Images
# ==============================================================================

# Mount /uploads to serve stored incident images during development.
# In production, replace this with a CDN or object storage proxy.
_upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_upload_dir), name="uploads")

from fastapi.responses import FileResponse

_admin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "admin"))

@app.get("/admin-dashboard", include_in_schema=False)
@app.get("/admin", include_in_schema=False)
def serve_admin_dashboard():
    index_path = os.path.join(_admin_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Admin dashboard index.html not found"})

if os.path.exists(_admin_dir):
    app.mount("/admin-static", StaticFiles(directory=_admin_dir), name="admin_static")

# ==============================================================================
# Citizen Portal — Web SPA & PWA
# ==============================================================================

_citizen_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "citizen"))

@app.get("/", include_in_schema=False)
@app.get("/citizen-portal", include_in_schema=False)
@app.get("/citizen", include_in_schema=False)
def serve_citizen_portal():
    index_path = os.path.join(_citizen_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Citizen portal index.html not found"})

if os.path.exists(_citizen_dir):
    app.mount("/citizen-static", StaticFiles(directory=_citizen_dir), name="citizen_static")
    app.mount("/", StaticFiles(directory=_citizen_dir, html=True), name="citizen_root")


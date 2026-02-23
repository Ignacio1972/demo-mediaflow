from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.services.scheduler import scheduler_worker
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Auth version middleware - adds X-Auth-Version header to all responses
VERSION_FILE = Path(__file__).parent.parent / "auth_version.txt"

class AuthVersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            version = VERSION_FILE.read_text().strip()
        except FileNotFoundError:
            version = "v1"
        response.headers["X-Auth-Version"] = version
        return response

app.add_middleware(AuthVersionMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Auth-Version"],
)

# Mount static files
try:
    app.mount("/storage", StaticFiles(directory="storage"), name="storage")
except RuntimeError:
    logger.warning("Storage directory not found - will be created on first upload")


# Health check endpoint
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📝 Environment: {settings.APP_ENV}")
    logger.info(f"🔗 API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")

    # Start the scheduler worker
    await scheduler_worker.start()
    logger.info("📅 Scheduler worker started")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Stop the scheduler worker
    await scheduler_worker.stop()
    logger.info("📅 Scheduler worker stopped")

    logger.info("👋 Shutting down MediaFlowDemo")


# Import and include routers
from app.api.v1 import api_router

app.include_router(api_router, prefix="/api/v1")

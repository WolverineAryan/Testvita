import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config.settings import settings
from app.database.session import engine, Base
from app.api.v1 import api_router
from app.seeds.seed_data import seed_database_if_empty

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("codevita")

# In-memory IP-based rate limiter (Sliding Window)
RATE_LIMIT_RECORD = defaultdict(list)
MAX_REQUESTS_PER_WINDOW = 120  # 120 requests per minute per IP
WINDOW_SECONDS = 60

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")
    
    # Auto-seed initial content if needed
    try:
        await seed_database_if_empty()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")

    yield
    logger.info("Shutting down CodeVita AI Coach backend...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Adaptive AI Coach for Competitive Programming & CodeVita Preparation",
    lifespan=lifespan
)

# Security Middleware: Headers & Rate Limiting
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # 1. Rate Limiting Check
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean old requests in window
    timestamps = [t for t in RATE_LIMIT_RECORD[client_ip] if now - t < WINDOW_SECONDS]
    RATE_LIMIT_RECORD[client_ip] = timestamps

    # Exclude health check and root from strict rate limit
    if request.url.path not in ["/health", "/"] and len(timestamps) >= MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Too many requests. Please slow down.",
                "retry_after_seconds": int(WINDOW_SECONDS - (now - timestamps[0]))
            }
        )

    RATE_LIMIT_RECORD[client_ip].append(now)

    # 2. Process Request
    response: Response = await call_next(request)

    # 3. Add Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    return response

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again."
            }
        }
    )

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "tagline": "Your adaptive AI coach for competitive programming."
    }

@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "engine": "FastAPI + SQLAlchemy"
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

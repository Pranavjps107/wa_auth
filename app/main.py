# ============================================================================
# AUTH SERVICE - COMPLETE CODEBASE (Matches Document Structure)
# ============================================================================

# ----------------------------------------------------------------------------
# FILE: auth-service/app/main.py
# ----------------------------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import router as api_v1_router
from app.db import Base, engine

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.ERROR)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    logger.info("Starting Auth Service...")
    Base.metadata.create_all(bind=engine)
    logger.info("Auth Service started")
    yield
    logger.info("Shutting down Auth Service...")


app = FastAPI(
    title="Authentication Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "auth"}


# Include API routes
app.include_router(api_v1_router, prefix="/v1")
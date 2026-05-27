
"""Фабрика FastAPI приложения"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import AppSettings
from app.core.logger import setup_logger
from app.api.v1 import tenders, health  

settings = AppSettings()
logger = setup_logger(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и завершение ресурсов приложения"""
    
    logger.info("Приложение запускается...")
    yield
    logger.info("Приложение останавливается")

def create_app() -> FastAPI:
    """Создаёт и конфигурирует экземпляр FastAPI"""
    app = FastAPI(
        title="Tender Search API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    
    app.include_router(tenders.router, prefix="/api/v1/tenders", tags=["tenders"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])  
    
    return app

app = create_app()
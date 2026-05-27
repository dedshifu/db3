
"""Фабрика FastAPI приложения"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import AppSettings
from app.core.logger import setup_logger
from app.api.v1 import tenders, health  

settings = AppSettings()
logger = setup_logger(settings.log_level)

# Глобальные переменные для хранения engine и session_factory
engine = None
session_factory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и завершение ресурсов приложения"""
    global engine, session_factory
    
    logger.info("Приложение запускается...")
    
    # Инициализация engine и session_factory при старте
    engine = create_async_engine(
        settings.database_url,
        echo=False,              
        pool_pre_ping=True,       
        pool_size=5,              
        max_overflow=10           
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    
    # Сохраняем в app.state для доступа через зависимости
    app.state.session_factory = session_factory
    
    yield
    
    # Закрытие пула соединений при остановке
    if engine:
        await engine.dispose()
    
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
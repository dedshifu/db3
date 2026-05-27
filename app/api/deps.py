"""Зависимости для FastAPI (DI-контейнер)"""
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi import Depends
from functools import cache

from app.core.config import AppSettings

@cache
def get_settings() -> AppSettings:
    """Возвращает конфигурацию (кэшируется после первого вызова, чтобы не парсить .env каждый раз)"""
    return AppSettings()

def get_session_factory(settings: AppSettings = Depends(get_settings)) -> async_sessionmaker[AsyncSession]:
    """Создаёт фабрику сессий. Движок инициализируется один раз при старте."""
    
    if not hasattr(get_session_factory, "engine"):
        get_session_factory.engine = create_async_engine(
            settings.database_url,
            echo=False,               
            pool_pre_ping=True,       
            pool_size=5,              
            max_overflow=10           
        )
        get_session_factory.factory = async_sessionmaker(
            get_session_factory.engine, 
            expire_on_commit=False
        )
    return get_session_factory.factory

async def get_db(session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory)) -> AsyncGenerator[AsyncSession, None]:
    """Возвращает сессию БД с автоматическим commit/rollback"""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()  
        except Exception:
            await session.rollback() 
            raise
        finally:
            await session.close()    

async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный HTTP-клиент для интеграции с ЕИС/Госплан"""
    async with AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client
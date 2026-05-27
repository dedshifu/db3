"""Health check endpoint для мониторинга"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import get_db

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(session: AsyncSession = Depends(get_db)) -> dict:
    """Проверка доступности приложения и базы данных"""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "service": "tender-search-api"}
    except Exception as e:
        return {"status": "unhealthy", "database": f"error: {str(e)}", "service": "tender-search-api"}
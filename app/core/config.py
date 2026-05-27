"""Конфигурация приложения через переменные окружения"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """Глобальные настройки сервиса. Загружаются из .env или окружения с префиксом APP_"""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tenders"
    gosplan_base_url: str = "https://api.gosplan.info"
    gosplan_api_key: str = ""
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
        case_sensitive=False,
    )
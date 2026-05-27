"""Настройка логирования приложения в JSON-формате"""
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(level: str = "INFO") -> logging.Logger:
    """Конфигурирует корневой логгер с JSON-форматированием и ротацией
    
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Настроенный экземпляр logging.Logger
    """
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "msg": "%(message)s"}'
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
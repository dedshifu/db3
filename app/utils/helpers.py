"""Общие утилиты для безопасной работы с данными."""
from datetime import datetime
from typing import Any, Optional


def safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    """
    Безопасный доступ к вложенным ключам в словаре
    Пример: safe_get(obj, 'a', 'b', 'c', default=[])
    
    Возвращает значение как есть, без преобразования в строку.
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def parse_iso_date(val: Optional[str]) -> Optional[datetime]:
    """
    Парсинг ISO-даты с обработкой ошибок и timezone
    Поддерживает форматы: 2024-01-15T10:30:00Z, 2024-01-15T10:30:00+03:00
    """
    if not val:
        return None
    try:
        
        normalized = val.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except (ValueError, TypeError, AttributeError):
        return None


def clean_price(value: Any) -> Optional[float]:
    """Очистка и конвертация цены в float"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        
        cleaned = value.replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None
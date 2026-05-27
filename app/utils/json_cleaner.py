"""Утилиты для рекурсивной очистки входящих JSON"""
from typing import Any

def clean_json_payload(data: Any) -> Any:
    """Рекурсивно удаляет пробелы из ключей и строковых значений
    
    Args:
        data: Исходная структура (dict, list, str, или примитив)
        
    Returns:
        Очищенную копию структуры данных
    """
    if isinstance(data, dict):
        return {k.strip(): clean_json_payload(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_json_payload(item) for item in data]
    if isinstance(data, str):
        return data.strip()
    return data
# Tender Search API
Поисковый сервис торгов с интеграцией к ЕИС/Госплан.

##  Быстрый старт
1. Клонируйте репозиторий
2. `docker compose up -d`
3. API доступен: `http://localhost:8000/docs`
4. Локальный запуск без Docker:
   ```bash
   pip install -e ".[dev]"
   alembic upgrade head
   uvicorn app.main:app --reload
## src/core/config.py
"""
Конфигурация приложения InvestCalc.

Здесь централизовано определяются:
- корневая папка проекта;
- каталог для JSON-данных;
- путь к файлу сценариев.

При необходимости сюда можно добавить:
- чтение переменных окружения;
- переключение окружений (dev/test/prod).
"""

from __future__ import annotations

from pathlib import Path


class Settings:
    """Простая конфигурация без Pydantic BaseSettings (для учебного проекта)."""

    def __init__(self) -> None:
        ## Путь до корня проекта: .../<project_root>/
        ## Файл находится в src/core/config.py → parents[2] = <project_root>
        self.BASE_DIR: Path = Path(__file__).resolve().parents[2]

        ## Каталог для хранения данных (JSON вместо БД)
        self.DATA_DIR: Path = self.BASE_DIR / "data"

        ## Файл, в котором будут храниться сценарии расчётов
        self.SCENARIOS_FILE: Path = self.DATA_DIR / "scenarios.json"

        ## Метаданные приложения (для Swagger)
        self.APP_NAME: str = "InvestCalc API"
        self.APP_DESCRIPTION: str = (
            "Мини-информационная система «InvestCalc — Инвестиционный аналитик ИС».\n\n"
            "Функции:\n"
            "- расчёт TCO, ROI, Payback Period;\n"
            "- анализ чувствительности ±20%;\n"
            "- сценарный анализ на основе JSON-файлов (без СУБД);\n"
            "- удобная документация Swagger (/docs) и ReDoc (/redoc)."
        )
        self.APP_VERSION: str = "0.1.0"


settings = Settings()

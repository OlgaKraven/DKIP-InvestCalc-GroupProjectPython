## src/main.py
"""
Главная точка входа FastAPI-приложения InvestCalc.

Задачи:
- создать объект FastAPI с метаданными (Swagger / OpenAPI);
- настроить CORS;
- подключить роуты API (v1);
- определить базовые служебные эндпоинты (/, /health, /redoc).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html

from src.api.v1.routes_invest import router as invest_router
from src.core.config import settings
from src.ui.routes_web import router as web_router


def create_app() -> FastAPI:
    """Фабрика приложения — удобно для тестирования и расширения."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",        ## Swagger UI
        redoc_url=None,          ## ВСТРОЕННЫЙ ReDoc отключаем
        openapi_url="/openapi.json",
    )

    ## ---------- CORS ----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  ## для учебного проекта можно разрешить всё
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ## ---------- API v1 ----------
    app.include_router(
        invest_router,
        prefix="/api/v1",
        tags=["invest"],
    )
    app.include_router(
        web_router,
        prefix="",   ## путь будет просто /ui
    )
    ## ---------- Root ----------
    @app.get("/", summary="Root endpoint", tags=["service"])
    async def root() -> dict:
        return {
            "message": "InvestCalc API is running",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
        }

    ## ---------- Health ----------
    @app.get("/health", summary="Проверка работоспособности сервиса", tags=["service"])
    async def health() -> dict:
        return {"status": "ok"}

    ## ---------- Явное формирование OpenAPI-схемы ----------
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.APP_NAME,
            version=settings.APP_VERSION,
            description=settings.APP_DESCRIPTION,
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return openapi_schema

    app.openapi = custom_openapi

    ## ---------- Наш собственный ReDoc по /redoc ----------
    @app.get("/redoc", include_in_schema=False)
    async def redoc_ui():
        return get_redoc_html(
            ## используем то же openapi_url, что и приложение
            openapi_url=app.openapi_url,
            title=f"{settings.APP_NAME} – ReDoc documentation",
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

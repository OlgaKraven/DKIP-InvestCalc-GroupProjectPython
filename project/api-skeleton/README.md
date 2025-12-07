## API Skeleton — шаблон FastAPI-сервиса с JSON-хранилищем

Этот каталог содержит минимальный каркас API-проекта на **FastAPI**, который можно
использовать как стартовую точку для учебных и командных проектов.

## Структура

```text
api-skeleton/
  README.md           ## описание каркаса
  requirements.txt    ## зависимости Python
  src/                ## исходный код приложения
    main.py           ## точка входа (FastAPI + Swagger)
    core/             ## конфигурация, общие настройки
    api/              ## маршруты (routers)
    models/           ## Pydantic-модели
    services/         ## бизнес-логика
    storage/          ## работа с JSON-файлами вместо БД
  data/
    items.json        ## пример JSON-хранилища
  tests/
    test_healthcheck.py  ## пример автотеста
```

## Быстрый старт

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

После запуска:

* Swagger UI: `http://localhost:8000/docs`
* OpenAPI JSON: `http://localhost:8000/openapi.json`
* Пример эндпоинта: `GET /api/v1/items`

## Как адаптировать под свой проект

1. Переименуйте сущность `Item` в свою (`Scenario`, `Ticket`, `Order` и т.д.).
2. Обновите модели в `models/item.py`.
3. Измените бизнес-логику в `services/item_service.py`.
4. При необходимости обновите структуру JSON-хранилища в `data/items.json`.
5. Добавьте новые роуты в `api/v1/routes_example.py` или создайте свои модули.

## Назначение

Каркас предназначен для:

* учебных проектов по backend-разработке;
* быстрых прототипов API с хранением в JSON;
* демонстрации архитектуры «FastAPI + сервисы + JSON-storage»;
* основы для более сложных проектов (с переходом на БД).

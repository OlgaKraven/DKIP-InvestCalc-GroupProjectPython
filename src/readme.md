## Папка `src` — серверное приложение InvestCalc (FastAPI)

В каталоге `src` находится **основной backend-проект InvestCalc**:

- REST API на базе **FastAPI**;
- бизнес-логика расчётов эффективности ИС (TCO, ROI, Payback);
- работа со сценариями через JSON-файлы в папке `data/`;
- простая веб-форма для ручного ввода данных.

Этот код — **боевое приложение** InvestCalc. Учебные каркасы (skeleton’ы) лежат отдельно в папке `PROJECT/`.

---

## Структура папки

```text
src/
  main.py                 ## точка входа, создание FastAPI-приложения
  core/
    __init__.py
    config.py             ## настройки приложения (пути, метаданные и т.п.)
  api/
    __init__.py
    v1/
      __init__.py
      routes_invest.py    ## маршруты API v1 (расчёты, сценарии и др.)
  models/
    __init__.py
    invest.py             ## Pydantic-модели: входные данные, результаты, сценарии
  services/
    __init__.py
    invest_service.py     ## бизнес-логика расчётов и работы со сценариями
  ui/
    __init__.py
    routes_web.py         ## HTML-страница `/ui` с веб-формой расчёта
```

> Примечание: структура может расширяться (новые модули, сервисы, роутеры), но базовая архитектура «core + api + models + services + ui» сохраняется.

---

## Основные компоненты

## `main.py`

* фабрика `create_app()` создаёт объект `FastAPI`;
* настраивается:

  * заголовок, описание, версия (`settings.APP_NAME` и др.);
  * пути к Swagger (`/docs`) и OpenAPI (`/openapi.json`);
  * CORS (для учебных целей разрешён доступ с любых Origin);
* подключаются роутеры:

  * `src.api.v1.routes_invest` → префикс `/api/v1`, тег `invest`;
  * `src.ui.routes_web` → страница `/ui`;
* служебные эндпоинты:

  * `GET /` — корневой, ссылки на `/docs`, `/openapi.json`, `/ui`, `/health`;
  * `GET /health` — health-check сервиса;
  * `GET /redoc` (если настроен) — ReDoc-документация.

## `core/config.py`

* хранит настройки приложения:

  * название, версия, описание;
  * путь к папке `data/` и файлам `scenarios.json`, `negative-scenarios.json` и т.п.;
  * при необходимости — чтение переменных окружения (для Docker/CI).

## `api/v1/routes_invest.py`

Маршрутизатор (`APIRouter`) с основными эндпоинтами InvestCalc, например:

* `POST /api/v1/calc` — расчёт TCO/ROI/Payback по модели `InvestInput`;
* `POST /api/v1/sensitivity` (если реализован) — анализ чувствительности;
* `GET /api/v1/scenarios` / `POST /api/v1/scenarios` / `GET /api/v1/scenarios/{id}` — работа со сценариями;
* другие операции, связанные с учебными задачами.

Все типы данных опираются на модели из `src.models.invest`.

## `models/invest.py`

Набор Pydantic-моделей, описывающих предметную область:

* входные данные для расчётов (например, `InvestInput`);
* результат расчёта (например, `InvestResult`);
* сущности сценариев (`ScenarioBase`, `ScenarioDetail` и т.п.);
* при необходимости — общие типы/ответы API (`ApiError`, `PaginatedResponse` и др.).

## `services/invest_service.py`

Сервисный слой (бизнес-логика):

* функции/классы для расчёта TCO, ROI, Payback Period;
* работа со сценариями:

  * чтение/запись JSON-файлов из `data/scenarios.json`;
  * валидация, генерация идентификаторов, обновление `last_result`;
* вспомогательные операции (загрузка пресетов, работа с негативными сценариями и т.п.).

API-роуты обращаются **не напрямую к файлам**, а через сервис — это разделяет слои «транспорт» и «логика».

## `ui/routes_web.py`

Простой веб-интерфейс:

* `GET /ui` — HTML-страница с формой ввода:

  * `project_name`, `capex`, `opex`, `effects`, `period_months`, `discount_rate_percent`;
* JavaScript на странице отправляет `POST /api/v1/calc` и отображает:

  * TCO,
  * ROI (%),
  * срок окупаемости в месяцах/годах,
  * комментарий.

Страница служит наглядной демонстрацией работы API без необходимости заходить в Swagger.

---

## Запуск приложения

Из корня проекта (где лежит папка `src`):

```bash
uvicorn src.main:app --reload
```

После запуска доступны:

* Swagger UI: `http://127.0.0.1:8000/docs`
* OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
* Health-check: `http://127.0.0.1:8000/health`
* Веб-форма: `http://127.0.0.1:8000/ui`

---

## Связанные каталоги

* `data/` — JSON-хранилище сценариев и примеров (`scenarios.json`, `input-*.json`, `negative-scenarios.json` и др.);
* `docs/` — архитектурная и проектная документация (требования, ADR, C4, DevOps и т.п.);
* `PROJECT/` — учебные skeleton-проекты (`api-skeleton`, `client-skeleton`, `db-schema.sql`);
* `devops/` — Docker, CI/CD, мониторинг и эксплуатация (в отдельной папке).

---

## Как развивать `src`

* добавлять новые роутеры в `src/api/v1/` и подключать их в `main.py`;
* расширять модели в `src/models/invest.py`;
* выносить бизнес-логику в отдельные сервисы/классы в `src/services/`;
* при необходимости подключать БД (SQLAlchemy и т.п.), сохранив текущий JSON-вариант для учебных целей.

```
```

# Внутреннее устройство API (Internal API Design)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия документа: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает **внутреннюю структуру и устройство API-слоя** приложения InvestCalc:

- как устроен FastAPI-приложение;
- как организованы модули и пакеты;
- как данные проходят путь от HTTP-запроса до бизнес-логики и обратно;
- как реализованы валидация, обработка ошибок и работа с JSON-хранилищем.

Документ ориентирован на разработчиков и используется при сопровождении и развитии проекта.

---

## 2. Общая структура модулей API

API-слой реализован на базе **FastAPI** и разбит на несколько логических уровней:

```text
src/
├── main.py                 ## точка входа, создание FastAPI-приложения
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── routes_invest.py  ## HTTP-эндпоинты InvestCalc v1
├── core/
│   ├── __init__.py
│   └── config.py           ## конфигурация приложения (пути, метаданные)
├── models/
│   ├── __init__.py
│   └── invest.py           ## Pydantic-модели запросов и ответов
└── services/
    ├── __init__.py
    └── invest_service.py   ## бизнес-логика и работа с JSON
```

Принципиальный подход:

* **`main.py`** — только создание приложения и подключение роутеров.
* **`api/v1/routes_invest.py`** — HTTP-маршруты, никакой бизнес-логики.
* **`models/invest.py`** — контракт данных (Pydantic).
* **`services/invest_service.py`** — расчёты и доступ к JSON-хранилищу.
* **`core/config.py`** — общая конфигурация и пути до файлов.

---

## 3. Создание приложения (src/main.py)

Файл `src/main.py` реализует паттерн **application factory**:

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(CORSMiddleware, ...)

    app.include_router(
        invest_router,
        prefix="/api/v1",
        tags=["invest"],
    )

    @app.get("/")
    async def root(): ...
    @app.get("/health")
    async def health(): ...

    return app

app = create_app()
```

Особенности:

* Конфигурация (`название`, `описание`, `версия`, пути `/docs`, `/redoc`) берётся из `core.config.settings`.
* CORS настроен максимально свободно для учебного проекта (`allow_origins=["*"]`).
* Все доменные маршруты собраны в одном роутере `invest_router` (см. ниже).
* Есть служебные эндпоинты `/` и `/health` для проверки работоспособности.

---

## 4. Маршруты API (src/api/v1/routes_invest.py)

Основной роутер:

```python
router = APIRouter()
```

Подключение в `main.py`:

```python
app.include_router(
    invest_router,
    prefix="/api/v1",
    tags=["invest"],
)
```

### 4.1. Эндпоинт расчёта показателей

```python
@router.post(
    "/calc",
    response_model=InvestResult,
    summary="Расчёт TCO, ROI и срока окупаемости",
    tags=["calculations"],
    status_code=status.HTTP_200_OK,
)
async def calculate_invest_metrics(payload: InvestInput) -> InvestResult:
    try:
        result = calculate_metrics(payload)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
```

Маршрут:

* **Метод:** `POST`
* **Путь:** `/api/v1/calc`
* **Запрос:** `InvestInput` (Pydantic-модель)
* **Ответ:** `InvestResult`
* **Ошибки:**

  * `422 Unprocessable Entity` — некорректные входные данные (ошибка бизнес-валидации).

Бизнес-логика вынесена в `services.invest_service.calculate_metrics`.

### 4.2. Эндпоинт анализа чувствительности

```python
@router.post(
    "/sensitivity",
    response_model=SensitivityResult,
    summary="Анализ чувствительности ±20%",
    tags=["calculations"],
    status_code=status.HTTP_200_OK,
)
async def sensitivity_analysis(payload: SensitivityRequest) -> SensitivityResult:
    try:
        result = run_sensitivity(payload)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
```

Маршрут:

* **Метод:** `POST`
* **Путь:** `/api/v1/sensitivity`
* **Запрос:** `SensitivityRequest`
* **Ответ:** `SensitivityResult`

### 4.3. Работа со сценариями (JSON-хранилище)

```python
@router.get(
    "/scenarios",
    response_model=List[ScenarioShort],
    summary="Список сценариев (JSON-хранилище)",
    tags=["scenarios"],
)
async def get_scenarios() -> List[ScenarioShort]:
    return list_scenarios()
```

```python
@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Получить сценарий по идентификатору",
    tags=["scenarios"],
)
async def get_scenario_by_id(scenario_id: str) -> ScenarioDetail:
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id={scenario_id} not found",
        )
    return scenario
```

```python
@router.post(
    "/scenarios",
    response_model=ScenarioDetail,
    summary="Создать или обновить сценарий",
    tags=["scenarios"],
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_scenario(scenario: ScenarioDetail) -> ScenarioDetail:
    try:
        saved = save_scenario(scenario)
        return saved
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save scenario: {exc}",
        ) from exc
```

Особенности:

* Чтение/запись выполняются через `services.invest_service`.
* Хранилище — JSON-файл `data/scenarios.json`.
* Ошибки:

  * `404` — сценарий не найден;
  * `500` — ошибка работы с файловой системой.

---

## 5. Модели данных (src/models/invest.py)

Все запросы/ответы описаны через **Pydantic** — это обеспечивает:

* автоматическую валидацию входных данных;
* генерацию схем OpenAPI;
* удобный Swagger.

Основные модели:

* `InvestInput` — входные данные расчётов: `capex`, `opex`, `effects`, `period_months`, `discount_rate_percent`.
* `InvestResult` — результат: `tco`, `roi_percent`, `payback_months`, `payback_years`, `note`.
* `SensitivityRequest` / `SensitivityResult` / `SensitivityItem`.
* `ScenarioShort` — краткая информация о сценарии.
* `ScenarioDetail` — полная информация о сценарии (+ входные данные и последний результат).

Модели используются:

* как типы параметров в эндпоинтах (FastAPI → автоматическая валидация);
* как `response_model` для строгих контрактов ответа;
* внутри сервисов.

---

## 6. Бизнес-логика и доступ к данным (src/services/invest_service.py)

### 6.1. Расчёт экономических показателей

Ключевая функция:

```python
def calculate_metrics(input_data: InvestInput) -> InvestResult:
    if input_data.capex < 0 or input_data.opex < 0 or input_data.effects < 0:
        raise ValueError("CAPEX, OPEX и эффекты не могут быть отрицательными.")

    if input_data.period_months <= 0:
        raise ValueError("Период анализа (period_months) должен быть больше нуля.")

    tco = _calculate_tco(input_data)
    roi_percent = _calculate_roi_percent(input_data, tco)
    payback_months, payback_years, note = _calculate_payback(input_data)

    final_note = note or "Проект окупается в рамках заданного периода анализа."

    return InvestResult(
        project_name=input_data.project_name,
        tco=float(round(tco, 2)),
        roi_percent=roi_percent,
        payback_months=payback_months,
        payback_years=payback_years,
        note=final_note,
    )
```

Важно:

* Все бизнес-проверки (например, отрицательные значения, нулевой период) выполняются здесь и **возвращаются как `ValueError`**, а не как HTTP.
* HTTP-слой только превращает их в `422 Unprocessable Entity`.

### 6.2. Анализ чувствительности

```python
def run_sensitivity(request: SensitivityRequest) -> SensitivityResult:
    if request.delta_percent <= 0:
        raise ValueError("delta_percent должен быть больше 0.")
    if not request.parameters:
        raise ValueError("Не указан ни один параметр для анализа чувствительности.")

    base_result = calculate_metrics(request.base_input)
    items: List[SensitivityItem] = []

    base_input_dict = request.base_input.model_dump()
    ...
    return SensitivityResult(
        base_result=base_result,
        delta_percent=request.delta_percent,
        items=items,
    )
```

Параметры `capex`, `opex`, `effects` изменяются на ±`delta_percent`, пересчёт выполняется через ту же функцию `calculate_metrics`.

### 6.3. Доступ к JSON-хранилищу

Расположение файла определяется в `core.config.settings`:

```python
settings.DATA_DIR      ## каталог data/
settings.SCENARIOS_FILE  ## файл data/scenarios.json
```

Базовые функции:

* `_load_scenarios_raw()` — чтение списка словарей из JSON.
* `_save_scenarios_raw(items)` — сохранение списка в JSON.
* `list_scenarios()` — возвращает `List[ScenarioShort]`.
* `get_scenario(id)` — возвращает `ScenarioDetail | None`.
* `save_scenario(scenario)` — создаёт/обновляет сценарий (UUID, created_at/updated_at).

---

## 7. Поток обработки запроса (Request Flow)

На примере `/api/v1/calc`:

1. Клиент отправляет `POST /api/v1/calc` с JSON-телом.
2. FastAPI:

   * маппит тело запроса на модель `InvestInput`,
   * выполняет базовую валидацию типов/ограничений Pydantic.
3. Функция `calculate_invest_metrics` получает объект `InvestInput`.
4. Функция вызывает `services.invest_service.calculate_metrics`:

   * выполняются бизнес-проверки;
   * считается `TCO`, `ROI`, `Payback`.
   * формируется `InvestResult`.
5. Результат возвращается в эндпоинт.
6. FastAPI сериализует `InvestResult` в JSON согласно `response_model`.
7. Клиент получает структурированный ответ и описание в Swagger.

---

## 8. Обработка ошибок

Уровень API:

* Используется `HTTPException` из FastAPI.
* Бизнес-ошибки (`ValueError`) ловятся в контроллерах и переводятся в:

  * `422 Unprocessable Entity` с текстом ошибки.
* Ошибки файловой системы при работе с JSON:

  * перехватываются как `OSError`,
  * трансформируются в `500 Internal Server Error` (`"Failed to save scenario: ..."`).
* Ошибка "сценарий не найден" → `404 Not Found`.

Уровень моделей:

* Pydantic автоматически генерирует ошибки валидации (`422`) при неправильных типах, отсутствии обязательных полей и нарушении ограничений (`ge`, `gt`, `le`).

---

## 9. Версионирование API

Текущее версия API:

* Префикс маршрутов: `/api/v1`.
* Основной роутер: `api.v1.routes_invest`.

При добавлении новых версий:

```text
src/api/
├── v1/
│   └── routes_invest.py
└── v2/
    └── routes_invest.py   ## изменённый контракт
```

* `main.py` подключает оба роутера с разными префиксами (`/api/v1`, `/api/v2`).
* Параллельная поддержка версий позволяет безопасно изменять контракты.

Подробнее — см. `docs/05-api/api-versioning.md`.

---

## 10. Тестирование внутреннего API

Тесты для API находятся в `tests/test_api.py` и используют `TestClient` FastAPI:

* `test_api_calc_basic` — проверка `/api/v1/calc`.
* `test_api_sensitivity_basic` — проверка `/api/v1/sensitivity`.
* `test_api_scenarios_crud_with_temp_storage` — проверка сценариев с временным JSON-хранилищем (подмена путей через `monkeypatch`).

Тесты бизнес-логики анализируют:

* корректность расчётов (`test_service.py`),
* поведение анализа чувствительности (`test_sensitivity.py`).

---

## 11. Рекомендации по расширению

При добавлении новых функций в API:

1. **Сначала** описать бизнес-логика в `services/`.
2. **Затем** добавить модели в `models/invest.py` (или новый модуль).
3. **После этого** создать эндпоинт в `api/v1/routes_invest.py`.
4. Обновить документацию:

   * `docs/05-api/endpoints-invest.md`,
   * при необходимости — ADR.
5. Добавить автотесты:

   * юнит-тесты сервисов,
   * интеграционные тесты API.

Так сохраняется чистое разделение слоёв и устойчивость архитектуры.


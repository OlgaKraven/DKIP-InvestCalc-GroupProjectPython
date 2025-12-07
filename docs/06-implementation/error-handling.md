# Обработка ошибок (Error Handling)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает, **как в InvestCalc обрабатываются ошибки**:

- на уровне входных данных (валидация Pydantic),
- в бизнес-логике (расчёты и сценарии),
- на уровне HTTP-API (FastAPI / HTTP-коды),
- при работе с файловой системой (JSON-хранилище).

Цель: обеспечить предсказуемое поведение сервиса и единый подход к генерации и отображению ошибок.

---

## 2. Уровни обработки ошибок

Обработка ошибок реализована в три слоя:

1. **Модели** (`src/models/invest.py`)  
   → Pydantic-валидация структуры и типов.

2. **Бизнес-логика** (`src/services/invest_service.py`)  
   → проверки бизнес-правил, выброс `ValueError`.

3. **HTTP-слой** (`src/api/v1/routes_invest.py`)  
   → маппинг ошибок на HTTP-коды через `HTTPException`.

Дополнительно:

- Ошибки файловой системы (`OSError`) оборачиваются в `HTTP 500`.
- Нестандартные/неизвестные ошибки по умолчанию обрабатываются FastAPI как `HTTP 500`.

---

## 3. Ошибки валидации моделей (Pydantic)

Все входные и выходные данные описаны Pydantic-моделями:

- `InvestInput`, `InvestResult`,
- `SensitivityRequest`, `SensitivityResult`, `SensitivityItem`,
- `ScenarioShort`, `ScenarioDetail`.

При получении HTTP-запроса FastAPI:

1. Преобразует JSON-тело запроса в модель (например, `InvestInput`).
2. Выполняет валидацию:
   - обязательные поля,
   - типы (`float`, `int`, `str`),
   - ограничения (если заданы через `Field` и т.п.).
3. При любой ошибке валидации формируется стандартный ответ:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "ошибка валидации",
      "type": "value_error"
    }
  ]
}
```

HTTP-код: **422 Unprocessable Entity**.

**Важно:** эта валидация выполняется **до** вызова бизнес-логики.

---

## 4. Ошибки бизнес-логики

Бизнес-логика реализована в `services/invest_service.py`.
Основной публичный интерфейс:

* `calculate_metrics(input_data: InvestInput) -> InvestResult`
* `run_sensitivity(request: SensitivityRequest) -> SensitivityResult`
* `list_scenarios()`, `get_scenario()`, `save_scenario()`

## 4.1. Типичные бизнес-проверки

```python
if input_data.capex < 0 or input_data.opex < 0 or input_data.effects < 0:
    raise ValueError("CAPEX, OPEX и эффекты не могут быть отрицательными.")

if input_data.period_months <= 0:
    raise ValueError("Период анализа (period_months) должен быть больше нуля.")
```

```python
if request.delta_percent <= 0:
    raise ValueError("delta_percent должен быть больше 0.")

if not request.parameters:
    raise ValueError("Не указан ни один параметр для анализа чувствительности.")
```

Если бизнес-правило нарушено, выбрасывается **`ValueError`** с осмысленным текстом.

HTTP-слой перехватывает `ValueError` и конвертирует в **HTTP 422**.

---

## 5. Обработка ошибок в HTTP-слое

Все эндпоинты реализованы в `src/api/v1/routes_invest.py` и используют `HTTPException`:

```python
from fastapi import HTTPException, status
```

### 5.1. Ошибки бизнес-логики (`ValueError` → 422)

Пример для `/calc`:

```python
@router.post("/calc", response_model=InvestResult, ...)
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

Пример для `/sensitivity` аналогичен.

**Поведение:**

* Любая `ValueError` из бизнес-логики → **422** с сообщением из исключения.
* Формат ответа:

```json
{
  "detail": "CAPEX, OPEX и эффекты не могут быть отрицательными."
}
```

---

### 5.2. Ошибки “ресурс не найден” (`404 Not Found`)

Для сценариев:

```python
@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetail, ...)
async def get_scenario_by_id(scenario_id: str) -> ScenarioDetail:
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id={scenario_id} not found",
        )
    return scenario
```

Формат ответа:

```json
{
  "detail": "Scenario with id=... not found"
}
```

---

### 5.3. Ошибки файловой системы (`OSError` → 500)

При сохранении сценария:

```python
@router.post("/scenarios", response_model=ScenarioDetail, status_code=status.HTTP_201_CREATED)
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

Используется, если:

* нет доступа к файлу `scenarios.json`,
* нет прав на запись,
* произошла другая ошибка ввода-вывода.

---

## 6. Коды ответов и их семантика

| HTTP-код                      | Где используется                                     | Значение                                              |
| ----------------------------- | ---------------------------------------------------- | ----------------------------------------------------- |
| **200 OK**                    | Успешные GET/POST (расчёты, чувствительность)        | Операция выполнена успешно                            |
| **201 Created**               | `POST /api/v1/scenarios`                             | Сценарий успешно создан/обновлён                      |
| **404 Not Found**             | `GET /api/v1/scenarios/{id}` при отсутствии сценария | Ресурс не найден                                      |
| **422 Unprocessable Entity**  | Ошибки Pydantic и бизнес-валидации                   | Некорректные входные данные / нарушение бизнес-правил |
| **500 Internal Server Error** | Ошибки файловой системы, неожиданные исключения      | Внутренняя ошибка сервера                             |

---

## 7. Формат ошибок для клиентов

### 7.1. Ошибки Pydantic (структура/типы)

```json
{
  "detail": [
    {
      "loc": ["body", "capex"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

### 7.2. Ошибки бизнес-логики

```json
{
  "detail": "Период анализа (period_months) должен быть больше нуля."
}
```

## 7.3. Ошибка сценария (404)

```json
{
  "detail": "Scenario with id=123 not found"
}
```

### 7.4. Ошибка записи файла (500)

```json
{
  "detail": "Failed to save scenario: [Errno 13] Permission denied: 'scenarios.json'"
}
```

---

## 8. Тестирование обработки ошибок

**Юнит-тесты** в `tests/test_service.py` и `tests/test_sensitivity.py`:

* проверяют, что при некорректных данных (`period_months <= 0`, отрицательные значения, пустой список параметров) функция `calculate_metrics` / `run_sensitivity` выбрасывает `ValueError`.

**Интеграционные тесты API** в `tests/test_api.py`:

* `test_api_calc_invalid_input` → отправка некорректного запроса (`period_months = 0`) приводит к `422`;
* тесты сценариев проверяют поведение `404` (не найден сценарий) и работу временного JSON-хранилища.

---

## 9. Рекомендации по добавлению новых ошибок

При добавлении новых функций в API:

1. **В бизнес-логике**:

   * проверять бизнес-правила,
   * выбрасывать `ValueError` с понятным сообщением, если правило нарушено.

2. **В HTTP-слое**:

   * перехватывать `ValueError` и переводить в `HTTP 422`,
   * использовать `HTTP 404` для отсутствующих ресурсов,
   * `HTTP 400` — для ошибок формата запроса (если не покрыто Pydantic),
   * `HTTP 500` — только для неожиданных ошибок или проблем инфраструктуры.

3. **В документации**:

   * обновить `docs/05-api/errors-and-status-codes.md`,
   * при необходимости — ADR по стратегии ошибок.

---

## 10. Связанные документы

* `docs/05-api/errors-and-status-codes.md` — публичное описание ошибок API
* `docs/06-implementation/validation.md` — (при наличии) подробности валидации
* `docs/06-implementation/api-internal.md` — внутреннее устройство API
* `docs/06-implementation/business-logic.md` — бизнес-логика расчётов
* `docs/06-implementation/data-access.md` — доступ к данным
 
 
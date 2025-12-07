# Логирование (Logging)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия документа: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает подход к **логированию** в проекте InvestCalc:

- какие типы событий логируются;
- на каком уровне (uvicorn, FastAPI, бизнес-логика);
- как настроен формат логов;
- какие есть рекомендации для дальнейшего развития.

Текущее решение ориентировано на учебный проект, но построено так, чтобы его можно было расширить до продакшн-уровня.

---

## 2. Уровни логирования в проекте

В проекте используется несколько уровней логов:

1. **Uvicorn / серверные логи**
   - старт/остановка приложения,
   - ошибки запуска,
   - access-логи (по желанию).

2. **FastAPI / middleware-уровень**
   - стандартные HTTP-ошибки/трейсбеки.

3. **Прикладное логирование (Application / Business)**
   - логирование ключевых событий в бизнес-логике и доступе к данным (по мере необходимости).

На данный момент акцент сделан на:

- понятной отладке в процессе разработки,
- отсутствии чрезмерного шума в логах,
- возможности быстро увидеть ошибки.

---

## 3. Базовая конфигурация логирования

### 3.1. Логгер приложения

Рекомендуемый шаблон (может быть размещён, например, в `src/core/logging.py` или в `main.py`):

```python
import logging

logger = logging.getLogger("investcalc")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

**Принципы:**

* один именованный логгер `"investcalc"` для всего приложения;
* формат: `время | уровень | имя логгера | сообщение`;
* уровень по умолчанию — **INFO** для учебного проекта.

Далее этот логгер может использоваться во всех слоях:

```python
from src.core.logging import logger

logger.info("Scenario saved: %s", scenario.id)
logger.error("Failed to read scenarios.json: %s", exc)
```

---

## 4. Логирование на уровне сервера (Uvicorn)

При запуске приложения через uvicorn (локально или в Docker):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

Uvicorn по умолчанию ведёт:

* **access-логи** (метод, путь, статус, время обработки);
* **error-логи** (traceback при необработанных исключениях).

Для учебного окружения этого достаточно, чтобы:

* видеть все входящие запросы,
* отслеживать ошибки 5xx.

---

## 5. Логирование в бизнес-логике

В модуле `src/services/invest_service.py` логирование рекомендуется включать в **ключевых точках**:

### 5.1. Расчёты

Пример:

```python
from src.core.logging import logger

def calculate_metrics(input_data: InvestInput) -> InvestResult:
    logger.info(
        "calculate_metrics called: capex=%s, opex=%s, effects=%s, period=%s",
        input_data.capex,
        input_data.opex,
        input_data.effects,
        input_data.period_months,
    )

    ## ... бизнес-логика ...

    logger.info(
        "calculate_metrics result: tco=%s, roi=%s, payback_months=%s",
        result.tco,
        result.roi_percent,
        result.payback_months,
    )
    return result
```

Использование:

* **INFO** — успешные вызовы ключевых функций;
* **DEBUG** (опционально) — детальные вычисления, если понадобится более подробная отладка.

---

### 5.2. Анализ чувствительности

Пример:

```python
def run_sensitivity(request: SensitivityRequest) -> SensitivityResult:
    logger.info(
        "run_sensitivity called: delta_percent=%s, parameters=%s",
        request.delta_percent,
        request.parameters,
    )

    ## ... расчёты ...

    logger.info(
        "run_sensitivity finished: items=%s",
        len(result.items),
    )
    return result
```

---

## 6. Логирование при работе с JSON-хранилищем

В `data-access` слое (функции `_load_scenarios_raw`, `_save_scenarios_raw`, `save_scenario`):

### 6.1. Чтение данных

```python
def _load_scenarios_raw() -> List[dict]:
    _ensure_data_dir()
    if not settings.SCENARIOS_FILE.exists():
        logger.info("scenarios.json not found, returning empty list")
        return []
    try:
        with settings.SCENARIOS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning("scenarios.json has invalid structure, expected list")
            return []
        return data
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse scenarios.json: %s", exc)
        return []
```

### 6.2. Запись данных

```python
def _save_scenarios_raw(items: List[dict]) -> None:
    _ensure_data_dir()
    try:
        with settings.SCENARIOS_FILE.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        logger.info("scenarios.json saved successfully, items=%s", len(items))
    except OSError as exc:
        logger.error("Failed to save scenarios.json: %s", exc)
        raise
```

---

## 7. Логирование ошибок и исключений

### 7.1. Ошибки бизнес-логики

При выбросе `ValueError` в бизнес-логике логирование можно выполнять на уровне **WARNING/ERROR**, если это не ожидаемая ситуация.

Пример:

```python
def calculate_metrics(input_data: InvestInput) -> InvestResult:
    if input_data.period_months <= 0:
        logger.warning(
            "Invalid period_months: %s for project %s",
            input_data.period_months,
            input_data.project_name,
        )
        raise ValueError("Период анализа (period_months) должен быть больше нуля.")
```

### 7.2. HTTP-слой и исключения

HTTP-слой (`routes_invest.py`) обычно:

* преобразует `ValueError` в `HTTP 422`,
* но явного логирования там можно избегать, если всё уже логируется на уровне сервиса.

При желании, в обработчиках можно добавить:

```python
except ValueError as exc:
    logger.info("Business validation error: %s", exc)
    raise HTTPException(...) from exc
```

---

## 8. Логирование в тестовой среде

В юнит-тестах и интеграционных тестах:

* логи по умолчанию могут быть либо отключены, либо оставлены на уровне INFO;
* при необходимости можно использовать `caplog` (pytest) для проверки того, что нужные сообщения логируются.

Пример использования в тестах:

```python
def test_calculate_metrics_logs(caplog):
    with caplog.at_level(logging.INFO, logger="investcalc"):
        result = calculate_metrics(InvestInput(...))
    assert "calculate_metrics called" in caplog.text
```

---

## 9. Рекомендации по развитию логирования

1. **Структурированные логи**
   Использовать JSON-формат логов для последующего анализа (ELK / Loki / etc.).

2. **Корреляция запросов**
   Добавить `request_id` в контекст логов (middleware), чтобы связывать события одного запроса.

3. **Разные уровни для разных окружений**

   * `DEBUG` — в dev-режиме,
   * `INFO` — в тестовом стенде,
   * `WARNING/ERROR` — в продакшн-режиме.

4. **Разделить логгеры по модулям**
   Например:

   * `"investcalc.api"` — для HTTP-слоя,
   * `"investcalc.service"` — для бизнес-логики,
   * `"investcalc.data"` — для доступа к данным.

5. **Интеграция с мониторингом**

   * Метрики по количеству ошибок,
   * алёрты по ERROR-логам.

---

## 10. Связанные документы

* `docs/06-implementation/api-internal.md` — внутренняя архитектура API
* `docs/06-implementation/business-logic.md` — бизнес-логика расчётов
* `docs/06-implementation/data-access.md` — доступ к данным (JSON)
* `docs/06-implementation/error-handling.md` — обработка ошибок
 

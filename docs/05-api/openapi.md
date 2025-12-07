# OpenAPI Specification — InvestCalc API

Документ описывает **структуру OpenAPI 3.0**, используемую для автоматической генерации Swagger UI и клиентских SDK.

InvestCalc предоставляет REST API для:

- расчёта экономических показателей (TCO/ROI/Payback),
- анализа чувствительности,
- управления сценариями, хранящимися в JSON-файлах.

Swagger доступен по адресу:

```

/docs

```

---

## 1. Общая информация об API

```yaml
openapi: 3.0.3
info:
  title: InvestCalc API
  version: "1.0"
  description: >
    REST API для расчёта показателей экономической эффективности ИС.
    Поддерживает:
      - TCO
      - ROI
      - период окупаемости
      - анализ чувствительности
      - работу со сценариями (JSON-хранилище)
servers:
  - url: http://localhost:8000
    description: Local Development
```

---

## 2. Модели данных (schemas)

### 2.1 `InvestInput`

```yaml
InvestInput:
  type: object
  required: [project_name, capex, opex, effects, period_months]
  properties:
    project_name:
      type: string
    capex:
      type: number
      minimum: 0
    opex:
      type: number
      minimum: 0
    effects:
      type: number
      minimum: 0
    period_months:
      type: integer
      minimum: 1
```

---

### 2.2 `InvestResult`

```yaml
InvestResult:
  type: object
  properties:
    tco:
      type: number
    roi:
      type: number
    payback_months:
      type: number
      nullable: true
    payback_years:
      type: number
      nullable: true
    note:
      type: string
      nullable: true
```

---

### 2.3 `SensitivityRequest`

```yaml
SensitivityRequest:
  type: object
  required: [base_input, parameters, delta_percent]
  properties:
    base_input:
      $ref: "##/components/schemas/InvestInput"
    parameters:
      type: array
      items:
        type: string
    delta_percent:
      type: number
      minimum: 0
```

---

### 2.4 `ScenarioItem` (для списка сценариев)

```yaml
ScenarioItem:
  type: object
  properties:
    id:
      type: string
    name:
      type: string
    last_result:
      $ref: "##/components/schemas/InvestResult"
```

---

### 2.5 `ScenarioDetail`

```yaml
ScenarioDetail:
  type: object
  required: [name, description, input]
  properties:
    id:
      type: string
    name:
      type: string
    description:
      type: string
    input:
      $ref: "##/components/schemas/InvestInput"
    last_result:
      $ref: "##/components/schemas/InvestResult"
      nullable: true
```

---

## 3. Эндпоинты API

Ниже приведена OpenAPI-структура основных методов.

---

### 3.1. POST `/api/v1/calc`

```yaml
post:
  summary: Calculate TCO, ROI and Payback
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: "##/components/schemas/InvestInput"
  responses:
    "200":
      description: Calculation successful
      content:
        application/json:
          schema:
            $ref: "##/components/schemas/InvestResult"
    "422":
      description: Validation error
```

---

### 3.2. POST `/api/v1/sensitivity`

```yaml
post:
  summary: Perform sensitivity analysis on input parameters
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: "##/components/schemas/SensitivityRequest"
  responses:
    "200":
      description: Sensitivity analysis result
    "422":
      description: Validation error
```

---

### 3.3. GET `/api/v1/scenarios`

```yaml
get:
  summary: Get list of saved scenarios
  responses:
    "200":
      description: List of scenarios
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: "##/components/schemas/ScenarioItem"
```

---

### 3.4. GET `/api/v1/scenarios/{scenario_id}`

```yaml
get:
  summary: Get full scenario details
  parameters:
    - name: scenario_id
      in: path
      required: true
      schema:
        type: string
  responses:
    "200":
      description: Scenario detail
      content:
        application/json:
          schema:
            $ref: "##/components/schemas/ScenarioDetail"
    "404":
      description: Scenario not found
```

---

### 3.5. POST `/api/v1/scenarios`

```yaml
post:
  summary: Create or update scenario
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: "##/components/schemas/ScenarioDetail"
  responses:
    "201":
      description: Scenario created
    "200":
      description: Scenario updated
    "422":
      description: Validation error
```

---

### 3.6. DELETE `/api/v1/scenarios/{scenario_id}`

```yaml
delete:
  summary: Delete scenario by ID
  parameters:
    - name: scenario_id
      in: path
      schema:
        type: string
      required: true
  responses:
    "200":
      description: Scenario deleted
    "404":
      description: Scenario not found
```

---

## 4. Ошибки API

Документированы в:

```
errors-and-status-codes.md
```

Стандартные ошибки:

| Код | Причина                                   |
| --- | ----------------------------------------- |
| 422 | Ошибка валидации Pydantic / бизнес-логики |
| 404 | Сценарий не найден                        |
| 500 | Ошибка файловой системы / внутренний сбой |

---

## 5. Версионирование API

См. файл:

```
api-versioning.md
```

Текущая версия: **v1**.

Все маршруты начинаются с:

```
/api/v1/
```

---

## 6. Генерация OpenAPI

Используется встроенная схема FastAPI:

```
/openapi.json
/docs
/redoc
```

Чтобы получить JSON:

```
GET http://localhost:8000/openapi.json
```

---

## 7. Связанные документы

* `api-overview.md`
* `api-versioning.md`
* `endpoints-invest.md`
* `errors-and-status-codes.md`
* `../03-architecture/adr-15-openapi-documentation-strategy.md`

 
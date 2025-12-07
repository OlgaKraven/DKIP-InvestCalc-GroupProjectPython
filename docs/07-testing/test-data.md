# Тестовые данные (Test Data)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает **наборы тестовых данных**, используемых при проверке:

- расчёта показателей (TCO, ROI, Payback),
- анализа чувствительности,
- операций со сценариями,
- обработки ошибок,
- граничных условий.

Цель: обеспечить **повторяемость** и **стандартизацию** тестирования.

---

## 2. Форматы тестовых данных

### 2.1. JSON-запросы для API
- Используются для тестирования через Postman, Swagger или автотесты.
- В большинстве случаев соответствуют моделям:
  - `InvestInput`
  - `SensitivityRequest`
  - `ScenarioDetail`

### 2.2. JSON-файл сценариев (`scenarios.json`)
Используется для тестирования работы подсистемы данных.

### 2.3. Табличные данные
Используются в документации и ручном тестировании (Excel/Google Sheets).

---

## 3. Базовые тестовые данные для `/calc`

### 3.1. Валидный минимальный кейс

```json
{
  "project_name": "Test Minimal",
  "capex": 0,
  "opex": 0,
  "effects": 0,
  "period_months": 1
}
```

Ожидаемое:

* TCO = 0
* ROI = 0
* Payback = нет окупаемости (note меняется согласно логике)

---

### 3.2. Базовый валидный кейс

```json
{
  "project_name": "Base Valid",
  "capex": 100000,
  "opex": 20000,
  "effects": 150000,
  "period_months": 36
}
```

Ожидаемое:

* TCO = 120000
* ROI = 25.00
* PaybackMonths ≈ `(100000 / ((150000/36) - (20000/36))) ≈ 28.8`

---

### 3.3. Некорректные данные — отрицательные значения

```json
{
  "project_name": "Negative Input",
  "capex": -10,
  "opex": 0,
  "effects": 0,
  "period_months": 12
}
```

Ожидаемое:

```
422 Unprocessable Entity
"CAPEX, OPEX и эффекты не могут быть отрицательными."
```

---

### 3.4. Некорректные данные — нулевой период

```json
{
  "project_name": "Zero Period",
  "capex": 1000,
  "opex": 500,
  "effects": 2000,
  "period_months": 0
}
```

Ожидаемое:

```
422
"Период анализа (period_months) должен быть больше нуля."
```

---

## 4. Тестовые данные для анализа чувствительности (`/sensitivity`)

### 4.1. Валидный кейс

```json
{
  "base_input": {
    "project_name": "Sensitivity Demo",
    "capex": 100000,
    "opex": 30000,
    "effects": 180000,
    "period_months": 36
  },
  "parameters": ["capex", "opex", "effects"],
  "delta_percent": 20
}
```

Ожидаемое:

* результат يحتوي `base_result`
* для каждого параметра есть:

  * `minus_delta_result`
  * `plus_delta_result`
* структура полностью валидна.

---

### 4.2. Ошибка — пустой список параметров

```json
{
  "base_input": {
    "project_name": "Invalid Sensitivity",
    "capex": 1000,
    "opex": 1000,
    "effects": 2000,
    "period_months": 12
  },
  "parameters": [],
  "delta_percent": 20
}
```

Ожидаемое:

```
422
"Не указан ни один параметр для анализа чувствительности."
```

---

### 4.3. Ошибка — delta_percent <= 0

```json
{
  "base_input": {
    "project_name": "Wrong Delta",
    "capex": 1000,
    "opex": 500,
    "effects": 2000,
    "period_months": 12
  },
  "parameters": ["capex"],
  "delta_percent": 0
}
```

Ожидаемое:

```
422
"delta_percent должен быть больше 0."
```

---

## 5. Тестовые данные для сценариев (`/scenarios`)

### 5.1. Валидный сценарий (POST)

```json
{
  "id": "",
  "name": "Scenario 1",
  "description": "Первый тестовый сценарий",
  "input": {
    "project_name": "CRM Implementation",
    "capex": 120000,
    "opex": 30000,
    "effects": 200000,
    "period_months": 36
  },
  "last_result": null
}
```

Ожидаемое:

* Создаётся новый сценарий (id генерируется)
* Возвращается `201 Created`

---

### 5.2. Некорректный сценарий

```json
{
  "id": "abc",
  "name": "Broken Scenario",
  "description": "invalid",
  "input": {
    "project_name": "Test",
    "capex": -100,
    "opex": 1000,
    "effects": 1000,
    "period_months": 12
  },
  "last_result": null
}
```

Ожидаемое:

```
422
"CAPEX, OPEX и эффекты не могут быть отрицательными."
```

---

## 6. Тестовые данные для нагрузки (необязательно для учебного проекта)

### 6.1. Пакет данных для 1000 последовательных вызовов `/calc`

```json
{
  "project_name": "Load Test",
  "capex": 100000,
  "opex": 50000,
  "effects": 200000,
  "period_months": 60
}
```

Используется для тестирования:

* производительности,
* стабильности расчётов,
* обработки однотипных запросов.

---

## 7. Данные для негативного тестирования

### 7.1. Неверные типы

```json
{
  "capex": "string",
  "opex": 100,
  "effects": 100,
  "period_months": 12
}
```

Результат: **422**, ошибка Pydantic.

---

### 7.2. Повреждённый JSON для сценариев

Пример содержимого `scenarios.json`:

```
{ broken json [
```

Ожидаемое:

* `_load_scenarios_raw()` → empty list
* лог: `"Failed to parse scenarios.json"`
* корректная работа API

---

### 7.3. Превышение разумных значений

```json
{
  "capex": 1000000000000,
  "opex": 10,
  "effects": 10,
  "period_months": 12
}
```

Ожидаемое:

* расчёт выполняется,
* но тест-кейс используется для проверки устойчивости и переполнения.

---

## 8. Пример тестовых наборов для ручного тестирования (таблица)

| ID  | Цель               | CAPEX  | OPEX  | Effects | Period | Ожидание                  |
| --- | ------------------ | ------ | ----- | ------- | ------ | ------------------------- |
| T01 | Минимальный        | 0      | 0     | 0       | 1      | ROI=0, Payback=None       |
| T02 | Базовый            | 100000 | 20000 | 150000  | 36     | ROI=25%                   |
| T03 | Отрицательные      | -1     | 0     | 0       | 12     | Ошибка                    |
| T04 | Нулевой период     | 1000   | 1000  | 2000    | 0      | Ошибка                    |
| T05 | Большой эффект     | 0      | 1000  | 100000  | 12     | ROI высокий               |
| T06 | Payback невозможен | 100000 | 50000 | 50000   | 24     | note: проект не окупается |

---

## 9. Связанные документы

* `test-cases.md`
* `test-plan.md`
* `test-strategy.md`
* `regression-checklist.md`
* `bug-report-samples.md`
* `../06-implementation/validation.md`
* `../06-implementation/business-logic.md`

 
# Sequence Diagrams — Диаграммы последовательностей InvestCalc

Документ содержит UML-диаграммы последовательностей (в формате Mermaid) для основных сценариев использования системы InvestCalc:

- UC-1 — Базовый расчёт (Calculate)
- UC-2 — Анализ чувствительности (Sensitivity)
- UC-3 — Сравнение сценариев (Compare)
- UC-4 — Формирование отчёта (Report)

Диаграммы показывают, **как взаимодействуют** пользователь, API, сервисный слой, модели и данные.

---

## 1. UC-1 — Выполнить базовый расчёт (Calculate)

**Описание:**  
Пользователь (или внешняя система) отправляет входные данные (CAPEX, OPEX, Period, Effect), а система возвращает рассчитанные TCO, ROI, Payback и флаг `is_profitable`.

### 1.1. Диаграмма последовательностей (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Client
    participant API as FastAPI API<br/>/api/v1/calculate
    participant M as Pydantic Models<br/>InvestmentInput / CalcResult
    participant S as Service Layer<br/>invest_service
    participant D as Data (none/JSON only)

    U->>API: 1. POST /api/v1/calculate {capex, opex, period, effect}
    API->>M: 2. Валидация входных данных (InvestmentInput)
    M-->>API: 3. Валидная модель или ошибка
    alt Данные некорректны
        API-->>U: 4. HTTP 400 / 422 + details
    else Данные корректны
        API->>S: 4. calculate_all(input_model)
        S->>S: 5. calculate_tco()
        S->>S: 6. calculate_roi()
        S->>S: 7. calculate_payback()
        S->>M: 8. Формирование CalcResult
        M-->>S: 9. Объект результата
        S-->>API: 10. CalcResult
        API-->>U: 11. HTTP 200 + JSON {tco, roi, payback, is_profitable}
    end
```

---

## 2. UC-2 — Анализ чувствительности (Sensitivity Analysis)

**Описание:**
Пользователь задаёт базовые входные данные, система автоматически варьирует параметры (по умолчанию CAPEX/OPEX ±20%) и возвращает матрицу результатов.

### 2.1. Диаграмма последовательностей (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Client
    participant API as FastAPI API<br/>/api/v1/sensitivity
    participant M as Pydantic Models<br/>InvestmentInput / SensitivityResult
    participant S as Service Layer<br/>invest_service
    participant D as Data (in-memory only)

    U->>API: 1. POST /api/v1/sensitivity {capex, opex, period, effect}
    API->>M: 2. Валидация входных данных (InvestmentInput)
    M-->>API: 3. Валидная модель или ошибка
    alt Данные некорректны
        API-->>U: 4. HTTP 400 / 422 + details
    else Данные корректны
        API->>S: 4. sensitivity_analysis(input_model)
        S->>S: 5. Генерация вариаций параметров (80%, 100%, 120%)
        loop Для каждой вариации
            S->>S: 6. Расчёт TCO/ROI/Payback (reuse calculate_all)
        end
        S->>M: 7. Формирование SensitivityResult (matrix)
        M-->>S: 8. Объект результата
        S-->>API: 9. SensitivityResult
        API-->>U: 10. HTTP 200 + JSON (матрица чувствительности)
    end
```

---

## 3. UC-3 — Сравнение сценариев (Compare Scenarios)

**Описание:**
Система сравнивает два сценария (обычно локальный и облачный), выполняет расчёты по каждому и возвращает сравнительный результат с рекомендацией.

### 3.1. Диаграмма последовательностей (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Client
    participant API as FastAPI API<br/>/api/v1/compare
    participant S as Service Layer<br/>invest_service
    participant M as Pydantic Models<br/>InvestmentInput / CalcResult
    participant F as File Loader<br/>data/*.json

    U->>API: 1. GET /api/v1/compare?local=...&cloud=...
    API->>S: 2. compare_scenarios(local_path, cloud_path)

    S->>F: 3. Загрузка local-сценария (JSON)
    F-->>S: 4. JSON local-сценария
    S->>M: 5. Валидация → InvestmentInput (local)
    M-->>S: 6. Валидация ОК

    S->>F: 7. Загрузка cloud-сценария (JSON)
    F-->>S: 8. JSON cloud-сценария
    S->>M: 9. Валидация → InvestmentInput (cloud)
    M-->>S: 10. Валидация ОК

    S->>S: 11. Расчёт по local (calculate_all)
    S->>S: 12. Расчёт по cloud (calculate_all)
    S->>S: 13. Сравнение метрик (ROI, TCO, Payback)
    S->>M: 14. Формирование результата сравнения (ComparisonResult)
    M-->>S: 15. Объект результата

    S-->>API: 16. ComparisonResult
    API-->>U: 17. HTTP 200 + JSON {local, cloud, recommended, justification}
```

---

## 4. UC-4 — Формирование отчёта (Generate Report)

**Описание:**
Система формирует HTML-отчёт (и в перспективе PDF) на основе результатов расчётов, анализа чувствительности и сравнения сценариев.

### 4.1. Диаграмма последовательностей (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Client (Browser)
    participant API as FastAPI API<br/>/api/v1/report
    participant S as Service Layer<br/>invest_service
    participant R as Report Service<br/>report_service
    participant T as Templates<br/>report_template.html
    participant D as Data Sources<br/>data/*.json

    U->>API: 1. GET /api/v1/report
    API->>S: 2. Получить базовые данные и сценарии
    S->>D: 3. Загрузка сценариев (local/cloud JSON)
    D-->>S: 4. Данные сценариев
    S->>S: 5. Выполнить расчёты (calculate_all)
    S->>S: 6. Выполнить анализ чувствительности
    S-->>API: 7. AggregatedResults (calc + sensitivity + compare)

    API->>R: 8. generate_html_report(AggregatedResults)
    R->>T: 9. Подстановка данных в шаблон report_template.html
    T-->>R: 10. HTML-контент отчёта
    R-->>API: 11. HTML (готовый отчёт)
    API-->>U: 12. HTTP 200 + text/html (страница отчёта)
```

---

## 5. Использование диаграмм при разработке и защите проекта

Диаграммы последовательностей:

* демонстрируют понимание **взаимодействия компонентов**;
* помогают студентам реализовать и отлаживать код;
* служат связующим звеном между:

  * Use Case-описанием (`use-cases.md`),
  * архитектурой (`c4-*.md`, ADR),
  * реализацией (слои `api/`, `services/`, `models/`).

На защите проекта:

* можно использовать этот документ для пояснения логики работы системы;
* легко показать, как запрос «проходит» через все уровни.


# ER Diagram — ER-диаграмма данных InvestCalc

Документ описывает **логическую модель данных** в виде ER-диаграммы.  
Она отражает потенциальную структуру БД (для расширенной версии проекта) и основывается на предметной модели (`domain-model.md`).

---

## 1. Сущности и связи (обзор)

Основные сущности:

- `SCENARIO` — сценарий инвестиций;
- `CALC_RESULT` — результат расчёта по сценарию;
- `SENSITIVITY_RUN` — запуск анализа чувствительности;
- `SENSITIVITY_POINT` — точка чувствительности;
- `COMPARISON` — сравнение двух сценариев;
- `REPORT` — (опционально) сохранённый отчёт.

Связи:

- один `SCENARIO` → один `CALC_RESULT`;
- один `SCENARIO` → множество `SENSITIVITY_RUN`;
- один `SENSITIVITY_RUN` → три `SENSITIVITY_POINT` (low/base/high);
- один `COMPARISON` → два `SCENARIO` и два `CALC_RESULT`;
- `REPORT` может ссылаться либо на `SCENARIO`, либо на `COMPARISON`.

---

## 2. ER-диаграмма (Mermaid erDiagram)

```mermaid
erDiagram

    SCENARIO {
        int        id PK
        string     name
        string     description
        float      capex
        float      opex
        int        period
        float      effect
        datetime   created_at
        string     source
    }

    CALC_RESULT {
        int        id PK
        int        scenario_id FK
        float      tco
        float      roi
        float      payback
        boolean    is_profitable
    }

    SENSITIVITY_RUN {
        int        id PK
        int        scenario_id FK
        string     parameter
        float      base_value
        float      delta_percent
    }

    SENSITIVITY_POINT {
        int        id PK
        int        run_id FK
        string     variant
        float      value
        float      tco
        float      roi
        float      payback
        boolean    is_profitable
    }

    COMPARISON {
        int        id PK
        int        left_scenario_id FK
        int        right_scenario_id FK
        int        left_result_id FK
        int        right_result_id FK
        string     recommended
        string     justification
    }

    REPORT {
        int        id PK
        int        scenario_id FK
        int        comparison_id FK
        text       payload_json
        datetime   created_at
    }

    SCENARIO ||--o| CALC_RESULT : "has result"
    SCENARIO ||--o{ SENSITIVITY_RUN : "has many runs"
    SENSITIVITY_RUN ||--|{ SENSITIVITY_POINT : "has variants"
    COMPARISON }o--|| SCENARIO : "left scenario"
    COMPARISON }o--|| SCENARIO : "right scenario"
    COMPARISON }o--|| CALC_RESULT : "left result"
    COMPARISON }o--|| CALC_RESULT : "right result"
    REPORT }o--|| SCENARIO : "based on scenario"
    REPORT }o--|| COMPARISON : "or comparison"
```

---

## 3. Нормализация и ключи

### 3.1. Нормальные формы

* Данные структурированы минимум в **3НФ**:

  * каждый факт хранится один раз;
  * нет повторяющихся групп полей;
  * нет транзитивных зависимостей вне ключей.

### 3.2. Первичные и внешние ключи

* Все `id` — первичные ключи (PK).
* `scenario_id`, `run_id`, `left_scenario_id` и т.п. — внешние ключи (FK).
* При физической реализации в SQL для FK задаются ограничения `FOREIGN KEY`.

---

## 4. Связь ER-модели с JSON-файлами

В базовой (учебной) версии:

* JSON-файлы `data/input-local.json`, `data/input-cloud.json` реализуют **упрощённый поднабор сущности SCENARIO** без `id` и метаданных;
* остальные сущности («результат», «чувствительность», «сравнение») существуют только в оперативной модели и не сохраняются в БД.

При переходе к БД:

* JSON можно рассматривать как «источник» для заполнения таблиц;
* структура таблиц повторяет поля JSON, расширяя их техническими полями (`id`, `created_at`, `source`).

---


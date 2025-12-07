# DB Schema — Проект схемы базы данных InvestCalc

Документ описывает **предлагаемую структуру базы данных** для расширенной версии InvestCalc.  
В базовой версии проекта БД не используется (см. ADR-06, ADR-08), но схема формируется как задел для:

- будущих учебных групп;
- курсовых и дипломных проектов;
- промышленной адаптации системы.

---

## 1. Общие положения

- Тип БД: реляционная (PostgreSQL / SQLite / любая SQL-СУБД).
- Нотация: SQL (DDL).
- Нормализация: минимум до 3НФ.
- Генерация миграций: может выполняться через ORM (например, SQLAlchemy + Alembic).
- Именование:
  - таблицы — snake_case во множественном числе (`scenarios`, `calc_results` и т.п.);
  - поля — snake_case.

---

## 2. Таблица `scenarios`

Хранит инвестиционные сценарии (локальный, облачный и др.).

```sql
CREATE TABLE scenarios (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    description  TEXT,
    capex        NUMERIC(18, 2) NOT NULL CHECK (capex >= 0),
    opex         NUMERIC(18, 2) NOT NULL CHECK (opex >= 0),
    period       INTEGER NOT NULL CHECK (period >= 1),
    effect       NUMERIC(18, 2) NOT NULL CHECK (effect >= 0),
    source       VARCHAR(50) NOT NULL DEFAULT 'manual',  -- 'json' | 'manual' | 'api'
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Назначение полей:**

* `capex`, `opex`, `period`, `effect` — соответствуют требованиям `data-requirements.md` и бизнес-правилам.
* `source` — откуда взят сценарий (файл, ручной ввод, запрос по API).
* `created_at` — время создания записи.

---

## 3. Таблица `calc_results`

Результаты расчётов для сценария.

```sql
CREATE TABLE calc_results (
    id             SERIAL PRIMARY KEY,
    scenario_id    INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    tco            NUMERIC(18, 2) NOT NULL,
    roi            NUMERIC(10, 2) NOT NULL,
    payback        NUMERIC(10, 2),        -- NULL = проект не окупается
    is_profitable  BOOLEAN NOT NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Особенности:**

* `scenario_id` связывает результат с конкретным сценарием.
* `payback` допускает `NULL`, если по бизнес-правилам окупаемость не достигается.
* `is_profitable` дублирует логический вывод (удобно для запросов и фильтрации).

---

## 4. Таблица `sensitivity_runs`

Хранит информацию о запуске анализа чувствительности.

```sql
CREATE TABLE sensitivity_runs (
    id             SERIAL PRIMARY KEY,
    scenario_id    INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    parameter      VARCHAR(50) NOT NULL,         -- 'capex' | 'opex' | 'effect'
    base_value     NUMERIC(18, 2) NOT NULL,
    delta_percent  NUMERIC(5, 2) NOT NULL,      -- обычно 20.00
    created_at     TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Назначение:**

* Описывает один запуск анализа чувствительности по конкретному параметру.
* Содержит базовое значение и процент изменения.

---

## 5. Таблица `sensitivity_points`

Хранит точки (low/base/high) для одного запуска анализа чувствительности.

```sql
CREATE TABLE sensitivity_points (
    id              SERIAL PRIMARY KEY,
    run_id          INTEGER NOT NULL REFERENCES sensitivity_runs(id) ON DELETE CASCADE,
    variant         VARCHAR(10) NOT NULL,      -- 'low' | 'base' | 'high'
    value           NUMERIC(18, 2) NOT NULL,   -- значение изменённого параметра
    tco             NUMERIC(18, 2) NOT NULL,
    roi             NUMERIC(10, 2) NOT NULL,
    payback         NUMERIC(10, 2),
    is_profitable   BOOLEAN NOT NULL
);
```

**Почему так:**

* каждая запись → одна точка чувствительности;
* для каждого запуска (run) будет минимум три записи (`low/base/high`).

---

## 6. Таблица `comparisons`

Результаты сравнения двух сценариев.

```sql
CREATE TABLE comparisons (
    id                SERIAL PRIMARY KEY,
    left_scenario_id  INTEGER NOT NULL REFERENCES scenarios(id),
    right_scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    left_result_id    INTEGER NOT NULL REFERENCES calc_results(id),
    right_result_id   INTEGER NOT NULL REFERENCES calc_results(id),
    recommended       VARCHAR(10) NOT NULL,     -- 'left' | 'right' | 'equal'
    justification     TEXT NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Смысл:**

* хранит информацию о том, какие сценарии сравнивались;
* какие результаты расчётов использовались;
* какое решение рекомендовано (`recommended`) и почему (`justification`).

---

## 7. Таблица `reports` (опционально)

Сохранённые отчёты, которые могут быть позже просмотрены или экспортированы.

```sql
CREATE TABLE reports (
    id              SERIAL PRIMARY KEY,
    scenario_id     INTEGER REFERENCES scenarios(id),
    comparison_id   INTEGER REFERENCES comparisons(id),
    payload_json    JSONB NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Особенности:**

* либо `scenario_id`, либо `comparison_id` (или оба) используются для ссылки на источник данных;
* `payload_json` хранит агрегированные данные: входные параметры, результаты расчётов, чувствительность, текст выводов.

---

## 8. Связи между таблицами

Краткое описание связей:

* `scenarios 1 — N calc_results`
* `scenarios 1 — N sensitivity_runs`
* `sensitivity_runs 1 — N sensitivity_points`
* `comparisons` ссылается на:

  * два сценария (`left_scenario_id`, `right_scenario_id`);
  * два результата (`left_result_id`, `right_result_id`).
* `reports` может ссылаться:

  * на один сценарий;
  * на одно сравнение.

---

## 9. Индексы и производительность (базовый минимум)

Рекомендованные индексы:

```sql
CREATE INDEX idx_calc_results_scenario_id
    ON calc_results (scenario_id);

CREATE INDEX idx_sensitivity_runs_scenario_id
    ON sensitivity_runs (scenario_id);

CREATE INDEX idx_sensitivity_points_run_id
    ON sensitivity_points (run_id);

CREATE INDEX idx_comparisons_scenarios
    ON comparisons (left_scenario_id, right_scenario_id);
```

При необходимости можно добавить индексы по:

* `is_profitable`,
* `recommended`,
* `created_at`.

---

## 10. Соответствие требованиям

Связи с другими документами:

* `data-requirements.md` — структура полей `capex`, `opex`, `period`, `effect` и результатных полей.
* `business-rules.md` — наличие `tco`, `roi`, `payback`, `is_profitable` отражает бизнес-метрики.
* `domain-model.md` и `er-diagram.md` — таблицы и связи напрямую соответствуют предметной модели и ER-модели.
* `requirements-spec.md` — удовлетворяются требования к данным и расширяемости.

---



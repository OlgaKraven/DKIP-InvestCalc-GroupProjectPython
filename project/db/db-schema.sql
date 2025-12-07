-- ==========================================================
--  DB Schema for InvestCalc — учебный проект
--  Хранилище сценариев, входных данных и результатов расчётов
-- ==========================================================

-- Создать базу данных (опционально)
-- CREATE DATABASE investcalc;
-- USE investcalc;

-- ==========================================================
-- Таблица проектов / сценариев
-- ==========================================================

CREATE TABLE scenarios (
    id              CHAR(36) PRIMARY KEY,         -- UUID
    name            VARCHAR(255) NOT NULL,        -- Название сценария
    description     TEXT,                         -- Описание
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_scenarios_name ON scenarios(name);


-- ==========================================================
-- Таблица входных данных (InvestInput)
-- Один сценарий → один набор входных параметров
-- ==========================================================

CREATE TABLE scenario_inputs (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    scenario_id             CHAR(36) NOT NULL,
    project_name            VARCHAR(255) NOT NULL,
    capex                   DECIMAL(18,2) NOT NULL,     -- капитальные затраты
    opex                    DECIMAL(18,2) NOT NULL,     -- операционные затраты
    effects                 DECIMAL(18,2) NOT NULL,     -- экономический эффект
    period_months           INT NOT NULL,               -- период анализа
    discount_rate_percent   DECIMAL(5,2),               -- null = не используется

    CONSTRAINT fk_input_scenario
        FOREIGN KEY (scenario_id)
        REFERENCES scenarios(id)
        ON DELETE CASCADE
);

-- Индексы
CREATE INDEX idx_inputs_scenario_id ON scenario_inputs(scenario_id);


-- ==========================================================
-- Таблица результатов расчётов (InvestResult)
-- Один сценарий → один последний результат
-- ==========================================================

CREATE TABLE scenario_results (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    scenario_id     CHAR(36) NOT NULL,
    tco             DECIMAL(18,2) NOT NULL,  -- Total Cost of Ownership
    roi             DECIMAL(18,2) NOT NULL,  -- ROI %
    payback_months  DECIMAL(10,2) NOT NULL,  -- срок окупаемости, месяцы
    payback_years   DECIMAL(10,2) NOT NULL,  -- срок окупаемости, годы
    note            TEXT,                    -- пояснение

    CONSTRAINT fk_result_scenario
        FOREIGN KEY (scenario_id)
        REFERENCES scenarios(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_results_scenario_id ON scenario_results(scenario_id);


-- ==========================================================
-- Пример данных (опционально)
-- ==========================================================

-- INSERT INTO scenarios (id, name, description)
-- VALUES ('11111111-1111-1111-1111-111111111111', 'Demo Scenario', 'Пример сценария для тестов');


-- INSERT INTO scenario_inputs (scenario_id, project_name, capex, opex, effects, period_months, discount_rate_percent)
-- VALUES ('11111111-1111-1111-1111-111111111111', 'Demo', 100000, 20000, 150000, 36, NULL);


-- INSERT INTO scenario_results (scenario_id, tco, roi, payback_months, payback_years, note)
-- VALUES ('11111111-1111-1111-1111-111111111111', 120000, 25.00, 30.0, 2.5, 'Демо-результат.');

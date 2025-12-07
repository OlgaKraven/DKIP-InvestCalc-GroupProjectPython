## src/services/invest_service.py
"""
Бизнес-логика InvestCalc:
- расчёт экономических показателей (TCO, ROI, Payback);
- анализ чувствительности ±N%;
- работа со сценариями в JSON-файле (без БД).

Этот модуль не зависит от FastAPI и может использоваться
как отдельно, так и в тестах (pytest).
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.core.config import settings
from src.models.invest import (
    InvestInput,
    InvestResult,
    SensitivityRequest,
    SensitivityResult,
    SensitivityItem,
    ScenarioShort,
    ScenarioDetail,
)


## === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ JSON ===============================================


def _ensure_data_dir() -> None:
    """Гарантирует, что каталог для данных существует."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_scenarios_raw() -> List[dict]:
    """
    Считывает сценарии из JSON-файла.

    Формат файла:
    [
        {...сценарий 1...},
        {...сценарий 2...}
    ]
    """
    _ensure_data_dir()
    if not settings.SCENARIOS_FILE.exists():
        return []
    try:
        with settings.SCENARIOS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except json.JSONDecodeError:
        return []


def _save_scenarios_raw(items: List[dict]) -> None:
    """Сохраняет список сценариев в JSON-файл."""
    _ensure_data_dir()
    with settings.SCENARIOS_FILE.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def _now() -> datetime:
    """Текущее время в UTC (без таймзоны)."""
    return datetime.utcnow()


## === РАСЧЁТ ПОКАЗАТЕЛЕЙ =============================================================


def _calculate_tco(input_data: InvestInput) -> float:
    """Простейшая модель TCO: CAPEX + OPEX."""
    return float(input_data.capex + input_data.opex)


def _calculate_roi_percent(input_data: InvestInput, tco: float) -> float:
    """
    Расчёт ROI в процентах.

    Базовая учебная формула:
        ROI = (effects - TCO) / TCO * 100%

    Если TCO == 0:
        - если эффекты > 0 — ROI считаем очень большим (условно бесконечным),
        - если эффекты == 0 — ROI = 0.
    """
    if tco == 0:
        if input_data.effects > 0:
            return 999.99
        return 0.0

    roi = (input_data.effects - tco) / tco * 100.0
    return float(round(roi, 2))


def _calculate_payback(input_data: InvestInput) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Расчёт срока окупаемости (Payback) в месяцах и годах.

    Допущения (учебная модель):
    - затраты: CAPEX (разовый) + OPEX (равномерно по периодам),
    - эффекты: равномерно по period_months,
    - ежемесячный денежный поток = эффект_в_месяц - opex_в_месяц.
    """
    months = input_data.period_months
    if months <= 0:
        return None, None, "Период анализа должен быть больше 0 месяцев."

    monthly_opex = input_data.opex / months
    monthly_effect = input_data.effects / months
    monthly_cash_flow = monthly_effect - monthly_opex

    if monthly_cash_flow <= 0:
        return (
            None,
            None,
            "Проект не окупается в рамках заданного периода: ежемесячный денежный поток ≤ 0.",
        )

    payback_months = input_data.capex / monthly_cash_flow
    payback_years = payback_months / 12.0

    return (
        float(round(payback_months, 2)),
        float(round(payback_years, 2)),
        None,
    )


def calculate_metrics(input_data: InvestInput) -> InvestResult:
    """
    Выполняет полный расчёт экономических показателей по входным данным.

    При некорректных входных данных может выбросить ValueError.
    """
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


## === АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ =========================================================


def _apply_delta(value: float, delta_percent: float, direction: str) -> float:
    """Увеличивает или уменьшает значение на delta_percent процентов."""
    factor = delta_percent / 100.0
    if direction == "minus":
        return float(round(value * (1.0 - factor), 2))
    if direction == "plus":
        return float(round(value * (1.0 + factor), 2))
    raise ValueError("direction must be 'minus' or 'plus'")


def run_sensitivity(request: SensitivityRequest) -> SensitivityResult:
    """
    Выполняет анализ чувствительности для списка параметров.

    Для каждого параметра:
    - рассчитывается базовый результат,
    - рассчитываются результаты при уменьшении и увеличении на delta_percent.
    """
    if request.delta_percent <= 0:
        raise ValueError("delta_percent должен быть больше 0.")
    if not request.parameters:
        raise ValueError("Не указан ни один параметр для анализа чувствительности.")

    base_result = calculate_metrics(request.base_input)
    items: List[SensitivityItem] = []

    base_input_dict = request.base_input.model_dump()

    for param in request.parameters:
        if param not in base_input_dict:
            continue

        ## minus
        minus_input_dict = deepcopy(base_input_dict)
        minus_input_dict[param] = _apply_delta(
            float(base_input_dict[param]),
            request.delta_percent,
            "minus",
        )
        minus_input = InvestInput(**minus_input_dict)
        minus_result = calculate_metrics(minus_input)

        ## plus
        plus_input_dict = deepcopy(base_input_dict)
        plus_input_dict[param] = _apply_delta(
            float(base_input_dict[param]),
            request.delta_percent,
            "plus",
        )
        plus_input = InvestInput(**plus_input_dict)
        plus_result = calculate_metrics(plus_input)

        items.append(
            SensitivityItem(
                parameter=param,
                minus_delta_result=minus_result,
                plus_delta_result=plus_result,
            )
        )

    return SensitivityResult(
        base_result=base_result,
        delta_percent=request.delta_percent,
        items=items,
    )


## === РАБОТА СО СЦЕНАРИЯМИ В JSON ====================================================


def _parse_scenario(item: dict) -> Optional[ScenarioDetail]:
    """Преобразует dict из JSON в ScenarioDetail, при ошибке возвращает None."""
    try:
        return ScenarioDetail.model_validate(item)
    except Exception:
        return None


def list_scenarios() -> List[ScenarioShort]:
    """
    Возвращает список кратких сведений о сценариях.

    Используется в GET /scenarios.
    """
    raw_items = _load_scenarios_raw()
    result: List[ScenarioShort] = []

    for item in raw_items:
        scenario = _parse_scenario(item)
        if scenario is None:
            continue
        result.append(
            ScenarioShort(
                id=scenario.id,
                name=scenario.name,
                created_at=scenario.created_at,
                updated_at=scenario.updated_at,
            )
        )

    result.sort(key=lambda s: (s.updated_at or s.created_at), reverse=True)
    return result


def get_scenario(scenario_id: str) -> Optional[ScenarioDetail]:
    """
    Возвращает сценарий по id или None, если не найден.

    Используется в GET /scenarios/{id}.
    """
    raw_items = _load_scenarios_raw()
    for item in raw_items:
        if item.get("id") == scenario_id:
            return _parse_scenario(item)
    return None


def save_scenario(scenario: ScenarioDetail) -> ScenarioDetail:
    """
    Создаёт новый или обновляет существующий сценарий.

    - если id пустой → генерируется новый UUID;
    - если created_at отсутствует → проставляется текущее время;
    - updated_at всегда обновляется.
    """
    raw_items = _load_scenarios_raw()
    items: List[ScenarioDetail] = []

    for item in raw_items:
        parsed = _parse_scenario(item)
        if parsed is not None:
            items.append(parsed)

    now = _now()

    scenario_id = scenario.id or str(uuid4())
    created_at = scenario.created_at or now
    updated_at = now

    final_scenario = ScenarioDetail(
        id=scenario_id,
        name=scenario.name,
        created_at=created_at,
        updated_at=updated_at,
        description=scenario.description,
        input=scenario.input,
        last_result=scenario.last_result,
    )

    found = False
    for idx, existing in enumerate(items):
        if existing.id == final_scenario.id:
            items[idx] = final_scenario
            found = True
            break

    if not found:
        items.append(final_scenario)

    raw_to_save = [item.model_dump(mode="json") for item in items]
    _save_scenarios_raw(raw_to_save)

    return final_scenario


## === КЛАСС-ОБЁРТКА ДЛЯ ТЕСТОВ И ДРУГИХ СЛОЁВ =======================================


class InvestService:
    """
    Сервисный класс для работы с расчётами и сценариями InvestCalc.

    Оборачивает функции модуля:
    - calculate_metrics(...)
    - run_sensitivity(...)
    - list_scenarios()
    - get_scenario(...)
    - save_scenario(...)
    """

    ## --- Расчёты ---

    def calculate(self, input_data: InvestInput) -> InvestResult:
        """Выполняет расчёт TCO/ROI/Payback по входным данным."""
        return calculate_metrics(input_data)

    def run_sensitivity(self, request: SensitivityRequest) -> SensitivityResult:
        """Запускает анализ чувствительности для набора параметров."""
        return run_sensitivity(request)

    ## --- Сценарии ---

    def list_scenarios(self) -> List[ScenarioShort]:
        """Возвращает список кратких сведений о сценариях."""
        return list_scenarios()

    def get_scenario(self, scenario_id: str) -> Optional[ScenarioDetail]:
        """Возвращает сценарий по id или None, если не найден."""
        return get_scenario(scenario_id)

    def save_scenario(self, scenario: ScenarioDetail) -> ScenarioDetail:
        """Создаёт новый или обновляет существующий сценарий в JSON-файле."""
        return save_scenario(scenario)

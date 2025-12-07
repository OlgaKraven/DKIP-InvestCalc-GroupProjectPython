## src/api/v1/routes_invest.py
"""
Маршруты API для InvestCalc (v1).

Задачи:
- расчёт TCO, ROI и срока окупаемости;
- анализ чувствительности;
- работа со сценариями (JSON вместо БД).
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from src.models.invest import (
    InvestInput,
    InvestResult,
    SensitivityRequest,
    SensitivityResult,
    ScenarioShort,
    ScenarioDetail,
)
from src.services.invest_service import (
    calculate_metrics,
    run_sensitivity,
    list_scenarios,
    get_scenario,
    save_scenario,
)

router = APIRouter()


@router.post(
    "/calc",
    response_model=InvestResult,
    summary="Расчёт TCO, ROI и срока окупаемости",
    tags=["calculations"],
    status_code=status.HTTP_200_OK,
)
async def calculate_invest_metrics(payload: InvestInput) -> InvestResult:
    """
    Выполнить расчёт основных экономических показателей по входным данным.
    """
    try:
        result = calculate_metrics(payload)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/sensitivity",
    response_model=SensitivityResult,
    summary="Анализ чувствительности ±20%",
    tags=["calculations"],
    status_code=status.HTTP_200_OK,
)
async def sensitivity_analysis(payload: SensitivityRequest) -> SensitivityResult:
    """
    Выполнить анализ чувствительности показателей к изменению входных параметров.
    """
    try:
        result = run_sensitivity(payload)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/scenarios",
    response_model=List[ScenarioShort],
    summary="Список сценариев (JSON-хранилище)",
    tags=["scenarios"],
)
async def get_scenarios() -> List[ScenarioShort]:
    """
    Получить список всех сохранённых сценариев расчётов.
    """
    return list_scenarios()


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Получить сценарий по идентификатору",
    tags=["scenarios"],
)
async def get_scenario_by_id(scenario_id: str) -> ScenarioDetail:
    """
    Получить детальную информацию о сценарии по его ID.
    """
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id={scenario_id} not found",
        )
    return scenario


@router.post(
    "/scenarios",
    response_model=ScenarioDetail,
    summary="Создать или обновить сценарий",
    tags=["scenarios"],
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_scenario(scenario: ScenarioDetail) -> ScenarioDetail:
    """
    Создать новый или обновить существующий сценарий.
    """
    try:
        saved = save_scenario(scenario)
        return saved
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save scenario: {exc}",
        ) from exc

## src/models/invest.py
"""
Pydantic-схемы (модели данных) для InvestCalc.

Задачи модуля:
- Описать входные данные для расчётов (InvestInput).
- Описать результат расчётов (InvestResult).
- Описать структуры для анализа чувствительности (Sensitivity*).
- Описать модели сценариев, которые будут храниться в JSON-файлах (Scenario*).
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


## === ВХОДНЫЕ ДАННЫЕ И РЕЗУЛЬТАТ РАСЧЁТОВ ============================================


class InvestInput(BaseModel):
    """
    Входные данные для расчёта экономической эффективности проекта.

    Допущение (учебный вариант):
    - CAPEX, OPEX и эффекты задаются суммарно за период анализа.
    """

    project_name: Optional[str] = Field(
        default=None,
        description="Название проекта / сценария (необязательно).",
        examples=["Внедрение CRM", "InvestCalc — пилот"],
    )
    capex: float = Field(
        ...,
        ge=0,
        description="Капитальные затраты (CAPEX), денежные единицы.",
        examples=[100000.0],
    )
    opex: float = Field(
        ...,
        ge=0,
        description="Операционные затраты (OPEX) за весь период анализа.",
        examples=[20000.0],
    )
    effects: float = Field(
        ...,
        ge=0,
        description=(
            "Суммарный экономический эффект за период: "
            "экономия затрат, рост выручки, снижение потерь и т.д."
        ),
        examples=[160000.0],
    )
    period_months: int = Field(
        ...,
        gt=0,
        le=600,
        description="Период анализа в месяцах (например, 36 месяцев = 3 года).",
        examples=[36],
    )
    discount_rate_percent: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Ставка дисконтирования в процентах (если применяется). "
            "В учебной модели может не использоваться."
        ),
        examples=[10.0],
    )


class InvestResult(BaseModel):
    """
    Результат расчёта экономических показателей.

    Конкретные формулы реализуются в services.invest_service.calculate_metrics().
    """

    project_name: Optional[str] = Field(
        default=None,
        description="Название проекта (протягивается из входных данных, если было указано).",
    )
    tco: float = Field(
        ...,
        description="Total Cost of Ownership — суммарные затраты за период (CAPEX + OPEX).",
        examples=[120000.0],
    )
    roi_percent: float = Field(
        ...,
        description="ROI — рентабельность инвестиций в процентах.",
        examples=[33.3],
    )
    payback_months: Optional[float] = Field(
        default=None,
        description="Срок окупаемости в месяцах (None, если проект не окупается в заданный период).",
        examples=[18.0],
    )
    payback_years: Optional[float] = Field(
        default=None,
        description="Срок окупаемости в годах.",
        examples=[1.5],
    )
    note: Optional[str] = Field(
        default=None,
        description="Дополнительный комментарий (например, пояснение по окупаемости).",
        examples=["Проект окупается в пределах периода анализа."],
    )


## === АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ =========================================================


SensitivityParameterName = Literal["capex", "opex", "effects"]


class SensitivityRequest(BaseModel):
    """
    Запрос на анализ чувствительности.

    Базовая идея:
    - берём базовый набор входных данных (base_input),
    - для указанных параметров повышаем и понижаем значение на delta_percent (обычно ±20%),
    - пересчитываем показатели и сравниваем результаты.
    """

    base_input: InvestInput = Field(
        ...,
        description="Базовый сценарий, относительно которого выполняется анализ.",
    )
    parameters: List[SensitivityParameterName] = Field(
        default_factory=lambda: ["capex", "opex", "effects"],
        description=(
            "Список параметров, по которым проводится анализ чувствительности. "
            "По умолчанию: CAPEX, OPEX и эффекты."
        ),
    )
    delta_percent: float = Field(
        default=20.0,
        gt=0,
        le=100,
        description="Величина изменения параметра в процентах для анализа чувствительности (обычно 20%).",
        examples=[20.0],
    )


class SensitivityItem(BaseModel):
    """
    Результаты анализа чувствительности по одному параметру.
    """

    parameter: SensitivityParameterName = Field(
        ...,
        description="Имя параметра, по которому проводился анализ.",
    )
    minus_delta_result: InvestResult = Field(
        ...,
        description="Результат при уменьшении параметра на delta_percent.",
    )
    plus_delta_result: InvestResult = Field(
        ...,
        description="Результат при увеличении параметра на delta_percent.",
    )


class SensitivityResult(BaseModel):
    """
    Ответ сервиса анализа чувствительности.
    """

    base_result: InvestResult = Field(
        ...,
        description="Результат расчёта по базовым входным данным.",
    )
    delta_percent: float = Field(
        ...,
        description="Величина изменения параметра в процентах.",
    )
    items: List[SensitivityItem] = Field(
        default_factory=list,
        description="Массив результатов анализа чувствительности по параметрам.",
    )


## === СЦЕНАРИИ (JSON-ХРАНИЛИЩЕ ВМЕСТО БД) ===========================================


class ScenarioShort(BaseModel):
    """
    Краткая информация о сценарии для списков/таблиц.

    Используется в ответе /scenarios (GET).
    """

    id: str = Field(
        ...,
        description="Строковый идентификатор сценария (например, UUID4 или человекочитаемый ключ).",
    )
    name: str = Field(
        ...,
        description="Название сценария (для отображения в списках).",
        examples=["CRM_2025_base", "InvestCalc_demo"],
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания сценария (ISO 8601).",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Дата и время последнего обновления сценария (если было).",
    )


class ScenarioDetail(ScenarioShort):
    """
    Полное описание сценария.

    Хранится в JSON-файле, используется для:
    - загрузки/сохранения сценариев;
    - повторных расчётов;
    - учебных примеров.
    """

    description: Optional[str] = Field(
        default=None,
        description="Краткое текстовое описание сценария.",
        examples=["Базовый сценарий внедрения CRM в отдел продаж."],
    )
    input: InvestInput = Field(
        ...,
        description="Входные данные для расчёта по данному сценарию.",
    )
    last_result: Optional[InvestResult] = Field(
        default=None,
        description="Последний сохранённый результат расчётов по сценарию (может быть None).",
    )

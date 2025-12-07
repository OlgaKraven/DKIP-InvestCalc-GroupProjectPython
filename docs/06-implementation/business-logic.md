# Бизнес-логика приложения (Business Logic)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия документа: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает **бизнес-логику** приложения InvestCalc:

- какие расчёты выполняет система;
- какие допущения используются для учебной модели;
- как реализованы функции в модуле `services/invest_service.py`;
- как устроен анализ чувствительности;
- как связаны бизнес-правила и код.

Документ ориентирован на разработчиков и методистов, проверяющих корректность расчётов и архитектуры.

---

## 2. Краткий обзор бизнес-функций

Система InvestCalc реализует следующие основные функции:

1. **Расчёт экономических показателей проекта:**
   - TCO (Total Cost of Ownership),
   - ROI (Return on Investment),
   - Payback Period (срок окупаемости).

2. **Анализ чувствительности** показателей к изменению входных параметров (CAPEX, OPEX, эффекты) на ±N%.

3. **Сценарный анализ:**
   - сохранение, обновление и чтение сценариев в JSON-хранилище,
   - повторный расчёт по сохранённым сценариям.

Бизнес-логика реализована в модуле:

```text
src/services/invest_service.py
```

и использует модели:

```text
src/models/invest.py
```

---

## 3. Входные данные для расчётов

Основная модель входных данных — `InvestInput`:

* `project_name: Optional[str]` — название проекта.
* `capex: float` — капитальные затраты (CAPEX), всего за период.
* `opex: float` — операционные затраты (OPEX), суммарно за период.
* `effects: float` — суммарный экономический эффект за период (экономия, доп. доход).
* `period_months: int` — период анализа в месяцах (например, 36 месяцев = 3 года).
* `discount_rate_percent: Optional[float]` — ставка дисконтирования (в текущей учебной реализации может не использоваться).

**Допущения учебной модели:**

* Все значения задаются **в одной валюте** (например, рубли).
* `capex`, `opex`, `effects` — **неотрицательные** числа.
* `period_months > 0`.
* Эффекты и OPEX распределяются **равномерно по месяцам** периода анализа.

---

## 4. Расчёт TCO

Функция:

```python
def _calculate_tco(input_data: InvestInput) -> float:
    return float(input_data.capex + input_data.opex)
```

**Формула:**

```text
TCO = CAPEX + OPEX
```

Где:

* `CAPEX` — разовые капитальные затраты,
* `OPEX` — операционные затраты за весь период анализа.

**Особенности:**

* TCO возвращается как `float` с округлением до 2 знаков на уровне итоговой модели `InvestResult`.
* Никаких дополнительных поправочных коэффициентов в учебной модели не используется.

---

## 5. Расчёт ROI (Return on Investment)

Функция:

```python
def _calculate_roi_percent(input_data: InvestInput, tco: float) -> float:
    if tco == 0:
        if input_data.effects > 0:
            return 999.99
        return 0.0

    roi = (input_data.effects - tco) / tco * 100.0
    return float(round(roi, 2))
```

**Базовая формула ROI:**

```text
ROI = (Effects - TCO) / TCO * 100%
```

Где:

* `Effects` — суммарный экономический эффект за период,
* `TCO` — общие затраты (см. выше).

**Особые случаи:**

* Если `TCO == 0` и `Effects > 0` → возвращается условно «очень большой» ROI = **999.99%** (учебное допущение).
* Если `TCO == 0` и `Effects == 0` → ROI = **0%**.

---

## 6. Расчёт срока окупаемости (Payback Period)

Функция:

```python
def _calculate_payback(input_data: InvestInput) -> tuple[Optional[float], Optional[float], Optional[str]]:
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
```

**Допущения:**

1. CAPEX — разовый платёж в начале периода.
2. OPEX и эффекты распределены **равномерно** по `period_months`.
3. Ежемесячный денежный поток:

```text
MonthlyCashFlow = MonthlyEffect - MonthlyOpex
```

Где:

```text
MonthlyEffect = Effects / period_months
MonthlyOpex   = Opex / period_months
```

4. Срок окупаемости (в месяцах):

```text
PaybackMonths = CAPEX / MonthlyCashFlow
PaybackYears  = PaybackMonths / 12
```

**Если `MonthlyCashFlow <= 0`:**

* Проект **не окупается** в рамках заданного периода.
* Функция возвращает:

  * `payback_months = None`,
  * `payback_years = None`,
  * текстовое пояснение в `note`.

---

## 7. Объединённый расчёт (calculate_metrics)

Главная публичная функция бизнес-логики:

```python
def calculate_metrics(input_data: InvestInput) -> InvestResult:
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
```

**Этапы:**

1. Проверка бизнес-ограничений:

   * расходы и эффекты не могут быть отрицательными;
   * период анализа должен быть больше 0.
2. Расчёт TCO.
3. Расчёт ROI на основе TCO и Effects.
4. Расчёт срока окупаемости.
5. Формирование итогового объекта `InvestResult`:

   * все числовые значения округляются до 2 знаков,
   * `note` содержит пояснение (или причину отсутствия окупаемости).

В случае нарушения бизнес-ограничений функция генерирует `ValueError`;
HTTP-слой (`routes_invest.py`) конвертирует её в `HTTP 422`.

---

## 8. Анализ чувствительности (Sensitivity Analysis)

### 8.1. Входные данные

Модель `SensitivityRequest`:

* `base_input: InvestInput` — базовый сценарий;
* `parameters: List["capex" | "opex" | "effects"]` — список параметров для анализа;
* `delta_percent: float` — процент изменения (обычно 20%).

### 8.2. Логика работы

Функция:

```python
def run_sensitivity(request: SensitivityRequest) -> SensitivityResult:
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

        minus_input_dict = deepcopy(base_input_dict)
        minus_input_dict[param] = _apply_delta(
            float(base_input_dict[param]),
            request.delta_percent,
            "minus",
        )
        minus_input = InvestInput(**minus_input_dict)
        minus_result = calculate_metrics(minus_input)

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
```

**Функция `_apply_delta`:**

```python
def _apply_delta(value: float, delta_percent: float, direction: str) -> float:
    factor = delta_percent / 100.0
    if direction == "minus":
        return float(round(value * (1.0 - factor), 2))
    if direction == "plus":
        return float(round(value * (1.0 + factor), 2))
    raise ValueError("direction must be 'minus' or 'plus'")
```

### 8.3. Интерпретация

Для каждого параметра:

1. Берётся базовый сценарий (`base_input`).
2. Значение параметра уменьшается на `delta_percent` (%).
3. Выполняется пересчёт всех показателей (`calculate_metrics`).
4. Значение параметра увеличивается на `delta_percent` (%).
5. Результаты сохраняются в `SensitivityItem`:

   * `minus_delta_result` — при уменьшении параметра,
   * `plus_delta_result` — при увеличении параметра.

Выходная модель `SensitivityResult` содержит:

* `base_result` — исходные показатели,
* `delta_percent` — использованный процент изменения,
* `items[]` — массив результатов по параметрам.

---

## 9. Сценарный анализ (JSON-сценарии)

### 9.1. Модели сценариев

Модели:

* `ScenarioShort` — короткая форма (для списка): `id`, `name`, `created_at`, `updated_at`.
* `ScenarioDetail` — полная форма:

  * `id`, `name`, `created_at`, `updated_at`,
  * `description`,
  * `input: InvestInput`,
  * `last_result: Optional[InvestResult]`.

### 9.2. Механика работы

Функции:

* `list_scenarios() -> List[ScenarioShort]`
* `get_scenario(id: str) -> Optional[ScenarioDetail]`
* `save_scenario(scenario: ScenarioDetail) -> ScenarioDetail`

Особенности:

* Сценарии хранятся в JSON-файле `data/scenarios.json`.
* При сохранении:

  * если `id` пустой → генерируется новый `UUID4`;
  * `created_at` заполняется при первом сохранении;
  * `updated_at` обновляется при каждом сохранении.
* Перед записью объект Pydantic конвертируется в JSON-совместимый словарь `model_dump(mode="json")`.

---

## 10. Бизнес-валидация и ошибки

Основные бизнес-правила:

1. `capex`, `opex`, `effects` ≥ 0.
2. `period_months` > 0.
3. `delta_percent` > 0 (при анализе чувствительности).
4. Список `parameters` для чувствительности не должен быть пустым.

При нарушении правил:

* Генерируется `ValueError` в бизнес-логике.
* HTTP-слой перехватывает её и возвращает `HTTP 422`.

Ошибки работы с JSON (файловая система):

* перехватываются как `OSError`;
* конвертируются в `HTTP 500` с описанием.

---

## 11. Связь с документацией и требованиями

Бизнес-логика соответствует:

* **ТЗ и требованиям** (`docs/02-requirements/*.md`):

  * функциональным требованиям к расчётам,
  * требованиям к анализу чувствительности,
  * требованиям к сценарному анализу.
* **Архитектурным решениям** (`docs/03-architecture/adr-*.md`):

  * выбор JSON вместо БД,
  * выделение бизнес-логики в отдельный слой `services`.
* **Модели данных** (`docs/04-data-model/domain-model.md`, `db-schema.md`):

  * сущности проекта и сценариев.

---

## 12. Возможные расширения

В дальнейшем бизнес-логика может быть расширена:

* добавлением дисконтированных показателей (NPV, PI);
* переходом от «суммарных значений за период» к помесячным потокам;
* поддержкой сложных сценариев (чувствительность по ставке дисконтирования, по срокам);
* вынесением расчётного ядра в отдельный модуль/сервис.

При любом расширении должны быть:

* обновлены модели (`models/invest.py`),
* адаптированы расчётные функции,
* добавлены новые тесты (`tests/test_service.py`, `tests/test_sensitivity.py`),
* обновлена документация (ТЗ, API, бизнес-правила).

 
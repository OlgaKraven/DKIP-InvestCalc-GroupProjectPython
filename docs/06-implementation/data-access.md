# Доступ к данным (Data Access Layer)

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия документа: 1.0  
Дата: `<указать>`

---

## 1. Назначение документа

Документ описывает, **как в InvestCalc реализован доступ к данным**:

- где и как хранятся сценарии расчётов;
- как организовано чтение/запись JSON-файлов;
- какие используются модели и функции;
- как обеспечивается изоляция данных в тестах.

В текущей учебной версии проекта **не используется СУБД** — вместо неё применяется лёгкое JSON-хранилище.

---

## 2. Общая схема работы с данными

### 2.1. Физическое расположение данных

Все данные хранятся в каталоге:

```text
<корень проекта>/
├── data/
│   ├── scenarios.json    ## основное хранилище сценариев
│   └── ...               ## дополнительные файлы данных (по необходимости)
```

Пути задаются централизованно в модуле `src/core/config.py`:

```python
class Settings:
    def __init__(self) -> None:
        self.BASE_DIR: Path = Path(__file__).resolve().parents[2]
        self.DATA_DIR: Path = self.BASE_DIR / "data"
        self.SCENARIOS_FILE: Path = self.DATA_DIR / "scenarios.json"
```

Все операции с данными выполняются **через эти пути**, а не через “магические строки” в коде.

---

### 2.2. Логическая модель данных

Логическая сущность — **сценарий расчёта**:

* идентификатор сценария (`id`),
* название (`name`),
* временные метки (`created_at`, `updated_at`),
* описание (`description`),
* входные данные расчёта (`input: InvestInput`),
* последний результат (`last_result: InvestResult | None`).

Для сериализации используются Pydantic-модели:

* `ScenarioShort` — краткая форма,
* `ScenarioDetail` — полная форма.

---

## 3. Формат файла `scenarios.json`

Файл `data/scenarios.json` содержит массив объектов JSON:

```json
[
  {
    "id": "uuid-или-другой-ключ",
    "name": "demo_scenario",
    "created_at": "2025-01-01T12:00:00",
    "updated_at": "2025-01-02T10:30:00",
    "description": "Учебный сценарий для демонстрации.",
    "input": {
      "project_name": "CRM внедрение",
      "capex": 100000,
      "opex": 20000,
      "effects": 160000,
      "period_months": 36,
      "discount_rate_percent": null
    },
    "last_result": {
      "project_name": "CRM внедрение",
      "tco": 120000,
      "roi_percent": 33.33,
      "payback_months": 18.0,
      "payback_years": 1.5,
      "note": "Проект окупается в рамках заданного периода анализа."
    }
  }
]
```

**Требования:**

* Корневой элемент — **массив**.
* Каждый элемент — валидный JSON-объект, совместимый с моделью `ScenarioDetail`.
* Даты в формате ISO 8601 (например, `"2025-01-01T12:00:00"`).

---

## 4. Вспомогательные функции доступа к JSON

Реализованы в `src/services/invest_service.py`.

### 4.1. Гарантия наличия каталога

```python
def _ensure_data_dir() -> None:
    """Гарантирует, что каталог для данных существует."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
```

Используется перед чтением/записью, чтобы избежать ошибок вида “каталог не найден”.

---

## 4.2. Чтение сценариев из файла

```python
def _load_scenarios_raw() -> List[dict]:
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
```

**Особенности:**

* Если файл отсутствует → возвращается пустой список.
* Если структура файла ошибочна (`не массив`) → возвращается пустой список.
* При ошибке JSON (`JSONDecodeError`) → возвращается пустой список (файл сглаживается логикой выше).

---

### 4.3. Запись сценариев в файл

```python
def _save_scenarios_raw(items: List[dict]) -> None:
    _ensure_data_dir()
    with settings.SCENARIOS_FILE.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
```

**Особенности:**

* `ensure_ascii=False` — поддержка кириллицы.
* `indent=2` — форматирование для удобства чтения человеком.
* Предполагается, что на вход подаётся **валидный список словарей**.

---

## 5. Публичные функции доступа к сценариям

### 5.1. Преобразование dict → Pydantic-модель

```python
def _parse_scenario(item: dict) -> Optional[ScenarioDetail]:
    try:
        return ScenarioDetail.model_validate(item)
    except Exception:
        return None
```

Используется во всех публичных функциях, чтобы:

* отбрасывать некорректные элементы,
* всегда работать с Pydantic-моделями, а не “сырыми” dict.

---

### 5.2. Получение списка сценариев

```python
def list_scenarios() -> List[ScenarioShort]:
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
```

**Назначение:**

* Возвращает **краткий список** сценариев для отображения в UI или в ответе API `/scenarios`.
* Результат отсортирован по `updated_at` (если есть) или по `created_at` — от новых к старым.

---

### 5.3. Получение сценария по идентификатору

```python
def get_scenario(scenario_id: str) -> Optional[ScenarioDetail]:
    raw_items = _load_scenarios_raw()
    for item in raw_items:
        if item.get("id") == scenario_id:
            return _parse_scenario(item)
    return None
```

Используется:

* в HTTP-эндпоинте `GET /api/v1/scenarios/{id}`,
* в возможных внутренних операциях.

---

### 5.4. Создание/обновление сценария

```python
def save_scenario(scenario: ScenarioDetail) -> ScenarioDetail:
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
```

**Логика:**

1. Загружаем текущие сценарии и парсим их в `ScenarioDetail`.
2. Генерируем `id`, если ещё не задан (`uuid4`).
3. Устанавливаем `created_at` при первом создании, `updated_at` — при каждом сохранении.
4. Если сценарий с таким `id` уже есть — **обновляем**, иначе **добавляем**.
5. Записываем весь список обратно в `scenarios.json`.

---

## 6. Использование в HTTP-слое

Функции доступа к данным используются в `src/api/v1/routes_invest.py`:

* `list_scenarios()` → `GET /api/v1/scenarios`
* `get_scenario()` → `GET /api/v1/scenarios/{id}`
* `save_scenario()` → `POST /api/v1/scenarios`

При ошибке файловой системы (`OSError`) в слое HTTP:

```python
except OSError as exc:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to save scenario: {exc}",
    ) from exc
```

---

## 7. Тестирование доступа к данным

В интеграционных тестах `tests/test_api.py` используется **временное хранилище**:

```python
@pytest.fixture
def temp_scenarios_dir(tmp_path, monkeypatch):
    original_data_dir = settings.DATA_DIR
    original_file = settings.SCENARIOS_FILE

    data_dir = tmp_path / "data"
    scenarios_file = data_dir / "scenarios.json"

    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(settings, "SCENARIOS_FILE", scenarios_file)

    yield

    monkeypatch.setattr(settings, "DATA_DIR", original_data_dir)
    monkeypatch.setattr(settings, "SCENARIOS_FILE", original_file)
```

Это позволяет:

* не портить реальный файл `data/scenarios.json` при тестах;
* проверять полную цепочку: API → сервис → JSON-файл → API.

---

## 8. Ограничения текущего подхода

* JSON-файл **не подходит** для высоконагруженной/многопользовательской системы:

  * нет блокировок,
  * нет транзакций,
  * возможны гонки при параллельной записи.
* Размер `scenarios.json` должен оставаться небольшим:

  * учебный проект предполагает ограниченное количество сценариев.
* При повреждении файла он будет silently “обнулён” логикой `_load_scenarios_raw`
  (что допустимо в учебном контексте, но нежелательно в боевом).

---

## 9. Возможные направления развития

В дальнейшем JSON-хранилище можно заменить на:

1. **SQLite/PostgreSQL** с ORM (SQLAlchemy / Entity Framework).
2. Отдельный микросервис хранения сценариев.
3. Облачное хранилище (S3/Blob, NoSQL и т.д.).

При переходе на БД потребуется:

* создать новый слой DAL (Data Access Layer),
* заменить реализации `list_scenarios/get_scenario/save_scenario`,
* сохранить совместимость API-контрактов,
* обновить документацию (DB schema, миграции).

---

## 10. Связанные документы

* `docs/04-data-model/db-schema.md`
* `docs/04-data-model/domain-model.md`
* `docs/04-data-model/er-diagram.md`
* `docs/06-implementation/api-internal.md`
* `docs/06-implementation/business-logic.md`

---
 
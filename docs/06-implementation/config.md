# Config — Конфигурация приложения InvestCalc

Документ описывает структуру конфигурации приложения, используемые настройки, переменные окружения и правила изменения конфигурации.

---

## 1. Где хранится конфигурация

Конфигурация находится в файле:

```

src/core/config.py

```

---

## 2. Назначение конфигурационного слоя

Config:

- изолирует настройки от кода;
- управляет параметрами приложения;
- служит единым источником информации о версии API;
- используется сервисами и API-уровнем.

---

## 3. Поля конфигурации

Пример структуры `config.py`:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "InvestCalc API"
    api_v1_prefix: str = "/api/v1"
    report_template_path: str = "templates/report_template.html"
    sensitivity_delta: float = 0.2   ## 20%
    debug: bool = False

settings = Settings()
```

---

### 3.1. `app_name`

Название API для Swagger и внутренних логов.

### 3.2. `api_v1_prefix`

Префикс для всех API-эндпоинтов.

### 3.3. `report_template_path`

Путь к HTML-шаблону для генерации отчётов.

### 3.4. `sensitivity_delta`

Базовый процент для анализа чувствительности.

### 3.5. `debug`

Включает расширенный вывод ошибок.

---

## 4. Переменные окружения

Config может быть переопределён через переменные окружения:

```
APP_NAME="InvestCalc PROD"
DEBUG=true
```

FastAPI автоматически подхватит эти значения через Pydantic BaseSettings.

---

## 5. Примеры использования

В API-слое:

```python
from core.config import settings

router = APIRouter(prefix=settings.api_v1_prefix)
```

В сервисах:

```python
delta = settings.sensitivity_delta
```

 
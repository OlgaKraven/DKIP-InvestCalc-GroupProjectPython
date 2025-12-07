# Logging — Логирование сервиса InvestCalc

Документ описывает схему логирования, уровни, рекомендуемые форматы и правила фиксации ошибок.

---

## 1. Цели логирования

- Отслеживание ошибок.
- Диагностика работы сервиса.
- Анализ производительности.
- Поддержка аудита.

---

## 2. Уровни логов

Используются стандартные уровни Python:

- DEBUG  
- INFO  
- WARNING  
- ERROR  
- CRITICAL  

---

## 3. Формат логов

Рекомендуемый формат (JSON):

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "level": "INFO",
  "event": "calculate",
  "duration_ms": 12
}
```

---

## 4. Логирование ошибок

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = service.calculate(data)
except Exception as exc:
    logger.error("Calculation failed", exc_info=True)
    raise
```

---

## 5. Хранение

В учебной версии:

* stdout → собирается Docker/Kubernetes

В расширенной:

* Elastic Stack (ELK)
* Loki + Grafana
* Cloud Logging

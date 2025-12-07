# Monitoring — Мониторинг сервиса InvestCalc

Документ описывает методы мониторинга приложения, точки проверки,
метрики производительности и рекомендации по инструментам.

---

## 1. Зачем нужен мониторинг

Даже учебная ИС должна контролировать:

- доступность API;
- производительность эндпоинтов;
- количество ошибок;
- нагрузку при docker-run/compose.

---

## 2. Базовый мониторинг в FastAPI

### 2.1. Healthcheck endpoint

Используется `/api/v1/health`.

Ответ:

```json
{ "status": "ok" }
```

### 2.2. Logging middleware

Собирать:

* метод;
* путь;
* время выполнения;
* статус-код.

---

## 3. Продвинутый мониторинг (при расширении проекта)

### 3.1. Prometheus

Добавить библиотеку:

```bash
pip install prometheus-fastapi-instrumentator
```

Инициализация:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Будет доступно по `/metrics`.

---

## 4. Метрики

| Категория | Пример                                     |
| --------- | ------------------------------------------ |
| HTTP      | latency, requests count, error ratio       |
| App       | количество расчётов, среднее время расчёта |
| System    | CPU/Memory docker-контейнера               |

---

## 5. Инструменты мониторинга

* **Prometheus + Grafana** (рекомендуется)
* **cAdvisor** для Docker-ресурсов
* **Sentry** для ошибок

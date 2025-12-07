# Healthchecks — Проверки состояния InvestCalc

Документ описывает методы проверки работоспособности сервиса.

---

## 1. Типы проверок

### 1.1. Liveness Probe  
Проверяет, жив ли процесс сервера.

### 1.2. Readiness Probe  
Готов ли сервис принимать трафик.

---

## 2. Эндпоинт здоровья

```

GET /api/v1/health

```

Пример ответа:

```json
{ "status": "ok" }
```

---

## 3. Для Docker/Kubernetes

### Docker Compose (healthcheck):

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 10s
  retries: 5
```

### Kubernetes:

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
```

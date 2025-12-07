# Scaling — Масштабирование InvestCalc

Документ описывает варианты масштабирования приложения в локальных и облачных средах.

---

## 1. Типы масштабирования

### 1.1. Вертикальное  
Увеличение ресурсов одного контейнера.

### 1.2. Горизонтальное  
Добавление дополнительных экземпляров контейнера.

---

## 2. Горизонтальное масштабирование

Использование Gunicorn + Uvicorn Workers:

```bash
gunicorn src.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

---

## 3. Масштабирование через Docker Compose

```yaml
services:
  investcalc:
    image: investcalc
    deploy:
      replicas: 3
```

---

## 4. Масштабирование в Kubernetes

* Deployment replicas
* Horizontal Pod Autoscaler (HPA)
* Resource requests/limits

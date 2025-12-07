# CI Test Report

Проект: **InvestCalc — Инвестиционный аналитик ИС**  
Версия документа: 1.0  
Дата генерации отчёта: `<указать>`

---

## 1. Назначение документа

Этот документ служит **офлайн-версией отчёта о результатах тестирования**, автоматически выполняемого в CI/CD (GitHub Actions).

Он фиксирует:

- успешность выполнения тестов;
- количество пройденных/проваленных тестов;
- ошибки, возникшие при прогоне;
- покрытие кода (coverage);
- время выполнения тестового пайплайна;
- артефакты, сохранённые после выполнения CI-процесса.

Используется:

- преподавателями для проверки выполнения проекта,
- командой проекта для анализа стабильности сборок,
- при формировании отчётности.

---

## 2. Описание CI-пайплайна

Тестирование выполняется в GitHub Actions в workflow-файле:

```

.github/workflows/tests.yml

```

Пайплайн включает:

1. Установка Python и зависимостей (`pip install -r requirements.txt`)
2. Запуск юнит-тестов:  
```

pytest --maxfail=1 --disable-warnings -q

```
3. Генерация отчёта coverage:  
```

pytest --cov=src --cov-report=xml --cov-report=term-missing

```
4. Сохранение артефактов (coverage.xml, pytest-report)
5. Отправка статуса сборки

---

## 3. Результат выполнения тестов

### 3.1. Общая статистика

| Показатель | Значение |
|-----------|----------|
| Всего тестов | `<N>` |
| Успешно | `<N_passed>` |
| Провалено | `<N_failed>` |
| Пропущено | `<N_skipped>` |
| Ошибки выполнения | `<N_errors>` |
| Broken tests (xfail/xpass) | `<N>` |
| Время выполнения | `<T сек>` |

---

### 3.2. Пример лога CI

```

==================== Test Session ====================
platform linux -- Python 3.11
collected 18 items

tests/test_api.py ............
tests/test_service.py ......
tests/test_sensitivity.py ...

## 18 passed in 1.42s

```

---

## 4. Покрытие кода (Coverage)

### 4.1. Общая сводка

| Модуль | Coverage (%) |
|--------|--------------|
| src/services/invest_service.py | `<XX>%` |
| src/api/v1/routes_invest.py | `<XX>%` |
| src/models/invest.py | `<XX>%` |
| src/core/config.py | `<XX>%` |
| Итого | `<TOTAL>%` |

### 4.2. Пример отчёта (консоль)

```

---------- coverage: platform linux, python 3.11 ----------
Name                                   Stmts   Miss  Cover
----------------------------------------------------------

src/services/invest_service.py           185      8    96%
src/api/v1/routes_invest.py               75      4    94%
src/models/invest.py                      42      0   100%
src/core/config.py                        18      0   100%
----------------------------------------------------------

TOTAL                                    320     12    96%

```

### 4.3. Покрытие по строкам (пример)

```

src/services/invest_service.py ..................... 96%

* Пропущено: 141, 208, 309, 350

```

---

## 5. Выявленные дефекты (если есть)

Если в тестировании CI обнаружены сбои, их фиксируют ниже:

| ID | Тип ошибки | Модуль | Описание | Лог |
|----|------------|--------|----------|-----|
| BUG-CI-01 | AssertionError | test_api.py | Неверный статус-код | см. log ##158 |
| BUG-CI-02 | KeyError | invest_service | Ошибка при чтении сценариев | см. log ##162 |

Если ошибок нет:

```

Ошибки в ходе выполнения CI не обнаружены.
Все тесты выполнены успешно.

```

---

## 6. Скриншоты/артефакты CI

Артефакты CI:

- coverage.xml  
- junit-report.xml  
- pytest-stdout.txt  
- workflow-log.txt  

Пример ссылки:

```

Artifacts: [https://github.com/](https://github.com/)<ORG>/<REPO>/actions/runs/<RUN_ID>

```

---

## 7. Граф истории сборок (если используется badge)

Пример badge:

![Tests](https://img.shields.io/github/actions/workflow/status/<ORG>/<REPO>/tests.yml?label=tests)
![Coverage](https://img.shields.io/codecov/c/github/<ORG>/<REPO>?label=coverage)

---

## 8. Выводы

CI-процесс позволяет:

- гарантировать стабильность проекта,
- автоматически проверять ключевые функции,
- фиксировать метрики качества,
- предотвращать регрессии,
- обеспечивать точность расчётов (что важно для InvestCalc).

На текущем этапе:

- ✔ тесты выполнены успешно,  
- ✔ уровень покрытия соответствует требованиям,  
- ✔ ошибок stability/regression не выявлено,  
- ✔ артефакты сохранены.

---

## 9. Связанные документы

- `/07-TESTING/test-plan.md`  
- `/07-TESTING/test-strategy.md`  
- `/07-TESTING/metrics.md`  
- `/07-TESTING/regression-checklist.md`  
- `/08-DEVOPS/ci-cd-pipeline.md`  
- `/08-DEVOPS/github-actions.yml`  


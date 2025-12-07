## Use Case модель системы «InvestCalc — Инвестиционный аналитик ИС»

Документ описывает пользовательские сценарии в формате Use Case, включая акторов, пред- и постусловия, основной поток событий, альтернативные потоки и исключения.

Все ключевые диаграммы представлены в формате Mermaid.

---

## 1. Акторы

| Актор | Описание |
|-------|----------|
| **Пользователь** (Студент / Аналитик) | Выполняет ввод данных, запускает расчёты, анализирует результаты |
| **Преподаватель / Руководитель** | Проверяет результат, анализирует отчёты |
| **Внешняя система** | Обращается к API InvestCalc |
| **CI/CD Pipeline** | Запускает тесты и сборку (косвенный актор) |

---

## 2. Общая Use Case-диаграмма

```mermaid
flowchart LR
    actorUser([Пользователь])
    actorTeacher([Преподаватель])
    actorExternal([Внешняя система])

    UC1[[UC-1: Базовый расчёт]]
    UC2[[UC-2: Анализ чувствительности]]
    UC3[[UC-3: Сравнение сценариев]]
    UC4[[UC-4: Формирование отчёта]]
    UC5[[UC-5: Использование API]]
    UC6[[UC-6: Валидация данных]]
    UC7[[UC-7: Загрузка сценария]]

    actorUser --> UC1
    actorUser --> UC2
    actorUser --> UC3
    actorUser --> UC4
    actorUser --> UC6
    actorUser --> UC7

    actorTeacher --> UC4

    actorExternal --> UC5
    UC5 --> UC1
    UC5 --> UC2
```

---

## 3. Список Use Cases

| ID   | Название                          | Описание                            |
| ---- | --------------------------------- | ----------------------------------- |
| UC-1 | Выполнить базовый расчёт          | Расчёт TCO, ROI, Payback            |
| UC-2 | Выполнить анализ чувствительности | Вариации CAPEX/OPEX ±20%            |
| UC-3 | Сравнить два сценария             | Локальный vs облачный               |
| UC-4 | Сформировать отчёт                | HTML/PDF                            |
| UC-5 | Использовать API                  | Работа внешних приложений           |
| UC-6 | Проверить корректность данных     | Валидация входа                     |
| UC-7 | Загрузить сценарий из файла       | input-local.json / input-cloud.json |

---

## 4. Use Case UC-1 — Выполнить базовый расчёт

## Диаграмма последовательности

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant API as /api/v1/calculate
    participant S as Сервис расчётов

    U->>API: POST /calculate (CAPEX,OPEX,period,effects)
    API->>API: Валидация данных
    alt Ошибка
        API-->>U: 422 Validation Error
    else Успех
        API->>S: Расчёт TCO/ROI/Payback
        S-->>API: Результат
        API-->>U: 200 OK + JSON
    end
```

---

## 5. Use Case UC-2 — Выполнить анализ чувствительности

## Диаграмма последовательности

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant API as /api/v1/sensitivity
    participant S as Модуль чувствительности

    U->>API: POST /sensitivity (data)
    API->>API: Валидация
    alt Некорректные данные
        API-->>U: 422 Validation Error
    else Корректно
        API->>S: Генерация вариаций
        loop Вариации CAPEX/OPEX
            S->>S: Расчёт TCO/ROI/Payback
        end
        S-->>API: Массив результатов
        API-->>U: 200 OK + JSON
    end
```

---

## 6. Use Case UC-3 — Сравнить два сценария

## Диаграмма потоков данных

```mermaid
flowchart TD
    A[input-local.json] --> C[Расчёт UC-1]
    B[input-cloud.json] --> D[Расчёт UC-1]

    C --> E[Сравнение показателей]
    D --> E

    E --> F[Вывод рекомендаций]
```

---

## 7. Use Case UC-4 — Сформировать отчёт

## Диаграмма

```mermaid
flowchart TD
    A[Исходные данные] --> R[Сбор данных для отчёта]
    B[Базовый расчёт] --> R
    C[Анализ чувствительности] --> R
    D[Сравнение сценариев] --> R

    R --> HTML[HTML-отчёт]
    R --> PDF[(PDF-отчёт)]
```

---

## 8. Use Case UC-5 — Использовать API

## Диаграмма

```mermaid
sequenceDiagram
    participant ES as Внешняя система
    participant API as FastAPI сервис

    ES->>API: POST /calculate
    API-->>ES: JSON результат

    ES->>API: POST /sensitivity
    API-->>ES: JSON массив вариаций
```

---

## 9. Use Case UC-6 — Проверка корректности данных

## Диаграмма валидации

```mermaid
flowchart TD
    A[JSON входные данные]
    B[Валидация Pydantic]
    C[Расчёт]
    D[422 Ошибка]

    A --> B
    B -->|OK| C
    B -->|Ошибка| D
```

---

## 10. Use Case UC-7 — Загрузка сценария

## Диаграмма

```mermaid
flowchart TD
    A[Выбор файла .json]
    B[Чтение файла]
    C[Валидация данных]
    D[Расчёт UC-1]
    E[Результат]

    A --> B --> C
    C -->|OK| D --> E
    C -->|Ошибка| X[Validation Error]
```


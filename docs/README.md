## InvestCalc — Инвестиционный аналитик ИС

[![CI](https://github.com/OlgaKraven/InvestCalc/actions/workflows/ci.yml/badge.svg)](https://github.com/OlgaKraven/InvestCalc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-MkDocs-green.svg)](https://olgakraven.github.io/InvestCalc/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

Учебная мини–информационная система для оценки экономической эффективности внедрения информационных систем
(TCO, ROI, срок окупаемости, чувствительность ±20%).

Проект используется как базовый пример для дисциплин по проектированию и разработке информационных систем
и может служить отправной точкой для учебных и дипломных проектов.

---

## 1. Основные возможности

- Расчёт **TCO (Total Cost of Ownership)**: совокупная стоимость владения ИС.
- Расчёт **ROI (Return on Investment)** и показателей эффективности.
- Расчёт **срока окупаемости** проекта.
- Анализ чувствительности параметров (CAPEX, OPEX, SaaS-подписка, эффекты) на уровне ±20%.
- Работа с несколькими сценариями (локальная инфраструктура / облачная модель).
- REST API (FastAPI) для интеграции с внешними системами и фронтендом.
- Документация в формате MkDocs с диаграммами (Mermaid, C4, схемы БД).
- Поддержка контейнеризации (Docker, docker-compose) и CI/CD (GitHub Actions).

---

## 2. Технологический стек

- Язык: **Python 3.11+**
- Web-фреймворк: **FastAPI**
- Валидация данных: **Pydantic**
- HTTP-сервер: **Uvicorn**
- Тестирование: **pytest**
- Документация: **MkDocs** (+ плагины и темы)
- Контейнеризация: **Docker**, **docker-compose**
- CI/CD: **GitHub Actions**

---

## 3. Структура репозитория

```text
investcalc/
├── README.md
├── LICENSE
├── .gitignore
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       └── ci.yml
├── data/                 ## исходные данные и тестовые сценарии
├── devops/               ## DevOps-документация и дополнительные файлы
├── docs/                 ## проектная документация (MkDocs)
├── src/                  ## исходный код приложения (FastAPI + доменная логика)
├── tests/                ## авто-тесты (pytest)
├── templates/            ## шаблоны отчётов / HTML
├── docker-compose.yml
├── Dockerfile
├── mkdocs.yml
└── requirements.txt
```

Подробное описание архитектуры, моделей данных и API см. в каталоге `docs/`.

---

## 4. Быстрый старт

## 4.1. Локальный запуск (без Docker)

1. Установите Python 3.11+.
2. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/OlgaKraven/InvestCalc.git
   cd InvestCalc
   ```

3. Создайте и активируйте виртуальное окружение (опционально):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  ## Windows: .venv\Scripts\activate
   ```

4. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

5. Запустите приложение:

   ```bash
   uvicorn src.main:app --reload
   ```

6. Откройте документацию API:

   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## 4.2. Запуск в Docker

```bash
docker compose up --build
```

После успешного запуска API будет доступен по адресу `http://localhost:8000`.

---

## 5. Тестирование

Для запуска тестов:

```bash
pytest
```

Рекомендуется добавлять новые тесты для всех модулей бизнес-логики и API-эндпоинтов.

---

## 6. Документация

Документация проекта собирается с помощью MkDocs.

```bash
mkdocs serve          ## локальный просмотр
mkdocs build          ## сборка статического сайта
```

Основные разделы документации расположены в каталоге `docs/`:

- `00-intro` — введение и описание проекта;
- `01-planning` — цели, заинтересованные стороны, риски;
- `02-requirements` — требования и бизнес-правила;
- `03-architecture` — архитектура, ADR, схемы;
- `04-data-model` — модель данных и ER-диаграммы;
- `05-api` — описание API и ошибок;
- `06-implementation`, `07-quality`, `08-devops`, `09-team` и др.

---

## 7. Как участвовать в развитии проекта

Мы приглашаем студентов и преподавателей к доработке прототипа:

- улучшение предметной модели и расчётов;
- добавление новых сценариев (облачные и гибридные модели);
- улучшение интерфейса и UX;
- расширение тестового покрытия;
- улучшение документации и примеров.

Перед отправкой pull request, пожалуйста, ознакомьтесь с правилами в файле
[`CONTRIBUTING.md`](CONTRIBUTING.md) и кодексом поведения [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## 8. Лицензия

Проект распространяется по лицензии **MIT**. Подробности см. в файле [`LICENSE`](LICENSE).

---

## 9. Контакты и обратная связь

- Issues и предложения: вкладка **Issues** репозитория GitHub
- Ошибки и уязвимости: см. файл [`SECURITY.md`](SECURITY.md)

Если вы используете InvestCalc в учебном процессе, будет полезно указать ссылку на этот репозиторий
в методических материалах или отчётах.

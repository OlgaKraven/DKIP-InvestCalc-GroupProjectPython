## PROJECT — шаблоны (skeletons) проектов

Каталог `PROJECT` содержит два полностью готовых каркаса (skeletons), которые можно использовать как стартовые шаблоны для учебных, командных или демонстрационных проектов:

- **API Skeleton** — серверная часть на FastAPI с хранением данных в JSON.
- **Client Skeleton** — минимальный клиент (HTML + JS), который взаимодействует с REST API.

Оба каркаса запускаются отдельно, но могут работать **в связке**, образуя полноценное клиент-серверное приложение.

---

## Содержание папки

```text
PROJECT/
  api-skeleton/        ## серверный шаблон (FastAPI)
  client-skeleton/     ## клиентский шаблон (HTML + JS)
  db/
    db-schema.sql      ## пример схемы SQL-БД (для расширенных проектов)
```

---

##  1. API Skeleton (FastAPI)

API использует:

* FastAPI + Swagger UI
* JSON-файл как хранилище данных
* сервисный слой (services)
* маршруты (routers)
* Pydantic-модели
* CORS-middleware для работы с клиентом

## Структура

```text
api-skeleton/
  README.md
  requirements.txt
  data/
    items.json
  src/
    main.py
    api/v1/routes_example.py
    models/item.py
    services/item_service.py
    storage/json_storage.py
  tests/
```

## Запуск API

```bash
cd api-skeleton
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Доступно:

* Swagger: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
* Здоровье API: **[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)**
* Пример эндпоинта: **GET [http://127.0.0.1:8000/api/v1/items](http://127.0.0.1:8000/api/v1/items)**

---

## 2. Client Skeleton (HTML + JS)

Минималистичный клиент без фреймворков.

Работает через `fetch()` с API Skeleton.

## Структура

```text
client-skeleton/
  README.md
  public/
    index.html
  src/
    api.js
```

## Запуск клиента (вариант 1 — простой)

```bash
cd client-skeleton
python -m http.server 5500
```

Открой в браузере:

```
http://127.0.0.1:5500/public/index.html
```

Клиент начнёт обращаться к API Skeleton.

---

## 3. Связка клиент ↔ сервер

Чтобы клиент мог делать запросы в API, в сервер добавлен **CORS Middleware**:

```python
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Благодаря этому клиент может отправлять:

* `GET /api/v1/items`
* `POST /api/v1/items`

и получать ответы из API.

---

## 4. Полный цикл запуска (оба сервиса)

## Запуск API

```bash
cd api-skeleton
uvicorn src.main:app --reload
```

Проверка:

```
http://127.0.0.1:8000/health
```

## Запуск клиента

```bash
cd client-skeleton
python -m http.server 5500
```

Переход:

```
http://127.0.0.1:5500/public/index.html
```

## Протестировать взаимодействие

В браузере:

* нажмите **“Загрузить items”** → отображает JSON-список
* заполните поля id + name → нажмите **“Добавить item”**

Данные мгновенно появятся в `items.json`.

---

## 5. db-schema.sql (опционально)

В каталоге `db/` лежит схема SQL БД:

```
db/
  db-schema.sql
```

Она используется как:

* пример проектирования БД,
* основа для перехода с JSON-хранения на SQL,
* демонстрация нормализованной структуры (сценарий → вход → результат).

---

## 6. Использование skeleton-ов

Skeleton-ы предназначены для:

* командных учебных проектов,
* демонстраций клиент-серверного подхода,
* создания собственных API и клиентов,
* хакатонов и проектной деятельности СПО,
* практической работы с REST, сервисами, моделями и хранением данных.

 
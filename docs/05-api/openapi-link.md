# OpenAPI Specification — Спецификация API InvestCalc

Документ объясняет, как получить, использовать и подключить OpenAPI-спецификацию, автоматически генерируемую FastAPI.

---

## 1. Где получить OpenAPI

OpenAPI JSON доступен по адресу:

```

[http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

```

---

## 2. Swagger UI

```

[http://localhost:8000/docs](http://localhost:8000/docs)

```

Функции:

- просмотр моделей данных;
- отправка запросов;
- тестирование эндпоинтов;
- генерация примеров;
- проверка ошибок валидации.

---

## 3. ReDoc

```

[http://localhost:8000/redoc](http://localhost:8000/redoc)

```

Функции:

- структурированное дерево OpenAPI,
- просмотр вложенных схем,
- фильтрация по тегам.

---

## 4. Интеграция с внешними сервисами

Можно подключить OpenAPI к:

- Postman → Import → Link → `http://localhost:8000/openapi.json`
- Insomnia → Create from OpenAPI
- SwaggerHub → Import URL
- Stoplight → New → From OpenAPI URL

---

## 5. Экспорт OpenAPI в файл

```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

---

## 6. Использование OpenAPI для генерации клиента

С помощью `openapi-generator-cli`:

```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o client-sdk/
```

Поддерживаются:

* Python
* TypeScript/Fetch
* TypeScript/Angular
* C##
* Java
* Kotlin
* Go

---


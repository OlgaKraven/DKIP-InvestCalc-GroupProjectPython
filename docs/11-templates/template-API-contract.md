##  Шаблон контракта API (API Contract Specification)
*В соответствии с REST, RFC 7231, RFC 8259, OpenAPI 3.1, ГОСТ 34/19*

---

## 1. Общая информация об API

**Название API:**
Описание назначения, доменной области и бизнес-задачи API.

**Версия API:**
`v1` / `v2` / и т.д.

**Базовый URL:**

* Production: `https://api.example.com/api/v1/`
* Development: `http://localhost:8000/api/v1/`

**Стиль API:**
REST / JSON-only / Stateless

**Формат данных:**

* Request: JSON (RFC 8259)
* Response: JSON (RFC 8259)

**Стандарты:**

* RFC 7231 — HTTP semantics
* RFC 8259 — JSON
* RFC 7807 — Problem Details
* ГОСТ 34.602 — требования
* ISO/IEC 25010 — качество

---

## **2. Описание ресурса**

```
Ресурс: <Название ресурса>
Например: /calculations
```

**Описание ресурса:**
Кратко: что делает ресурс, какие сущности представляет.

**Модель данных (DTO):**

```json
{
  "field1": "string",
  "field2": 123,
  "field3": true
}
```

**Типы данных:**

* `string`, `number`, `integer`, `boolean`, `array`, `object`
* DateTime: ISO 8601

---

## **3. Методы API по ресурсу**

Каждый метод оформляется отдельно.

---

### **3.1. GET /resource**

**Назначение:**
Что возвращает метод.

**Query-параметры:**

| Параметр | Тип | Обязательный | Описание       |
| -------- | --- | ------------ | -------------- |
| offset   | int | нет          | Смещение       |
| limit    | int | нет          | Кол-во записей |

**Response 200 OK:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Example"
    }
  ],
  "total": 30
}
```

**Ошибки:**

| Код | Тип            | Описание               |
| --- | -------------- | ---------------------- |
| 400 | Bad Request    | Некорректные параметры |
| 500 | Internal Error | Внутренняя ошибка      |

---

### **3.2. GET /resource/{id}**

**Назначение:**
Вернуть элемент по ID.

**Path-параметры:**

| Параметр | Тип | Обязательный | Описание      |
| -------- | --- | ------------ | ------------- |
| id       | int | да           | Идентификатор |

**Response 200 OK:**

```json
{
  "id": 1,
  "name": "Example"
}
```

**Ошибки:**

| Код | Описание          |
| --- | ----------------- |
| 404 | Элемент не найден |

---

### **3.3. POST /resource**

**Назначение:**
Создать новый элемент.

**Request Body:**

```json
{
  "name": "string",
  "value": 123
}
```

**Response 201 Created:**

```json
{
  "id": 1,
  "name": "string",
  "value": 123
}
```

**Ошибки:**

| Код | Описание         |
| --- | ---------------- |
| 422 | Ошибка валидации |

---

### **3.4. PUT /resource/{id}**

**Назначение:**
Полное обновление ресурса.

**Request Body:**
Тот же формат, что и POST.

**Response 200 OK:**

```json
{
  "id": 1,
  "name": "updated",
  "value": 300
}
```

---

### **3.5. PATCH /resource/{id}**

**Назначение:**
Частичное обновление.

**Request Body (пример):**

```json
{
  "value": 999
}
```

---

### **3.6. DELETE /resource/{id}**

**Response 204 No Content**

Ошибки:

| Код | Описание  |
| --- | --------- |
| 404 | Не найден |

---

## **4. JSON Schema**

Пример схемы:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Example",
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name": { "type": "string" },
    "value": { "type": "number" }
  },
  "required": ["name"]
}
```

---

## **5. Стандартизированный формат ошибок (RFC 7807)**

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Ошибка валидации",
  "status": 422,
  "detail": "Поле name обязательно",
  "instance": "/resource"
}
```

---

## **6. Примеры сценариев использования**

### Сценарий 1 — создание расчёта

```
POST /calculations
```

## Сценарий 2 — получение списка

…

---

## **7. Требования по безопасности**

* Все входящие данные валидируются (OWASP)
* Нет передачи паролей/секретов
* Лимиты размера запроса
* Защита от:

  * SQL Injection
  * JSON Injection
  * DoS через большие payload

---

## **8. Версионирование контракта**

* Семантическое:

  * MAJOR — breaking changes
  * MINOR — новые поля
  * PATCH — исправления

---

## **9. Связанные ADR**

* ADR-09 — Принципы REST
* ADR-10 — Версионирование
* ADR-11 — Валидация
* ADR-12 — Ошибки
* ADR-14 — OpenAPI

---

## **10. Ссылки**

* RFC 7231
* RFC 8259
* RFC 7807
* ISO/IEC 25010
* ISO/IEC/IEEE 42010
* ГОСТ 34.602


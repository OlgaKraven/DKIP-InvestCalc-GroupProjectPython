# Backup & Restore — Бэкапы и восстановление

Документ описывает методы создания резервных копий данных и восстановления системы.

---

## 1. Текущая версия InvestCalc

В текущей версии БД нет. Используются файлы JSON в `data/`.

---

## 2. Резервное копирование файлов

### 2.1. Данные сценариев:

```bash
cp data/input-local.json backup/
cp data/input-cloud.json backup/
```

### 2.2. Шаблоны:

```bash
cp -r templates/ backup/templates/
```

---

## 3. Восстановление

```bash
cp backup/input-local.json data/
```

---

## 4. Если в будущем добавляется БД (PostgreSQL)

### Создание дампа:

```bash
pg_dump investcalc > backup/db.sql
```

### Восстановление:

```bash
psql investcalc < backup/db.sql
```

---

## 5. Хранение бэкапов

* Git LFS (не рекомендуется для больших файлов)
* S3-совместимое хранилище
* локальные копии

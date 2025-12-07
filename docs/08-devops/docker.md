# cker для InvestCalc##  ВведениеЭтот документ описывает процессы сборки, запуска и использования Docker-образов для учебного проекта **InvestCalc**.
В проекте используется единый образ *investcalc-api*, который автоматически публикуется в **GitHub Container Registry (GHCR)** через CI/CD.

Документ предназначен для студентов, преподавателей и DevOps-специалистов, желающих развернуть InvestCalc локально или на сервере.

---

##  Имя Docker-образаОфициальное имя образа:

```
ghcr.io/<owner>/investcalc-api:latest
```

Где:

* `<owner>` — пользователь или организация GitHub, например:
  `OlgaKraven`
* `investcalc-api` — имя контейнера сервера InvestCalc
* `latest` — стабильная версия образа
* возможен дополнительный тег по SHA коммита

Например:

```
ghcr.io/OlgaKraven/investcalc-api:latest
ghcr.io/OlgaKraven/investcalc-api:3a5fbb9
```

Эти образы собираются в CI job `docker` (см. **ci-cd.md**).

---

###  Локальная сборка Docker-образаДля локальной разработки вы можете собрать образ вручную.

Команда сборки:

```bash
docker build -t investcalc-api:local .
```

Пояснения:

* `investcalc-api:local` — локальный тег образа;
* Dockerfile должен находиться в корне проекта.

Проверка списка образов:

```bash
docker images
```

---

###  Локальный запуск контейнераПосле сборки выполняем запуск:

```bash
docker run --rm \
  -p 8000:8000 \
  investcalc-api:local
```

После этого API доступно:

```
http://localhost:8000
```

Документация:

* Swagger UI: `/docs`
* ReDoc: `/redoc`
* OpenAPI JSON: `/openapi.json`

---

## 5. Работа с GHCR (GitHub Container Registry)

## 5.1. Авторизация

Если репозиторий приватный, потребуется логин:

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <your-username> --password-stdin
```

Если репозиторий публичный — доступ возможен без логина.

---

## 5.2. Загрузка образа

```bash
docker pull ghcr.io/<owner>/investcalc-api:latest
```

Например:

```bash
docker pull ghcr.io/OlgaKraven/investcalc-api:latest
```

---

## 5.3. Запуск образа из GHCR

```bash
docker run --rm \
  -p 8000:8000 \
  ghcr.io/<owner>/investcalc-api:latest
```

---

## 6. Переменные окружения (.env)

Используемые переменные:

| Переменная             | Назначение                                  | Значение по умолчанию           |
| ---------------------- | ------------------------------------------- | ------------------------------- |
| `INVESTCALC_ENV`       | режим сервера                               | `production`                    |
| `INVESTCALC_LOG_LEVEL` | уровень логирования                         | `info`                          |
| `DATABASE_URL`         | строка подключения к БД (если используется) | *не требуется в базовой версии* |

Пример `.env`:

```env
INVESTCALC_ENV=production
INVESTCALC_LOG_LEVEL=info
## DATABASE_URL=postgresql://user:pass@db:5432/investcalc
```

---

## 6.1. Передача переменных в Docker

```bash
docker run --rm \
  -e INVESTCALC_ENV=production \
  -e INVESTCALC_LOG_LEVEL=debug \
  -p 8000:8000 \
  ghcr.io/<owner>/investcalc-api:latest
```

---

## 7. Использование docker-compose

Для локального или серверного развертывания рекомендуется `docker-compose`.

Файл `docker-compose.yml`:

```yaml
version: "3.9"

services:
  investcalc-api:
    image: ghcr.io/<owner>/investcalc-api:latest
    container_name: investcalc-api
    ports:
      - "8000:8000"
    restart: unless-stopped
    env_file:
      - .env
```

Запуск:

```bash
docker compose up -d
```

Остановка:

```bash
docker compose down
```

Проверка:

```bash
docker compose ps
```

---

## 8. Локальная разработка с авто-перезапуском (опционально)

При разработке полезно монтировать локальный код:

```yaml
services:
  investcalc-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    environment:
      INVESTCALC_ENV: "development"
```

Перезапуск контейнера после изменений:

```bash
docker compose restart
```

---

## 9. Сборка Docker в CI/CD

Этот процесс описан подробно в файле:

➡️ [CI/CD — GitHub Actions](ci-cd.md)

В CI образ:

* собирается через `docker buildx`;
* публикуется в GHCR;
* тегируется как:

```
latest
${{ github.sha }}
```

Сборка включает кеширование:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

---

## 10. Полезные команды Docker

## Просмотр контейнеров:

```bash
docker ps
```

## Просмотр логов:

```bash
docker logs investcalc-api
```

## Удаление контейнеров и образов:

```bash
docker rm <id>
docker rmi <image>
```

## Проверка слоёв образа:

```bash
docker history investcalc-api:local
```

---

## 11. Связанные документы

* CI/CD:
  ➡️ `ci-cd.md`

* Руководство по развёртыванию:
  ➡️ `deployment-manual.md`

* Тестирование API:
  ➡️ `../07-testing/test-strategy.md`

---

## 12. Заключение

Docker-подход делает проект InvestCalc:

* легко развертываемым,
* независимым от окружения,
* готовым для демонстрации и обучения,
* интегрированным в современный DevOps-процесс.



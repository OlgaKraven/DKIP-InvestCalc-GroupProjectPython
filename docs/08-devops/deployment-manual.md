# Руководство по развёртыванию InvestCalc


## 1. Введение

Этот документ описывает процесс развёртывания учебного проекта **InvestCalc** в окружениях разработки, тестирования и демонстрации.
Сервис разворачивается через Docker и использует готовый контейнер из **GitHub Container Registry (GHCR)**.

Документ подходит для:

* студентов, которым нужно запустить приложение у себя;
* преподавателей, которым нужно подготовить демонстрационный стенд;
* DevOps-специалистов, желающих автоматизировать развертывание.

---

## 2. Предварительные требования

Перед запуском убедитесь, что установлены:

### На Windows / macOS:

* Docker Desktop

### На Linux:

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin -y
sudo systemctl enable docker
sudo systemctl start docker
```

Проверить:

```bash
docker --version
docker compose version
```

---

## 3. Получение Docker-образа из GHCR

Образ InvestCalc публикуется автоматически через CI/CD.

### Имя образа:

```
ghcr.io/<owner>/investcalc-api:latest
```

Например:

```
ghcr.io/OlgaKraven/investcalc-api:latest
```

### Если репозиторий публичный:

```bash
docker pull ghcr.io/OlgaKraven/investcalc-api:latest
```

### Если репозиторий приватный:

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <your-username> --password-stdin
docker pull ghcr.io/<owner>/investcalc-api:latest
```

---

## 4. Минимальный .env файл

Создайте файл:

```
.env
```

Содержимое:

```env
INVESTCALC_ENV=production
INVESTCALC_LOG_LEVEL=info
## DATABASE_URL=postgresql://user:pass@db:5432/investcalc
```

В учебной версии проект **не требует БД**, строка DATABASE_URL не обязательна.

---

## 5. Вариант 1 — Быстрый запуск через Docker

### Команда запуска:

```bash
docker run --rm \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/<owner>/investcalc-api:latest
```

После запуска:

* API доступно на:
  [http://localhost:8000](http://localhost:8000)
* Swagger UI:
  [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc:
  [http://localhost:8000/redoc](http://localhost:8000/redoc)

Для остановки — нажмите **Ctrl+C**.

---

## 6. Вариант 2 — Развёртывание через docker-compose

Создайте файл:

```
docker-compose.yml
```

Содержимое:

```yaml
version: "3.9"

services:
  investcalc-api:
    image: ghcr.io/<owner>/investcalc-api:latest
    container_name: investcalc-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
```

### Запуск:

```bash
docker compose up -d
```

### Проверка:

```bash
docker compose ps
```

Ожидается статус `Up`.

### Логи:

```bash
docker compose logs -f
```

### Остановка:

```bash
docker compose down
```

---

## 7. Вариант 3 — Развёртывание на Linux-сервере (Ubuntu)

Пошаговая инструкция:

### 7.1. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### 7.2. Установка Docker

```bash
sudo apt install docker.io docker-compose-plugin -y
```

### 7.3. Добавить пользователя:

```bash
sudo usermod -aG docker $USER
```

Перелогиниться.

### 7.4. Подготовить папку проекта

```bash
mkdir investcalc && cd investcalc
nano .env
nano docker-compose.yml
```

### 7.5. Запустить в фоне:

```bash
docker compose up -d
```

### 7.6. Проверить работу:

```bash
curl http://localhost:8000/health
```

*Если реализован healthcheck endpoint.*

---

## 8. Обновление версии приложения

Переход на новую версию:

### Шаг 1. Остановка текущего контейнера:

```bash
docker compose down
```

### Шаг 2. Получение новой версии:

```bash
docker pull ghcr.io/<owner>/investcalc-api:latest
```

### Если репозиторий приватный:
### Шаг 3. Запуск:

```bash
docker compose up -d
```

---

## 9. Защита и безопасность

### Рекомендации:

* Использовать переменные окружения для чувствительных данных.
* Не хранить `.env` в Git.
* Ограничить внешние порты (использовать firewall).
* Добавить reverse-proxy (Traefik, Caddy, Nginx) — при необходимости.

---

## 10. Полезные команды

### Список контейнеров:

```bash
docker ps
```

### Удаление контейнера:

```bash
docker rm <id>
```

### Удаление образа:

```bash
docker rmi <image>
```

## Просмотр логов:

```bash
docker logs investcalc-api
```

---

## 11. Связанные документы

* **CI/CD:**
  ➡️ `ci-cd.md`

* **Docker:**
  ➡️ `docker.md`

* **Тестирование и API:**
  ➡️ `../07-testing/test-strategy.md`

 
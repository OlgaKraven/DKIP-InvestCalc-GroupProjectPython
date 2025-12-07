# CI/CD для проекта InvestCalc

## 1. Введение

Этот документ описывает полный процесс CI/CD для учебного проекта **InvestCalc**, реализованного на Python/FastAPI.
Пайплайн построен на базе **GitHub Actions** и выполняет проверку качества кода, тестирование, анализ безопасности, сборку документации и автоматическую публикацию Docker-образа в **GitHub Container Registry (GHCR)**.

Цель CI/CD — обеспечить:

* стабильность и воспроизводимость сборок;
* единый стандарт качества кода;
* автоматическую проверку всех PR;
* удобное развертывание в Docker.

---

## 2. Общая структура CI/CD

Полный конфигурационный файл GitHub Actions находится по пути:

```
.github/workflows/ci.yml
```

Пайплайн запускается автоматически при:

* `push` в ветку **main**,
* создании/обновлении Pull Request в **main**.

Состоит из следующих задач (**jobs**):

| Job          | Назначение                                       |
| ------------ | ------------------------------------------------ |
| **tests**    | Матричные тесты на Python 3.10 / 3.11 / 3.12     |
| **lint**     | Проверка качества кода (ruff + black)            |
| **security** | Проверка безопасности кода и зависимостей        |
| **docs**     | Сборка документации MkDocs и деплой GitHub Pages |
| **docker**   | Сборка и публикация Docker-образа в GHCR         |

---

## 3. Job `tests`: матричные тесты

Job выполняет тестирование на нескольких версиях Python:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

Проверяется:

* корректность функций расчётов (TCO, ROI, Payback);
* корректность API;
* совместимость проекта с несколькими версиями Python.

Основные команды:

```bash
pip install -r requirements.txt
pytest -q
```

Если тесты не проходят — сборка останавливается.

---

## 4. Job `lint`: проверка качества кода

Выполняется после тестов.

Инструменты:

* **ruff** — быстрый Python-линтер;
* **black** — форматтер кода.

Команды:

```bash
ruff check .
black --check .
```

Если найдено нарушение стиля — PR блокируется.

---

## 5. Job `security`: анализ безопасности

Проверяет:

## Уязвимости в исходном коде

Инструмент: **bandit**

Команда:

```bash
bandit -r src -ll
```

## Уязвимости во внешних зависимостях

Инструмент: **safety**

Команда:

```bash
safety check --file=requirements.txt --full-report
```

В учебных условиях можно настроить этот job как «не фатальный»
(например, `|| true`), но лучше оставлять строгим.

---

## 6. Job `docs`: сборка и публикация документации

Этот job:

1. Ставит mkdocs и плагины:

   ```bash
   pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
   ```

2. Проверяет, что документация собирается **без ошибок**:

   ```bash
   mkdocs build --strict
   ```

3. Если ветка **main**, запускается деплой на GitHub Pages:

```yaml
uses: peaceiris/actions-gh-pages@v4
publish_dir: ./site
publish_branch: gh-pages
```

В результате документация доступна по адресу:

```
https://<owner>.github.io/<repo>/
```

---

## 7. Job `docker`: сборка и публикация Docker-образа

Job зависит от тестов и линтинга.

### Шаги:

#### 1. Настройка buildx

Позволяет кэширование и многоархитектурные сборки.

#### 2. Вход в реестр GHCR

```yaml
registry: ghcr.io
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}
```

#### 3. Имя образа

```text
ghcr.io/<owner>/investcalc-api:latest
```

#### 4. Сборка с кэшированием

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

#### 5. Публикация тегов:

* latest
* по SHA коммита:

```
ghcr.io/<owner>/investcalc-api:${{ github.sha }}
```

---

#### 8. Порядок выполнения jobs

Порядок выстроен так:

1. **tests**
2. **lint**
3. **security**
4. **docs**
5. **docker**

Если тесты или линт не прошли — **docker и docs не выполняются**.
Такой порядок защищает качество основной ветки.

---

#### 9. Локальная проверка перед PR

Разработчик может локально воспроизвести CI:

#### Тесты

```
pytest -q
```

#### Линтеры

```
ruff check .
black --check .
```

#### Документация

```
mkdocs build --strict
```

#### Docker

```
docker build -t investcalc-api:local .
```

---

## 10. Связанные материалы

##ы# Требования

➡️ **[Спецификация требований](../02-requirements/requirements-spec.md)**

## API

➡️ **[Обзор API](../05-api/api-overview.md)**
## Тестирование

➡️ **[Стратегия тестирования](../07-testing/test-strategy.md)**

## DevOps

➡️ **[Docker](docker.md)**
➡️ **[Руководство по развёртыванию](deployment-manual.md)**


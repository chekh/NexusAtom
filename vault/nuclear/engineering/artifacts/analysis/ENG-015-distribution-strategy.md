---
id: ENG-015
type: analysis
status: active
tags: [distribution, mcp, tech_stack, boundaries, cli, architecture]
traces:
  analyzes: [DEC.ARCH.THREE_LAYER_MODEL.v1, DEC.ARCH.HYBRID_ARCHIVE_MODEL.v1]
  defines: [DEC.ARCH.DISTRIBUTION_BOUNDARIES.v1]
created: 2026-04-12
---
# Стратегия дистрибуции, реализации и границ NexusAtom

## 1. Языковая стратегия (Tech Stack)

| Компонент | Язык/Стек | Обоснование |
|-----------|-----------|-------------|
| **Ядро (Core)** | Python 3.11+ | Нативная работа с YAML/MD, Pydantic v2 для валидации, NetworkX для графов, экосистема AI-инструментов. |
| **MCP Сервер** | Python (официальный `mcp` SDK) | Прямой импорт ядра, zero-overhead, нативная совместимость с Cursor, Claude Desktop, Aider. |
| **CLI** | Python (Typer + Rich) → бинарники (`PyInstaller`/`shiv`) | Быстрый старт, кроссплатформенность, минимальный оверхед. |
| **Плагины IDE** | TypeScript (VS Code, Obsidian) | Только для UI/навигации. Логика валидации делегируется CLI/MCP через IPC. |
| **CI/CD Runner** | Python + Docker | Воспроизводимые среды, изоляция, интеграция с GitHub/GitLab Actions. |

**Правило:** Не дублировать логику валидации/парсинга. Ядро — единственный источник истины. Остальные компоненты — клиенты или обертки.

---

## 2. Модели Дистрибуции и Применения

| Вариант | Формат | Целевая аудитория | Сценарий использования |
|---------|--------|-------------------|------------------------|
| **A. Local CLI** | `pip`, `pipx`, `brew` | Разработчики, архитекторы | `nexus init`, `nexus validate`, `nexus status`. Работает локально, читает `vault/` напрямую. |
| **B. MCP Server** | Python-процесс (Stdio/SSE) | AI-агенты (OpenClaw, Cursor, Aider) | Агенты вызывают `read_artifact`, `query_vault`, `transition_status` без прямого доступа к ФС. |
| **C. Docker Image** | `nexusatom/engine:latest` | CI/CD, air-gapped среды, командные пайплайны | `docker run -v $(pwd):/vault nexusatom validate`. Изоляция, воспроизводимость. |
| **D. CI/CD Plugin** | GitHub/GitLab Action | DevOps, QA | Валидация `vault/` при PR, блокировка мёрджа при нарушении контрактов. |

**Границы (Чем мы НЕ являемся):**
- ❌ Не замена Git (мы дополняем его: спеки живут ВМЕСТЕ с кодом).
- ❌ Не UI-платформа для менеджеров (пока только CLI/MCP/API).
- ❌ Не облачный SaaS (локальный-first, данные остаются у пользователя).
- ❌ Не оркестратор задач/спринтов (мы управляем состоянием спеков, не бэклогом Jira).
- ❌ Не LLM-обертка (LLM — клиент, ядро детерминировано).

---

## 3. Архитектура MCP Сервера

### 3.1. Реализация
- **Язык:** Python (тот же репозиторий, импорт `nexus_atom.core`).
- **Протокол:** Stdio (для локальных IDE/агентов) + HTTP/SSE (для удалённых клиентов).
- **Безопасность:** Read-only по умолчанию. Write требует явного флага в `_core/config/security_policy.yaml`.

### 3.2. Доступные Инструменты (MCP Tools)
```yaml
tools:
  - name: "list_resources"
    description: "Вернуть список ядерных ресурсов и их статусы"
  - name: "read_artifact"
    description: "Прочитать контент артефакта по id или пути"
  - name: "query_vault"
    description: "Структурный поиск: filter by type, status, nuclear_id, tags"
  - name: "transition_status"
    description: "Изменить статус артефакта с FSM-валидацией"
  - name: "validate_resource"
    description: "Проверить контракт ядерного ресурса на соответствие _core/security_policy"
  - name: "resolve_links"
    description: "Резолвинг [[id]] → путь + статус + превью (исключая dark_zones)"
```

### 3.3. Запуск
```bash
# Локально (для Cursor/Claude/Aider)
nexus mcp serve --transport stdio

# Docker (для CI/агентных сред)
docker run -v $(pwd):/vault nexusatom/mcp --transport http --port 3000
```

---

## 4. Локальные Инструменты и Пользовательский Путь

### 4.1. CLI Команды (`nexus`)
```bash
nexus init --profile minimal          # Создать vault/ с канонической структурой
nexus add resource engineering        # Добавить новый ресурс в nuclear/
nexus validate [--all | --resource X] # Валидация контрактов, FSM, dark_zones
nexus status                          # Сводка: ресурсы, статусы, нарушения
nexus mcp serve                       # Запуск MCP сервера
nexus export --format markdown        # Экспорт vault/ для архива или миграции
```

### 4.2. Установка и Инициализация
1. **Установка:**
   ```bash
   pipx install nexus-atom  # или brew tap nexusatom/nexus && brew install nexus
   ```
2. **Инициализация в проекте:**
   ```bash
   cd /path/to/project
   nexus init --profile standard  # генерирует _core/config/, nuclear/engineering/
   git add vault/
   git commit -m "chore: initialize nexus vault"
   ```
3. **Подключение агентов:**
   Добавить в конфиг IDE/агента:
   ```json
   {
     "mcpServers": {
       "nexus": {
         "command": "nexus",
         "args": ["mcp", "serve", "--transport", "stdio"]
       }
     }
   }
   ```

---

## 5. Дорожная карта Реализации

| Фаза | Фокус | Компоненты | Критерий готовности |
|------|-------|------------|---------------------|
| **Phase 0** | Ядро + CLI + MCP | Python Core, Typer CLI, MCP Stdio, Pydantic валидатор | `nexus init`, `nexus validate`, MCP-клиент читает vault |
| **Phase 1** | Инфраструктура | Docker Image, CI Action, Obsidian/VS Code Plugin (TS) | Валидация в PR, плагин показывает граф/статусы |
| **Phase 2** | Интеллект | Vector Index, Semantic Search, Graph Viz | `nexus query --semantic "auth flow"` возвращает релевантные узлы |
| **Phase 3** | Enterprise | SSO, Multi-tenant Sync, Audit Webhooks, CAS Archive | Корпоративный деплой, compliance, retention policies |

---

## 6. Критические Решения и Обоснование

| Вопрос | Решение | Почему |
|--------|---------|--------|
| **Python или TS для MCP?** | Python | Прямой доступ к ядру, нет рассинхрона логики, нативная поддержка в AI-стеке. |
| **Нужен ли Web UI?** | Нет (в Phase 0/1) | CLI + MCP + IDE плагины покрывают 90% сценариев. UI = оверхед на старте. |
| **Локальный vs Облачный?** | Local-first | Данные не покидают репозиторий. Соответствует принципам SSOT и безопасности. |
| **Как обрабатывать бинарные файлы?** | Не храним в `vault/`. Только хэши + ссылки. `vault/` — текстовый слой. |
| **Что если агент сломает контракт?** | MCP возвращает `ValidationError`. Ядро блокирует запись. Требуется human-in-the-loop для `override`. |

---

## ✅ Итог
NexusAtom — **локальный, детерминированный, агенто-ориентированный слой управления знаниями**. Он не заменяет инструменты разработки, а делает их осознанными через валидируемые контракты. MCP-сервер — мост между строгостью ядра и гибкостью AI. CLI — точка входа для людей. Docker/CI — гарантия воспроизводимости.

**Следующий шаг:** Утвердить стратегию → перейти к реализации Phase 0 (Core Parser + MCP Server).

---
*Анализ проведён в рамках методологии NexusAtom*
*Дата: 2026-04-12*
*Статус: active (ожидает утверждения архитектуры дистрибуции)*

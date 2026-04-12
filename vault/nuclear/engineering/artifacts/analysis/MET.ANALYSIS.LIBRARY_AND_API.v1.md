---
id: MET.ANALYSIS.LIBRARY_AND_API.v1
type: methodology_analysis
status: active
tags: [library, api, templates, prompts, skills, adaptability, extensibility]
traces:
  analyzes: [DEC.ARCH.THREE_LAYER_MODEL.v1, DEC.ARCH.DISTRIBUTION_STRATEGY.v1]
  defines: [DEC.ARCH.LIBRARY_AND_API.v1]
created: 2026-04-12
---
# Стратегия: Хранилище активов (Templates/Skills/Prompts) и Архитектура API

## 1. Хранение и доставка "готовых активов"

### 1.1. Что такое "Активы"?
- **Шаблоны** (`_template.md`, `adr_template.md`)
- **Промпты** (`agentic_researcher.yaml`, `code_reviewer.yaml`)
- **Скиллы** (наборы правил, кастомные валидаторы, рендереры)
- **Профили инициализации** (`minimal`, `standard`, `research`, `enterprise`)

### 1.2. Архитектура хранения (Registry → Cache → Override)
```text
[Глобальный Реестр] (git-репо / CDN / SaaS)  ←  nexus pull template agile@1.2
        │
        ▼
[Локальный Кэш] (~/.nexus/cache/)           ←  Быстрый доступ, версионирование
        │
        ▼
[Проект] (vault/_core/config/overrides/)    ←  Локальная кастомизация (merge/patch)
```

**Правила:**
- ✅ Активы **не хранятся внутри каждого `vault/`**. Они подтягиваются по требованию.
- ✅ Версионирование через семвер: `skill:researcher@2.1.0`.
- ✅ Приоритет загрузки: `overrides/` > `cache/` > `registry`.
- ✅ Агенты не скачивают активы напрямую. Только `nexus pull` или MCP `pull_asset`.

### 1.3. Как доступны агентам и пользователям?
| Интерфейс | Команда / Инструмент | Пример |
|-----------|----------------------|--------|
| **CLI** | `nexus pull template research-log` | Скачивает в `~/.nexus/cache/`, линкует в проект |
| **CLI** | `nexus init --profile research` | Автоматически тянет нужные шаблоны и промпты |
| **MCP** | `list_assets`, `pull_asset`, `render_template` | Агенты получают готовые структуры без галлюцинаций |
| **Plugin API** | `on_asset_resolve(asset_id)` → `content` | Кастомные рендереры, динамическая подстановка контекста |

---

## 2. Архитектура API (Адаптивность и Интеграция)

### 2.1. Принципы проектирования
1. **Schema-First**: Все сущности описываются через JSON Schema / YAML. API не захардкоживает типы.
2. **Stateless Core**: API не хранит состояние. Всё чтение/запись идёт через `vault/` на диске.
3. **Generic Endpoints**: Эндпоинты не зависят от типов артефактов (`/artifacts/{id}`, не `/atoms/{id}`).
4. **Plugin Hooks**: Точки расширения для кастомной логики без изменения ядра.

### 2.2. Слои API
| Слой | Протокол | Назначение | Клиенты |
|------|----------|------------|---------|
| **Internal** | Python (`import nexus_atom.core`) | Прямой доступ для скриптов, тестов, плагинов | Core Engine, Scripts |
| **External (MCP)** | Stdio / HTTP SSE | Безопасный доступ для AI-агентов | Cursor, Claude, Aider, OpenClaw |
| **External (REST)** | HTTP/JSON | Интеграция с CI/CD, IDE, внешними системами | GitHub Actions, VS Code, Linear |
| **Events** | Webhooks / SSE | Реактивные уведомления об изменениях | Боты, мониторинг, дашборды |

### 2.3. Ключевые эндпоинты / MCP Tools
```yaml
# Generic Artifacts
GET    /v1/artifacts?nuclear_id=engineering&type=decision&status=approved
POST   /v1/artifacts/{id}              # Создание/обновление (с валидацией)
GET    /v1/artifacts/{id}/content      # Чтение контента (с резолвингом [[id]])
DELETE /v1/artifacts/{id}              # Архивация (soft-delete)

# State Machine
POST   /v1/transitions                 # Изменение статуса (FSM-валидация)
GET    /v1/fsm/{type}/graph            # Визуализация допустимых переходов

# Vault Operations
POST   /v1/validate                    # Проверка контрактов, манифестов, ссылок
GET    /v1/status                      # Сводка по ресурсам, нарушениям, активным Зонам тьмы
POST   /v1/query                       # Структурный поиск + семантика (опционально)

# Assets & Skills
GET    /v1/assets                      # Список доступных шаблонов/промптов/скиллов
POST   /v1/assets/{id}/render          # Рендер шаблона с подстановкой контекста
POST   /v1/skills/{id}/execute         # Запуск скилла (кастомная логика)
```

### 2.4. Plugin & Skill API (Точки расширения)
```python
# Пример регистрации плагина (Python)
from nexus_atom.plugins import hook

@hook("on_validate_artifact")
def my_custom_validator(artifact, context):
    if artifact.type == "adr" and "security" in artifact.tags:
        assert "threat_model" in artifact.content, "ADR must include threat_model"

@hook("on_transition")
def notify_slack(artifact, old_status, new_status):
    if new_status == "approved":
        send_slack(f"✅ {artifact.id} approved")
```
**Правила:**
- Плагины загружаются из `vault/_core/config/plugins/` или `~/.nexus/plugins/`.
- Не могут менять `_core/config/` напрямую. Только валидация, рендеринг, уведомления.
- Изолированы: ошибки в плагине не роняют ядро (только предупреждение в лог).

---

## 3. Адаптивность к другим решениям

| Сценарий интеграции | Механизм | Пример |
|---------------------|----------|--------|
| **Jira / Linear** | Вебхук + маппинг статусов | `approved → In Progress`, `completed → Done` |
| **Obsidian / Logseq** | Импорт/экспорт Markdown + граф связей | `nexus export --format obsidian` |
| **CI/CD (GitHub/GitLab)** | REST API + Docker Runner | `nexus validate --fail-on-critical` в пайплайне |
| **Кастомный LLM-агент** | MCP + `pull_asset` + `query_vault` | Агент получает контекст без доступа к ФС |
| **Enterprise SSO** | OAuth2 Proxy перед REST/MCP | Корпоративный деплой, аудит, мульти-тенант |

**Границы адаптивности:**
- ✅ Ядро валидирует только структуру и FSM. Не диктует бизнес-процессы.
- ✅ Экспорт/импорт поддерживает любые форматы (Markdown, JSON, GraphML, CSV).
- ✅ API не привязано к Git. `vault/` может лежать в S3, IPFS, локальной ФС.
- ❌ API не заменяет бизнес-логику клиента. Только состояние, валидация, трассировка.

---

## ✅ Итог
1. **Активы** хранятся в централизованном реестре, кэшируются локально, переопределяются в проекте. Не засоряют `vault/`.
2. **API** спроектирован как generic, schema-first, plugin-friendly. MCP для агентов, REST для CI/IDE, Events для реактивности.
3. **Адаптивность** достигается через плагины, маппинг статусов, экспорт в любые форматы и изоляцию ядра от бизнес-логики.

**Следующий шаг:** Утвердить стратегию → начать реализацию Phase 0 (Core Parser + MCP Server).

---
*Анализ проведён в рамках методологии NexusAtom*
*Дата: 2026-04-12*
*Статус: active (ожидает утверждения архитектуры API и реестра активов)*

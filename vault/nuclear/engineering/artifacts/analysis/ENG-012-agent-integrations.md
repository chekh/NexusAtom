---
id: ENG-012
type: analysis
status: active
tags: [integrations, mcp, vscode, claude, openai, codex, aider, sdk, api]
traces:
  analyzes: [DEC.ARCH.THREE_LAYER_MODEL.v1, DEC.ARCH.DISTRIBUTION_STRATEGY.v1]
  defines: [DEC.ARCH.AGENT_INTEGRATIONS.v1]
  related_to: [MET.ANALYSIS.LIBRARY_AND_API.v1]
created: 2026-04-12
---
# Стратегия интеграции с ведущими агентскими средами и IDE

## 1. Интеграционная Матрица

| Платформа / Агент | Протокол | Реализация NexusAtom | Уровень доступа | Сценарий использования |
|-------------------|----------|----------------------|-----------------|------------------------|
| **VS Code / Cursor** | MCP (Stdio) + TS Extension | Нативный MCP сервер + UI-плагин для графа/статусов | Read + Write (с аппрувом) | Чтение спеков в чате, валидация кода на лету, переходы FSM |
| **Claude Desktop** | MCP (Stdio) | Прямой импорт `nexus-atom` в `claude_desktop_config.json` | Read + Write (ограничено политикой) | Контекстный поиск по `vault/`, генерация артефактов, аудит |
| **OpenAI Codex / Agent SDK** | Function Calling / REST Bridge | REST `/v1/tools` + JSON Schema генерация | Read-only (по умолчанию) | Автоматическая валидация, query vault, экспорт отчётов |
| **Aider / Codex CLI** | CLI Hooks + FS Watch | `nexus agent hook --watch` + `--read-only` флаг | Read + FS-операции | Синхронизация кода и спеков, авто-обновление `manifest.yaml` |
| **LangChain / LlamaIndex** | Python Package / Tool Wrapper | `nexus_atom.integrations.langchain.NexusVaultTool` | Read + Query | RAG-пайплайны, семантический поиск по `vault/`, графовые запросы |
| **Obsidian / Logseq** | TS Plugin + File Sync | Плагин для рендеринга `[[id]]`, визуализации графа | Read + Local Edit | Навигация по знаниям, ручной ревью, экспорт Markdown |

---

## 2. Детальные Сценарии Интеграции

### 2.1. VS Code & Cursor (MCP + Extension)
**Протокол:** MCP Stdio (основной) + VS Code API (UI)
**Конфигурация (`.cursor/mcp.json` или `.vscode/mcp.json`):**
```json
{
  "mcpServers": {
    "nexus": {
      "command": "nexus",
      "args": ["mcp", "serve", "--transport", "stdio", "--scope", "project"],
      "env": {
        "NEXUS_VAULT_ROOT": "${workspaceFolder}/vault",
        "NEXUS_AGENT_ROLE": "builder"
      }
    }
  }
}
```
**Фичи:**
- `nexus_query_vault` → поиск спеков/решений прямо из Copilot/Cursor Chat.
- `nexus_validate_file` → проверка открытого файла против контракта артефакта.
- `nexus_transition_status` → безопасная смена статуса артефакта (требует подтверждения).
- **UI Extension:** Дерево `vault/`, статус-бейджи, визуализация графа зависимостей, быстрые команды (`Ctrl+Shift+P → Nexus: Init/Validate`).

### 2.2. Claude Desktop (Anthropic MCP)
**Протокол:** MCP Stdio
**Конфигурация (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "nexus-atom": {
      "command": "uvx", 
      "args": ["nexus-atom", "mcp", "serve"],
      "env": {
        "NEXUS_VAULT_ROOT": "/Users/chekh/Development/NexusAtom/vault",
        "NEXUS_DARK_ZONES": "strict"
      }
    }
  }
}
```
**Фичи:**
- Claude получает инструменты `list_resources`, `read_artifact`, `resolve_links`, `validate_contract`.
- Автоматическое исключение `_archive/` и `dark_zones` из контекста.
- `max_context_tokens: 16000` → ядро автоматически суммаризирует длинные артефакты перед отправкой.
- **Безопасность:** Write-операции требуют явного `allow_writes: true` в политике. По умолчанию — Read-only.

### 2.3. OpenAI Codex / Agent SDK
**Протокол:** REST `/v1/tools` + Function Calling
**Генерация схем:**
```python
# nexus_atom.api.openapi_tools.generate()
{
  "type": "function",
  "function": {
    "name": "nexus_query_artifacts",
    "description": "Query vault artifacts by nuclear_id, type, status, or semantic tags.",
    "parameters": {
      "type": "object",
      "properties": {
        "nuclear_id": {"type": "string"},
        "type": {"type": "string", "enum": ["decision", "analysis", "requirement"]},
        "status": {"type": "string"},
        "limit": {"type": "integer", "default": 5}
      },
      "required": ["query"]
    }
  }
}
```
**Фичи:**
- Codex может вызывать `nexus_query_artifacts` для поиска контекста перед генерацией кода.
- Интеграция с OpenAI Agent SDK через `ToolResource`.
- Поддержка Structured Outputs для гарантированного формата ответов.

### 2.4. CLI-агенты (Aider, Codex CLI, OpenCode)
**Протокол:** CLI Hooks + Filesystem Watcher
**Конфигурация (`.aider.conf.yaml`):**
```yaml
command: "nexus agent hook --mode read-only --watch vault/"
read: ["vault/**"]
write: [] # Запрет прямой записи, только через nexus CLI
```
**Фичи:**
- `nexus agent hook` запускает фоновый процесс, который:
  - Блокирует запись в `vault/` без валидации.
  - Авто-обновляет `manifest.yaml` при изменении кода в `src/`.
  - Инжектит актуальный контекст спеков в промпт агента.
- Поддержка `--auto-commit` для атомарных коммитов с привязкой к `atom_id`.

### 2.5. Фреймворки (LangChain, LlamaIndex, AutoGen)
**Протокол:** Python Package (`nexus_atom.integrations.*`)
**Пример (LangChain):**
```python
from nexus_atom.integrations.langchain import NexusVaultTool
from langchain.agents import AgentExecutor

vault_tool = NexusVaultTool(
    vault_path="./vault",
    role="researcher",
    vectorize=True
)

# Агент получает инструмент автоматически
executor = AgentExecutor(tools=[vault_tool], ...)
```
**Фичи:**
- `NexusRAGRetriever` для LlamaIndex.
- `NexusMemoryAdapter` для синхронизации агентской памяти с `_core/context/memory/agents/`.
- Поддержка асинхронных запросов и батчинга.

---

## 3. Управление Контекстом и Безопасность

| Механизм | Как работает | Для кого критично |
|----------|--------------|-------------------|
| **Dark Zones Enforcement** | Ядро удаляет пути из ответа ДО отправки в API. Даже если агент запросит явно. | Claude, Cursor, OpenAI (защита от промпт-инъекций) |
| **Token Budget & Summarization** | Если артефакт > `max_tokens`, ядро возвращает `summary + full_content_ref`. | Все LLM-агенты (экономия окна) |
| **Read/Write Scopes** | `role: builder` → `write: requirements`. `role: auditor` → `write: none`. | Мультиагентные среды (Aider, Cursor, Codex) |
| **Idempotent Operations** | Все `POST /v1/...` операции идемпотентны. Повторный вызов = no-op или актуальное состояние. | CLI-агенты, CI/CD, Retry-логика |
| **Audit Trail** | Каждое действие агента логируется: `agent_id`, `tool`, `args`, `timestamp`, `outcome`. | Enterprise, Compliance, Отладка |

---

## 4. Дорожная карта реализации

| Фаза | Фокус | Результат |
|------|-------|-----------|
| **Phase 0** | MCP Core + VS Code/Cursor Config | Рабочий MCP сервер, подключение к IDE, базовые инструменты |
| **Phase 1** | OpenAI Function Calling + CLI Hooks | Интеграция с Codex/Aider, рестрикт-политики, `agent hook` |
| **Phase 2** | LangChain/LlamaIndex Wrappers | Python SDK, RAG-репливатор, графовые запросы |
| **Phase 3** | Enterprise SSO + Multi-Agent Sync | OAuth2, аудит, кросс-агентная координация, Obsidian плагин |

---

## ✅ Итог
Интеграция строится на **едином стандарте (MCP Stdio)** для IDE/агентов, **REST/Function Calling** для OpenAI/Codex, и **Python SDK** для фреймворков. Ядро гарантирует безопасность через `dark_zones`, `token_budget` и строгие `roles`. Пользователь получает готовый конфиг для VS Code, Cursor, Claude Desktop и CLI-агентов за 1 команду.

**Следующий шаг:** Утвердить стратегию → начать реализацию Phase 0 (MCP Server + CLI Skeleton).

---
*Анализ проведён в рамках методологии NexusAtom*
*Дата: 2026-04-12*
*Статус: active (ожидает утверждения и перехода к кодированию MCP/CLI)*

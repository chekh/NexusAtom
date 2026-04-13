---
id: ENG-011
type: analysis
status: active
---

# Agent Discovery & Skills Protocol

## 1. Проблема
MCP — это только транспорт. Без явного протокола обнаружения и стандартизированных скиллов агенты будут "гадать", где лежит `vault/`, какие инструменты использовать и как действовать. Это ломает воспроизводимость и безопасность.

## 2. Решение: Agent Discovery Protocol
Единая точка входа: `_core/config/agent_discovery.yaml`.

### Структура конфига
```yaml
version: 1.0
vault_root: "${PROJECT_ROOT}/vault"
mcp:
  transport: stdio
  command: "nexus"
  args: ["mcp", "bootstrap", "--discovery", "auto"]
skills:
  - name: builder
    version: ">=1.0.0"
    source: "registry://nexus/skills/builder"
    local_override: "${vault_root}/_core/config/skills/builder/"
init_sequence:
  - resolve_paths
  - load_skills
  - validate_mcp_connection
  - apply_role_permissions
```

## 3. Анатомия Скилла
Скилл — это пакет поведения, а не просто промпт.

```
skills/{name}/
├── _meta.yaml              # Имя, версия, роль, описание
├── system_prompt.md        # Роль, стиль, ограничения
├── tool_mapping.yaml       # Маппинг инструментов: когда и как использовать
├── workflows/              # Пошаговые инструкции (capture_idea, review_ideas)
└── context_templates/      # Шаблоны запросов к vault
```

## 4. Безопасность и Интеграция
- **Dark Zones Enforcement**: Ядро фильтрует пути до отправки агенту.
- **Token Budget**: Саммаризация больших артефактов.
- **Bootstrap**: Команда `nexus agent bootstrap --role <role>` генерирует конфиги для IDE (VS Code, Claude Desktop).

## 5. Интеграция с IDE
Пример `.vscode/mcp.json`:
```json
{
  "mcpServers": {
    "nexus": {
      "command": "nexus",
      "args": ["mcp", "bootstrap", "--discovery", "auto"],
      "env": { "NEXUS_BOOT_ROLE": "builder" }
    }
  }
}
```

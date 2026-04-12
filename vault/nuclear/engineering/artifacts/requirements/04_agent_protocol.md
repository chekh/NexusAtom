---
id: requirement/agent_io_protocol
type: requirement
status: approved
priority: high
tags: [ai, safety, workflow]
traces:
  defines: [principle/agent_protocol]
  implements: [problem/parallel_dev_impossible]
created: 2026-04-11
---
# Требование: Протокол ввода/вывода для AI-агентов

## Описание
Агенты — полноправные участники системы. Они читают контекст, генерируют артефакты и валидируются ядром, но не обходят FSM-гейты и не пишут напрямую в файловую систему.

## Правила взаимодействия
1. **Контекст-паки**: Агенты загружают не папки, а `nexus context load --pack <role>` (например, `developer`, `researcher`, `auditor`).
2. **Захват знаний**: `nexus capture` создаёт узлы с `status: raw`. Валидация мягкая, индексация мгновенная.
3. **Эскалация**: Типы `governance`, `architecture`, `adr` требуют человеческого `approve`. Без аппрува узел не попадает в активный граф.
4. **Трассировка**: Каждое действие агента фиксируется в `traces.created_by` и `meta.session_hash`.

## Безопасность
- Агенты пишут только через API/CLI. Прямая запись в FS блокируется Git-хуками.
- Критические изменения проходят `Review Gate` (человеческий аппрув).
- `content_hash` каждого артефакта фиксируется при создании → детекция несанкционированных изменений.

## Критерии приемки
- [ ] `nexus capture --type note --content "..."` создаёт валидный узел с `status: raw`
- [ ] Агенты не могут изменить `status` на `approved` без человеческого аппрува
- [ ] `traces.created_by` содержит `agent_id` и `session_hash`
- [ ] Git-хук блокирует прямые коммиты агентов в `vault/` без использования CLI

## Зависимости
- `principle/agent_protocol` (концепция)
- `principle/git_integration` (блокировка прямых пушей)
- Система аутентификации агентов (API keys / session tokens)

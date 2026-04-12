---
id: principle/agent_protocol
type: concept
status: active
tags: [ai, workflow, safety]
traces:
  related_to: [principle/vault_ssot, principle/dynamic_registry]
---
# Протокол взаимодействия с AI-агентами

## Тезис
Агенты — полноправные участники системы. Они читают контекст, генерируют артефакты и валидируются ядром, но не обходят FSM-гейты.

## Принцип
1. Контекст-паки: агенты загружают не папки, а `nexus context load --pack <role>` (например, `developer`, `researcher`, `auditor`).
2. Захват знаний: `nexus capture` создаёт узлы с `status: raw`. Валидация мягкая, индексация мгновенная.
3. Эскалация: типы `governance`, `architecture`, `adr` требуют человеческого `approve`. Без аппрува узел не попадает в активный граф.
4. Трассировка: каждое действие агента фиксируется в `traces.created_by` и `meta.session_hash`.

## Безопасность
Агенты пишут только через API/CLI. Прямая запись в FS блокируется Git-хуками. Критические изменения проходят `Review Gate`.

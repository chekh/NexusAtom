---
id: principle/git_integration
type: concept
status: active
tags: [ci, workflow, trunk]
traces:
  related_to: [principle/atom_container, principle/agent_protocol]
---
# Git: Spec-First Trunk и изоляция доставки

## Тезис
`vault/` живёт в `main`. Ветки разработки создаются только после аппрува атома. Контракт = источник истины до написания кода.

## Принцип
1. Утверждённые атомы всегда в `main`. `feat/` ветки форкаются от актуальной спеки.
2. Манифест-трекинг: каждый коммит привязан к `atom_id` и `manifest.yaml`. CI проверяет целостность хэшей.
3. Бинарные правила: прямой пуш в `main` запрещён. Merge только через PR с пройденными статус-чеками.
4. Синхронизация: `external_refs` связывают атомы с Jira/Linear/Notion. Двусторонний вебхук обновляет статусы.

## Итог
Git фиксирует переходы. Истина живёт в `vault/`. Код — производная от утверждённого контракта.

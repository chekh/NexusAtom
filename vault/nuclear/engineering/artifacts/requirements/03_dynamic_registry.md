---
id: requirement/dynamic_type_registry
type: requirement
status: approved
priority: high
tags: [configuration, extensibility, fsm]
traces:
  defines: [principle/dynamic_registry, meta/registry]
  implements: [problem/no_planning_layer]
created: 2026-04-11
---
# Требование: Динамический реестр типов артефактов

## Описание
Типы артефактов (`atom`, `note`, `adr`, `research_log` и т.д.) не захардкожены в ядре. Они конфигурируются декларативно через `registry.yaml`, что позволяет адаптировать систему под любую процессную модель.

## Структура `registry.yaml`
```yaml
profiles:
  delivery:
    description: "Атомы поставки ценности (код, контракты, тесты)"
    required_artifacts: [spec, manifest, _meta]
    fsm_strict: true
    ci_gate: required
    archive_mode: logical

  context:
    description: "Знание, контекст, исследования, правила"
    required_artifacts: [_meta]
    fsm_strict: false
    ci_gate: optional
    archive_mode: logical

types:
  atom:
    profile: delivery
    fsm: [draft, rfc, approved, in_progress, completed, partial, deferred, archived]
    template: templates/atom.md

  note:
    profile: context
    fsm: [raw, refined, archived]
    template: templates/note.md

  research_log:
    profile: context
    fsm: [raw, analyzed, synthesized, archived]
    template: templates/research.md
```

## Правила
1. **Профили валидации**: `delivery` (строгий FSM + manifest), `context` (гибкий FSM + контент).
2. **Методологическая агностичность**: `story`, `task`, `change_request` — всё это типы из реестра.
3. **Расширяемость**: Новые типы добавляются декларативно. Ядро читает схему, строит валидатор, CLI генерирует шаблоны.

## Критерии приемки
- [ ] `nexus atom create --type {new_type}` генерирует файл по шаблону из реестра
- [ ] Валидатор проверяет переходы FSM согласно `registry.yaml`
- [ ] При добавлении нового типа не требуется перезапуск ядра
- [ ] `nexus validate --all` проверяет все артефакты против актуального реестра

## Зависимости
- `principle/dynamic_registry` (концепция)
- `meta/system.yaml` (конфигурация ядра)
- Парсер YAML + валидатор схем (Pydantic v2)

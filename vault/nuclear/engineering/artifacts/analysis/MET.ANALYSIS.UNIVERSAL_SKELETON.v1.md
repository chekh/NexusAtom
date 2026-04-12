---
id: MET.ANALYSIS.UNIVERSAL_SKELETON.v1
type: methodology_specification
status: draft
tags: [structure, portability, schema, specification]
traces:
  defines: [MET.ANALYSIS.VAULT_AS_RESOURCE.v1]
  implements: [GOV.PROTO.CONTEXT_ISOLATION.v1]
  related_to: [meta/registry.yaml, meta/system.yaml]
created: 2026-04-11
---
# Спецификация: Универсальный скелет `vault/` v2

## 1. Манифест ресурса (`_system/manifest.yaml`)

```yaml
# vault/_system/manifest.yaml
vault_schema_version: 2.0.0
name: "NexusAtom Knowledge Resource"
description: "Портативный контейнер знаний с динамической схемой"
created: 2026-04-11
updated: 2026-04-11
maintainer: "NexusAtom Core Team"

# Правила ресурса
rules:
  id_format: "^[A-Z]{2,}\\.[A-Z_]+\\.[A-Z0-9_]+\\.v\\d+$"  # Пример: MET.ANALYSIS.UNIVERSAL_SKELETON.v1
  required_metadata: [id, type, status, created]
  optional_metadata: [tags, traces, updated, owner]
  status_enum: [draft, active, deprecated, archived]  # Базовый набор, расширяется в schema.yaml

# Интеграция
integration:
  code_sync: "manifest.yaml в атомах связывает с файлами в репозитории"
  external_refs: "Поддержка ссылок на Jira, Linear, Notion через traces.external"
  export_formats: [markdown, json, graphml]  # Для обмена с другими системами

# Версионирование
versioning:
  schema_migration: "При изменении vault_schema_version предоставлять скрипт миграции"
  artifact_versioning: "Каждый артефакт имеет версию в id (.v1, .v2). Старые версии архивируются."
```

## 2. Схема ресурса (`_system/schema.yaml`)

Заменяет `meta/registry.yaml`. Определяет типы, состояния, связи, права.

```yaml
# vault/_system/schema.yaml
types:
  # Базовые типы (обязательные для любого vault/)
  note:
    description: "Краткая заметка, идея, наблюдение"
    profile: context
    states: [raw, refined, archived]
    required_fields: [content]
    allowed_traces: [related_to, inspired_by, supersedes]
    agent_permissions:
      can_create: [raw]
      can_transition: [raw→refined]
      requires_human_approval: []
  
  inquiry:
    description: "Вопрос, неопределённость, точка принятия решения"
    profile: context
    states: [open, triaged, researching, answered, archived]
    required_fields: [question, context]
    allowed_traces: [affects, answered_by, blocks]
    agent_permissions:
      can_create: [open]
      can_transition: [open→triaged, triaged→researching]
      requires_human_approval: [researching→answered]
  
  decision:
    description: "Архитектурное или процессное решение (ADR)"
    profile: governance
    states: [proposed, accepted, superseded, deprecated]
    required_fields: [context, decision, consequences]
    allowed_traces: [resolves, supersedes, related_to]
    agent_permissions:
      can_create: [proposed]
      can_transition: [proposed→accepted]
      requires_human_approval: [proposed→accepted]  # Всегда требует человека
  
  # Доменно-специфичные типы (пример для software project)
  atom:
    description: "Контейнер доставки ценности (фича, баг, рефакторинг)"
    profile: delivery
    states: [draft, rfc, approved, in_progress, completed, partial, deferred, archived]
    required_fields: [spec, manifest]
    allowed_traces: [depends_on, epic, story, adr, tests, docs]
    agent_permissions:
      can_create: [draft]
      can_transition: [draft→rfc, rfc→approved]
      requires_human_approval: [rfc→approved, approved→in_progress]
  
  # Новые типы добавляются здесь без изменения кода ядра
  research_log:
    description: "Запись исследования, эксперимента, гипотезы"
    profile: context
    states: [raw, analyzed, synthesized, archived]
    required_fields: [hypothesis, methodology, findings]
    allowed_traces: [inspired_by, tested_in, concludes]
    agent_permissions:
      can_create: [raw]
      can_transition: [raw→analyzed, analyzed→synthesized]
      requires_human_approval: [analyzed→synthesized]

namespaces:
  # Логические пространства. Каждое может иметь свои дополнительные правила.
  engineering:
    description: "Знания, связанные с разработкой ПО"
    default_types: [atom, decision, note, inquiry]
    acl:
      read: [architect, builder, auditor]
      write: [architect, builder]
      approve: [architect]
  
  business:
    description: "Бизнес-контекст: стратегия, метрики, стейкхолдеры"
    default_types: [note, inquiry, decision]
    acl:
      read: [product, architect, auditor]
      write: [product]
      approve: [product]
  
  research:
    description: "Научные исследования, эксперименты, гипотезы"
    default_types: [research_log, inquiry, note]
    acl:
      read: [researcher, architect, auditor]
      write: [researcher]
      approve: [researcher]  # Само-аппрув для research

# Глобальные ACL (переопределяются в namespaces)
global_acl:
  roles:
    architect: [read: all, write: engineering, approve: engineering]
    builder: [read: engineering, write: engineering/delivery, approve: none]
    researcher: [read: research, write: research, approve: research]
    auditor: [read: all, write: none, approve: none]
    product: [read: business, write: business, approve: business]
```

## 3. Структура папок (логическая, не обязательная)

```
vault/
├── _system/                          # Системные файлы (обязательные)
│   ├── manifest.yaml                 # Манифест ресурса
│   ├── schema.yaml                   # Схема типов, состояний, ACL
│   ├── indexing.yaml                 # Правила индексации (опционально)
│   └── migrations/                   # Скрипты миграции между версиями схемы
├── namespaces/                       # Логические пространства (конфигурируемые)
│   ├── engineering/                  # Пример: software project
│   ├── business/                     # Пример: бизнес-контекст
│   └── research/                     # Пример: научный проект
├── workspace/                        # Активная работа (обязательное)
│   ├── inbox/                        # Быстрый захват (низкий порог входа)
│   ├── drafts/                       # Черновики артефактов
│   └── current/                      # Ярлыки на активные атомы (символические ссылки)
├── archive/                          # Логический архив (обязательное)
│   # Файлы физически могут оставаться на местах, но индекс помечает их
│   # Опционально: физическое перемещение через команду
└── shared/                           # Кросс-доменные знания (обязательное)
    ├── glossary/                     # Глоссарий терминов
    ├── templates/                    # Шаблоны артефактов по типам
    └── ontologies/                   # Общие онтологии, таксономии
```

## 4. Правила именования и навигации

- **`id` артефакта**: Уникален в рамках всего `vault/`. Формат: `[PREFIX].[TYPE].[NAME].v[VERSION]`.
- **Пути в ФС**: Не являются частью `id`. Используются для человеческой навигации и контроля доступа.
- **Ссылки**: Всегда по `id`: `[[MET.ANALYSIS.UNIVERSAL_SKELETON.v1]]`. Резолвер подставляет путь.
- **Поиск**: Через индекс по метаданным (`id`, `type`, `status`, `tags`, `namespace`), не по контенту.

## 5. Контракт на вход/выход

### Импорт знаний
```bash
# Импортировать внешний Markdown-файл как артефакт
vault import --file external_doc.md --type note --namespace business --id NOTE.IMPORT.EXTERNAL.v1

# Импортировать целый набор (например, из другого vault/)
vault import --source ../other_project/vault/ --namespace engineering --merge-strategy append
```

### Экспорт знаний
```bash
# Экспортировать всё пространство в Markdown
vault export --namespace engineering --format markdown --output ./export/engineering/

# Экспортировать граф связей для визуализации
vault export --format graphml --output ./export/dependencies.graphml
```

### Синхронизация с кодом
- Атомы типа `atom` содержат `manifest.yaml`, который связывает `id` атома с файлами в репозитории.
- При коммите кода, если изменён файл из манифеста, ядро проверяет, что атом в статусе `in_progress` или `completed`.
- Обратная связь: при изменении атома (например, `spec.md`) ядро может предложить обновить связанные файлы кода (через шаблон или агент).

## 6. Миграция с v1 на v2

1.  **Добавить `_system/`**: Создать `manifest.yaml` и `schema.yaml` на основе текущего `meta/registry.yaml`.
2.  **Создать `namespaces/`**: Перенести `context/`, `meta/`, `delivery/` в соответствующие пространства (например, `engineering/`).
3.  **Обновить `workspace/`**: Переместить `funnel/` → `workspace/inbox/`.
4.  **Настроить `archive/`**: Оставить файлы на местах, но обновить индекс, чтобы по умолчанию поиск исключал `status: archived`.
5.  **Обновить ссылки**: Запустить скрипт, который заменяет старые относительные пути в `[[ ]]` на `id` (если ещё не использовались).
6.  **Протестировать**: Запустить `vault validate --all` для проверки целостности после миграции.

## 7. Критерии принятия спецификации

- [ ] Спецификация позволяет описать как минимум 3 разнородных проекта (софт, исследование, бизнес) без изменения структуры папок.
- [ ] Миграция с текущей структуры возможна без потери трассируемости (`id`, `traces`).
- [ ] Схема (`schema.yaml`) расширяема без изменения кода ядра.
- [ ] ACL система позволяет изолировать доступ по ролям/доменам.
- [ ] Контракт на импорт/экспорт реализуем через CLI (без прямого доступа к ФС).

---
*Спецификация создана в рамках методологии NexusAtom*
*Дата: 2026-04-11*
*Статус: draft (ожидает ревью экспертной панелью и утверждения)*

---
id: META.RESTRUCTURE.LOG.2026-04-11.v1
type: operational_log
status: active
tags: [restructure, migration, three_layer_architecture]
traces:
  implements: [DEC.ARCH.THREE_LAYER_MODEL.v1, DEC.ARCH.HYBRID_ARCHIVE_MODEL.v1]
created: 2026-04-11
---
# Лог реструктуризации `vault/` — 2026-04-11

## Цель
Перевести `vault/` на трёхуровневую архитектуру (Знания → Процессы → Доставка) с гибридной моделью архивации и изолированной памятью агентов.

## Выполненные изменения

### 1. Созданы системные ресурсы (L1)
- `_system/manifest.yaml` (из `meta/system.yaml`) — манифест ресурса
- `_system/schema.yaml` (из `meta/registry.yaml`) — глобальная схема типов
- `_system/nuclear_registry.yaml` (новый) — реестр ядерных ресурсов
- `_system/security_policy.yaml` (новый) — глобальная политика безопасности

### 2. Реорганизован `context/` (L1 + L2)
- `context/principles/` — принципы проекта (оставлено + добавлен `overview.md`)
- `context/memory/agents/` — изолированная память агентов (новая, пустая)
- `context/workflows/` — управление процессами (L2):
  - `governance-policies/` (из `context/governance/`)
  - `methodologies/`, `fsm-definitions/`, `routing-rules/` (новые, пустые)
- `context/history/` — хронология решений (из `meta/nuances_log.md`)
- `shared/guides/` — кросс-доменные гайды (из `context/guides/`)

### 3. Создан `workspace/` (L1)
- `workspace/inbox/` (из `context/funnel/`) — быстрый захват идей
- `workspace/drafts/`, `workspace/current/` (новые, пустые)

### 4. Создан `nuclear/engineering/` (L3 — Delivery)
- `_contract.yaml` (новый) — локальный контракт ресурса
- `dependencies.yaml` (новый) — зависимости от других ядерных ресурсов
- `_archive/` (новый) — локальный архив ресурса
- `artifacts/` — артефакты доставки, перенесены из:
  - `meta/analysis/` → `artifacts/analysis/`
  - `meta/decisions/` → `artifacts/decisions/`
  - `meta/requirements/` → `artifacts/requirements/`
  - `meta/inquiries/` → `artifacts/inquiries/`
  - `meta/reviews/` + `context/reviews/` → `artifacts/reviews/`
  - `context/problems/` → `artifacts/problems/`
  - `delivery/atom_template/` → `artifacts/templates/`
  - `AGT.PROTO...`, `CONTEXT_ISOLATION...` → `artifacts/protocols/`

### 5. Создан `archive/global/` (L1)
- Глобальный архив для комплаенса (пока пустой, индексы будут добавлены при реализации ядра)

### 6. Очищен `meta/` (L1 — операционные метаданные)
- Оставлены только служебные подпапки: `audit/`, `indexes/`, `migrations/` (все пустые)
- Весь контент перенесён в `nuclear/engineering/artifacts/` как артефакты разработки

### 7. Настроена гибридная архивация
- Архивация по умолчанию: только метаданные (`status: archived`)
- Локальный `_archive/` внутри ядерного ресурса — для мобильности
- Глобальный `archive/global/` — для комплаенса и аудита
- Автоматическое включение архивов в Зоны тьмы

## Сохранённость данных
✅ Все файлы сохранены, ни один не удалён.  
✅ Все `id` в фронтматтере сохранены (связи `[[id]]` не разорваны).  
✅ Все связи `traces.*` сохранены.  

## Обратная совместимость
⚠️ Пути файлов изменились. Если внешние инструменты ссылались на старые пути, их нужно обновить.  
✅ Ссылки `[[id]]` внутри артефактов продолжают работать (резолвер по `id`, не по пути).

## Следующие шаги
1. Закоммитить изменения с сообщением `feat(vault): restructure to 3-layer architecture`.
2. Обновить CI/CD скрипты, если они ссылались на старые пути.
3. Начать реализацию ядра: парсер `_system/`, валидатор контрактов, индексатор с Зонами тьмы.

---
*Лог создан автоматически при реструктуризации*
*Дата: 2026-04-11*
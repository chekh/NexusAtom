---
id: GOV.PROTO.CONTEXT_ISOLATION.v1
type: governance_rule
status: active
tags: [security, performance, agent, scalability]
traces:
  resolves: [INQ.AUDIT.AGENT_USABILITY.v1, REVIEW.AUDIT.SCALABILITY_RISKS.v1]
  defines: [principle/agent_protocol]
  related_to: [meta/registry.yaml, meta/system.yaml]
created: 2026-04-11
---
# Протокол: Изоляция контекста и ленивая загрузка для агентов

## Тезис
Агент не должен иметь прямого доступа к файловой системе `vault/`. Все операции чтения проходят через ядро, которое применяет фильтрацию по роли, ленивую загрузку и индекс-первый подход.

## Правила доступа

### 1. Запрет прямого чтения
- ❌ Агент не может выполнять `ls`, `grep`, `cat` в `vault/`.
- ✅ Агент использует только CLI/API: `nexus query`, `nexus resolve`, `nexus context load`.

### 2. Индекс-первый (Index-First)
- Ядро поддерживает индекс метаданных (SQLite/NetworkX).
- Индекс хранит: `id`, `type`, `status`, `summary` (первые 200 символов), `traces.*`, `content_hash`, `created_at`.
- **Полный контент файла не хранится в индексе**.
- Запросы агентов (`list`, `search`) выполняются против индекса, не файловой системы.

### 3. Ленивая загрузка (Lazy Loading)
- При запросе `nexus list --type atom --status approved` агент получает только метаданные.
- Полное содержание загружается **только** при явном вызове `nexus resolve <id>`.
- Ссылки `[[id]]` в контенте резолвятся лениво: при первом обращении к ним.

### 4. Контекст-паки (Context Packs)
- Предопределённые наборы артефактов под роль:
  ```yaml
  context_packs:
    developer:
      include_types: [atom, adr, test_plan]
      include_statuses: [approved, in_progress, completed]
      exclude_paths: [vault/context/funnel/, vault/meta/inquiries/]
    researcher:
      include_types: [research_log, note, problem]
      include_statuses: [raw, analyzed, active]
      exclude_types: [atom]  # пока не утверждено
    auditor:
      include_types: [all]
      include_statuses: [all]
      # но только метаданные, контент — по запросу
  ```
- Агент загружает пакет: `nexus context load --pack developer`.
- Ядро применяет фильтры из `registry.yaml` + `context_packs`.

### 5. Матрица доступа (ACL by Role)
- В `registry.yaml` для каждого типа указывается `read_roles`:
  ```yaml
  types:
    atom:
      profile: delivery
      read_roles: [architect, builder, auditor]
      write_roles: [architect, builder]  # только в статусе draft/rfc
    inquiry:
      profile: context
      read_roles: [architect, auditor, researcher]
      write_roles: [any]  # любой может задать вопрос
  ```
- Ядро фильтрует результаты запросов по роли агента.
- Попытка прочитать запрещённый тип → ошибка `AccessDenied`.

### 6. Запрос-ориентированный доступ (Query-Only)
- Агент не может сканировать директории.
- Все запросы — через `nexus query` с явными фильтрами:
  ```bash
  # ✅ Разрешено
  nexus query --filter "type=atom AND domain=auth AND status=approved"
  
  # ❌ Запрещено (агент не может выполнить)
  grep -r "JWT" vault/
  find vault/ -name "*.md" -exec cat {} \;
  ```

## Технические требования к ядру

| Компонент | Требование | Приоритет |
|-----------|------------|-----------|
| **Индексатор** | Сканирует `vault/`, извлекает метаданные, строит SQLite-индекс. Инкрементальное обновление при коммитах. | 🔴 Критический |
| **Роутер запросов** | Проверяет роль агента, применяет ACL, формирует безопасный SQL/графовый запрос. | 🔴 Критический |
| **Резолвер** | Загружает полный контент по `id`, резолвит `[[id]]` ссылки лениво, кэширует результаты. | 🟡 Высокий |
| **Кэш метаданных** | In-memory кэш индекса для ускорения частых запросов. TTL: 5 минут. | 🟡 Высокий |
| **Мониторинг** | Метрики: время запроса, размер возвращённого контекста, количество ленивых загрузок. | 🟢 Средний |

## Пример потока: агент-билдер работает с атомом

```bash
# 1. Агент загружает контекст-пак
nexus context load --pack developer --query "domain=auth"
# → Возвращает: 3 атома (метаданные: id, status, summary)

# 2. Агент выбирает атом для работы
nexus resolve DEL.FEAT.JWT_REFRESH.v1
# → Ядро загружает полный контент, резолвит [[id]] ссылки
# → Агент получает: spec.md, adr.md, test_plan.md (только этот атом)

# 3. Агент генерирует код, обновляет manifest
# → Коммит через `nexus commit --atom DEL.FEAT.JWT_REFRESH.v1`

# 4. Ядро обновляет индекс (инкрементально)
# → Кэш метаданных инвалидируется для этого атома
```

**Контекстное окно агента**: ~3-5 КБ (метаданные) + ~10-20 КБ (полный контент одного атома) = **<30 КБ**, независимо от размера `vault/`.

## Безопасность и аудит

- Все запросы агентов логируются: `agent_id`, `query`, `returned_ids`, `context_size_bytes`.
- Попытки доступа к запрещённым типам/статусам → алерт в `vault/meta/security/audit_log.md`.
- Регулярный аудит: `nexus audit --role builder --last-24h` показывает, какие атомы читал агент.

## Миграция и обратная совместимость

- Для существующих агентов: режим `compatibility: true` в `system.yaml` временно разрешает прямой доступ к `vault/` (с предупреждением в логах).
- После реализации ядра: `compatibility: false` → прямой доступ блокируется.

---

## Статус
✅ Активно. Применяется ко всем агентам, работающим с `vault/`.

## Связанные артефакты
- [[meta/registry.yaml]] — определение типов и `read_roles`
- [[meta/system.yaml]] — конфигурация ядра (`indexer`, `resolver`, `cache`)
- [[AGT.PROTO.CRITICAL_AUDIT.v1.md]] — протокол аудита (использует этот протокол)
- [[REVIEW.AUDIT.SCALABILITY_RISKS.v1.md]] — оценка рисков (решается этим протоколом)

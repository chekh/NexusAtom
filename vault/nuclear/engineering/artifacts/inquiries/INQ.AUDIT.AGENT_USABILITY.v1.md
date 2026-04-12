---
id: INQ.AUDIT.AGENT_USABILITY.v1
type: inquiry
status: open
tags: [audit, agent, usability, protocol]
traces:
  related_to: [principle/agent_protocol, governance/agent_workflow, meta/registry.yaml]
  blocks: [principle/agent_protocol]
created: 2026-04-11T00:00:00Z
---
# Usability для агентов: Понятны ли инструкции?

## Вопрос
Достаточно ли правил в `governance/`, чтобы агент не сломал граф при автономной работе?

## Анализ текущих инструкций

### ✅ Что есть
1. **Таблица разрешённых действий** (`agent_workflow.md`):
   ```
   | Чтение контекста | nexus context load --pack <role> | Только active/approved |
   | Захват идеи | nexus capture --type note | Статус raw |
   | Генерация черновика | nexus atom create --from-research | Статус draft |
   ```

2. **Таблица запрещённых действий**:
   ```
   | Прямая запись в vault/ | Обходит валидацию | Использовать CLI |
   | Изменение status на approved | Требует человеческого суждения | Оставить draft/rfc |
   ```

3. **Протокол эскалации** (5 шагов от генерации до аппрува).

4. **Пример сценария** (агент добавляет исследование).

### ❌ Чего не хватает

#### 1. Не определены границы «критичности»
> «Если тип критический (adr, governance, architecture) → требует человеческого аппрува»

❓ **Вопросы**:
- Где список «критических типов»? В `registry.yaml`? В отдельном файле?
- Может ли агент предлагать изменения в этот список?
- Что если агент не знает, критичен ли тип? (например, новый тип добавлен в реестр)

#### 2. Нет спецификации ошибок и восстановления
> «При отклонении → агент получает фидбек, может перегенерировать»

❓ **Вопросы**:
- В каком формате фидбек? Текст? Структурированный объект?
- Какие ошибки фатальные (агент должен остановиться), а какие — предупреждения?
- Есть ли лимит попыток перегенерации? Что при превышении?

#### 3. Не описано поведение при конфликтах
> «Агенты пишут только в свои feat/ ветки. Конфликты решаются через rebase --onto spec/{id}»

❓ **Вопросы**:
- Как агент детектирует конфликт? (через Git API? через ядро?)
- Если два агента одновременно создают атомы с зависимостями — кто приоритетнее?
- Что если `depends_on` атом ещё не `completed`, но уже в `in_progress`?

#### 4. Нет чёткого контракта для «контекст-паков»
> «Агенты загружают не папки, а `nexus context load --pack <role>`»

❓ **Вопросы**:
- Где определены доступные паки (`developer`, `researcher`, `auditor`)?
- Может ли агент запрашивать кастомный пак? С какими ограничениями?
- Что если пак содержит противоречивые инструкции?

#### 5. Не описана трассировка действий агента
> «Каждое действие агента фиксируется: agent_id, session_hash, timestamp, artifact_id»

❓ **Вопросы**:
- Где хранится аудит-лог? Отдельный файл? База данных?
- Может ли агент читать свой лог для самокоррекции?
- Как долго хранятся логи? Есть ли ротация?

## Предложение: Добавить `agent_contract.yaml`

Создать явный контракт для агентов в `vault/meta/agent_contract.yaml`:

```yaml
agent_contract:
  version: 1.0
  critical_types: [adr, governance_rule, architecture_overview]
  
  error_handling:
    format: structured_json
    fatal_errors: [invalid_fsm_transition, missing_required_field, circular_dependency]
    warning_errors: [deprecated_field_used, low_confidence_suggestion]
    max_retries: 3
    retry_backoff: exponential
  
  conflict_resolution:
    detection: via_core_api
    priority_rules:
      - human_override > agent_auto
      - approved_atom > draft_atom
      - earlier_timestamp > later_timestamp (при равном приоритете)
  
  context_packs:
    developer:
      includes: [principle/atom_container, principle/git_integration, delivery/**]
      excludes: [governance/**, meta/decisions/**]
    researcher:
      includes: [context/research/**, context/problems/**]
      excludes: [delivery/**]
    auditor:
      includes: [**]  # полный доступ для аудита
      read_only: true
  
  audit_log:
    location: vault/meta/audit/agent_actions.log
    format: json_lines
    retention_days: 90
    agent_readable: false  # агенты не читают логи других агентов
```

## Блокирующий статус
🟡 Этот вопрос **не блокирует полностью**, но создаёт риск некорректного поведения агентов. 
Рекомендуется закрыть до начала автономной работы агентов.

## Связанные артефакты
- [[INQ.AUDIT.CONTRADICTION_FSM_STRICTNESS.v1]] — вопрос о границах гибкости FSM
- [[PROB.AUDIT.GAP_MISSING_CORE.v1]] — отсутствие CLI/API для безопасного взаимодействия

---
*Вопрос зафиксирован в рамках критического аудита*
*Ссылка на родительский запрос: [[INQ.AUDIT.AUDITOR_READY.v1]]*

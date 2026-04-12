---
id: MET.GUIDE.VAULT_LAYER_MAPPING.v1
type: methodology_guide
status: active
tags: [guide, mapping, onboarding, reference]
traces:
  defines: [DEC.ARCH.THREE_LAYER_MODEL.v1]
  related_to: [MET.ANALYSIS.THREE_LAYER_ARCHITECTURE.v1]
created: 2026-04-11
---
# Гайд: Сопоставление уровней архитектуры с путями `vault/`

> Этот документ — быстрая справка для онбординга. Показывает, где в файловой системе `vault/` живут компоненты каждого из трёх уровней архитектуры.

---

## 🟦 Уровень 1: Ядро знаний (Vault Core)
**Назначение:** Универсальная база знаний, индексация, безопасность, память агентов.

| Концепция | Путь в `vault/` | Файл/Папка | Назначение |
|-----------|----------------|------------|------------|
| Манифест ресурса | `_system/` | `manifest.yaml` | Версия схемы, правила, поддерживаемые версии |
| Глобальная безопасность | `_system/` | `security_policy.yaml` | Запрещённые типы, глобальные Зоны тьмы, шифрование |
| Реестр ядерных ресурсов | `_system/` | `nuclear_registry.yaml` | Указатели на активные `nuclear/` + зависимости |
| Принципы проекта | `context/principles/` | `*.md` | Статические ценности, гайдлайны, глоссарий |
| Память агентов | `context/memory/agents/{id}/` | `short_term/`, `long_term/`, `_meta.yaml` | Динамические знания агентов, изолированные от принципов |
| Аудит и индексы | `meta/` | `audit/`, `indexes/`, `migrations/` | Логи изменений, кэши индексов, скрипты миграции |
| Активная работа | `workspace/` | `inbox/`, `drafts/`, `current/` | Быстрый захват, черновики, ярлыки на активные артефакты |
| Архив | `archive/` | (логический) | Артефакты со `status: archived`, исключаются из поиска по умолчанию |

**Ключевые команды (когда ядро реализовано):**
```bash
vault validate --all                      # Валидация всех артефактов против контрактов
vault search --query "аутентификация"     # Семантический поиск (исключая Зоны тьмы)
vault agent memory-stats --id researcher  # Статистика памяти конкретного агента
vault dark-zones --list                   # Показать активные Зоны тьмы и их обоснование
```

---

## 🟨 Уровень 2: Управление процессами (Orchestration Layer)
**Назначение:** Правила, методологии, FSM, маршрутизация задач.

| Концепция | Путь в `vault/` | Файл/Папка | Назначение |
|-----------|----------------|------------|------------|
| Методологии | `context/workflows/methodologies/` | `agile.yaml`, `research.yaml`, `kanban.yaml` | Конфигурация процессов: этапы, роли, артефакты |
| Машины состояний | `context/workflows/fsm-definitions/` | `atom_fsm.yaml`, `inquiry_fsm.yaml` | Допустимые переходы статусов для типов артефактов |
| Маршрутизация | `context/workflows/routing-rules/` | `review_routing.yaml`, `approval_chains.yaml` | Кто ревьюит, кто аппрувит, куда эскалировать |
| Политики управления | `context/workflows/governance-policies/` | `quality_gates.yaml`, `dark_zone_audit.yaml` | Требования к качеству, аудит Зон тьмы, этика |

**Ключевые команды:**
```bash
vault workflow list --active              # Показать активные методологии
vault fsm trace --type atom --id DEL.FEAT.JWT.v1  # Показать текущий статус и допустимые переходы
vault route --artifact INQ.SEC.LOGIN.v1   # Показать, кому направлен запрос на ревью
vault audit --dark-zone-violations        # Показать попытки обхода Зон тьмы
```

---

## 🟥 Уровень 3: Доставка ценности (Delivery Layer)
**Назначение:** Конкретные артефакты, производящие ценность: код, отчёты, решения.

| Концепция | Путь в `vault/` | Файл/Папка | Назначение |
|-----------|----------------|------------|------------|
| Контракт ресурса | `nuclear/{resource_id}/` | `_contract.yaml` | Локальные типы, права, Зоны тьмы, векторизация |
| Зависимости ресурса | `nuclear/{resource_id}/` | `dependencies.yaml` | Какие другие `nuclear/` требуются для работы |
| Артефакты доставки | `nuclear/{resource_id}/artifacts/{artifact_id}/` | `spec.md`, `adr.md`, `test_plan.md`, `manifest.yaml` | Конкретные контейнеры ценности (атомы, исследования, юридические брифы) |
| Манифест привязки | `.../artifacts/{id}/` | `manifest.yaml` | Связь абстрактного артефакта с физическими файлами в репозитории |

**Ключевые команды:**
```bash
vault nuclear list --with-contracts       # Показать ядерные ресурсы и их контракты
vault artifact create --type atom --nuclear engineering  # Создать новый атом в ресурсе
vault manifest validate --artifact DEL.FEAT.JWT.v1       # Проверить целостность манифеста
vault export --nuclear engineering --format markdown     # Экспортировать ресурс для копирования
```

---

## 🔗 Как уровни взаимодействуют (поток данных)

```
[Идея] 
  ↓ (захват в L1)
workspace/inbox/idea.md → status: raw
  ↓ (маршрутизация L2)
workflow: research_methodology → FSM: raw → proposed
  ↓ (создание контейнера L3)
nuclear/research/ с _contract.yaml + dark_zones (если нужно)
  ↓ (исполнение L3 + валидация L1)
Агенты пишут findings → L1 валидирует контракт, индексирует без Зон тьмы
  ↓ (переход к доставке L2)
FSM: approved → in_progress → workflow: product_dev
  ↓ (создание атома L3)
nuclear/engineering/artifacts/auth_v2/ → manifest.yaml → код → CI → release
  ↓ (архивация L1)
status: completed → archive/ (логически), индекс обновляется
```

---

## 🎯 Чек-лист: «На каком я уровне?»

| Вопрос | Если «Да» → Вы на уровне |
|--------|-------------------------|
| Вы работаете с `_system/`, `context/principles/`, `context/memory/`? | 🟦 L1: Ядро знаний |
| Вы редактируете `context/workflows/methodologies/`, `fsm-definitions/`? | 🟨 L2: Управление процессами |
| Вы создаёте/меняете файлы в `nuclear/`, `_contract.yaml`, `manifest.yaml`? | 🟥 L3: Доставка ценности |
| Вы настраиваете `dark_zones` в `_contract.yaml`? | 🟥 L3 (определение) + 🟨 L2 (аудит) + 🟦 L1 (применение) |
| Вы добавляете новый тип артефакта в `_system/schema.yaml`? | 🟦 L1 (глобальные типы) |
| Вы добавляете новый тип артефакта в `nuclear/.../_contract.yaml`? | 🟥 L3 (локальные типы) |

---

## ⚠️ Частые ошибки и как их избежать

| Ошибка | Почему плохо | Как правильно |
|--------|-------------|---------------|
| Писать принципы проекта в `nuclear/engineering/` | Принципы — статика, должны быть в `context/principles/`, доступны всем ресурсам | Принципы → `context/principles/`, специфичные для ресурса правила → `nuclear/.../_contract.yaml` |
| Определять процесс в `_contract.yaml` ядерного ресурса | Процесс — это L2, контракт ресурса — L3. Смешение усложняет смену методологии | Процесс → `context/workflows/methodologies/`, контракт ресурса → только типы/права/Зоны тьмы |
| Пытаться прочитать Зону тьмы через семантический поиск | Зоны тьмы исключаются из векторного индекса на уровне L1 | Использовать `vault dark-zones --list` для понимания ограничений, запрашивать доступ через процесс аудита (L2) |
| Хранить память агентов в `context/principles/` | Память — динамика, принципы — статика. Смешение ломает экспорт и шифрование | Память → `context/memory/agents/`, принципы → `context/principles/` |

---

## 🚀 Быстрый старт для нового проекта

1.  **Инициализация ядра (L1):**
    ```bash
    vault init --profile minimal  # Создаёт _system/, context/principles/, meta/, workspace/
    ```
2.  **Выбор методологии (L2):**
    ```bash
    vault workflow enable research  # Копирует context/workflows/methodologies/research.yaml в активные
    ```
3.  **Добавление ядерного ресурса (L3):**
    ```bash
    vault nuclear add --template research  # Создаёт nuclear/research/ с _contract.yaml и шаблонами
    ```
4.  **Начало работы:**
    ```bash
    vault capture "Идея для исследования" --type note  # Захват в workspace/inbox/
    ```

---

> **Помните:** Уровни — это логические границы, не физические барьеры. Файлы могут «путешествовать» между уровнями через определённые процессы (например, идея из `workspace/` (L1) становится атомом в `nuclear/` (L3) через процесс в `context/workflows/` (L2)). Главное — соблюдать контракты каждого уровня.

---
*Гайд создан в рамках методологии NexusAtom*
*Дата: 2026-04-11*
*Статус: active (обновляется при изменении архитектуры)*

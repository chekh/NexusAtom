---
id: architecture/overview
type: overview
status: active
tags: [core, navigation, reactor]
traces:
  aggregates: [principle/atom_container, principle/vault_ssot, principle/dynamic_registry, principle/logical_archiving, principle/agent_protocol, principle/git_integration]
---
# Архитектура NexusAtom: Обзор

> `Controlled energy for complex delivery.`

## 🧭 Навигация по принципам
{{query: type=concept status=active path=vault/context/principles render=summary}}
- [[principle/atom_container]] — Атом как контейнер доставки
- [[principle/vault_ssot]] — Vault как единый источник истины
- [[principle/dynamic_registry]] — Динамический реестр типов
- [[principle/logical_archiving]] — Логическая архивация
- [[principle/agent_protocol]] — Протокол AI-агентов
- [[principle/git_integration]] — Spec-First Trunk

## ⚛️ Метафора Реактора
- **Атом** = единица знания/доставки
- **Реактор** = ядро оркестратора + индексатор
- **Критическая масса** = порог готовности к merge (`approved + manifest + tests`)
- **Цепная реакция** = автопропагация изменений и инвалидация кэша
- **Регулирующие стержни** = FSM-гейты + CI-чеки
- **Модератор** = Human-in-the-loop

## 🔄 Жизненный цикл узла
```
raw → refined → approved → in_progress → completed → archived
          ↓           ↓           ↓
      (контекст)   (доставка)  (история)
```

## 🛠 Статус системы
- Типы: сконфигурированы в `meta/registry.yaml`
- Профили: `delivery`, `context`
- Архивация: логическая (статус), ID-ссылки
- Агенты: через `context packs` + `capture/validate`
- Git: `main` хранит `vault/`, код в `feat/`

{{query: type=concept status=deprecated render=compact with_successor=true}}
*Актуальных устаревших принципов нет.*

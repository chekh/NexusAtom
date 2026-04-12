---
id: problem/parallel_dev_impossible
type: problem_statement
status: active
tags: [parallelism, concurrency, git]
traces:
  resolved_by: [principle/git_integration, principle/atom_container]
  related_to: [requirement/worktree_isolation]
created: 2026-04-11
---
# Проблема: Параллельная работа в OpenSpec невозможна

## Тезис
OpenSpec архитектурно не рассчитан на мультиагентную или командную параллельную разработку.

## Механика сбоя
1. **Раздвоение точки правды**: Во время разработки истина = `specs/` (база) + `changes/` (дельты). Пока дельта не применена, её не существует для других агентов.
2. **Отсутствие графа**: OpenSpec не знает, что `changes/order-execution` зависит от `changes/signal-api`.
3. **CLI последователен**: `opsx:apply` и `opsx:archive` работают линейно. Нет `--resolve-deps`, нет очереди, нет блокировок.
4. **Контекст устаревает мгновенно**: Агент загрузил спеку → начал кодить → другой агент смёржил дельту → контракт изменился → код первого стал невалидным.

## Сценарий отказа
```
Агент 1: changes/feat-A/trading.md (добавляет поле volume в Signal)
Агент 2: changes/feat-B/trading.md (использует Signal, но без volume)
Результат:
- merge conflict в одном файле
- если force-merge: Pydantic валидация падает, тесты не проходят
- если sequential: Агент 2 блокируется → параллелизм исчезает
```

## Решение в NexusAtom
- **Spec-First Trunk**: Утверждённые атомы в `main`, код в `feat/`.
- **Worktree isolation**: Каждый агент работает в изолированном окружении (`git worktree`).
- **DAG Scheduler**: Топологическая сортировка зависимостей перед стартом.
- **Contract versioning**: Вместо правки `SignalV2` → создание `SignalV2.1` с `extends`.
- **Context invalidation**: Вебхук/событие, сбрасывающее кэш зависимых агентов при `archive`.

## Статус
✅ Архитектурно решено. Требует реализации `worktree` менеджера и DAG-резолвера.

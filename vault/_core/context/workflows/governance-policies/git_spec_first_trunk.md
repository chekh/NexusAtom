---
id: governance/git_spec_first_trunk
type: governance_rule
status: active
tags: [git, workflow, ci]
traces:
  defines: [principle/git_integration]
  implements: [requirement/atom_as_container]
created: 2026-04-11
---
# Правило: Spec-First Trunk для управления ветками

## Тезис
Утверждённые атомы всегда в `main`. Ветки реализации создаются только после `status: approved`. Контракт = источник истины до написания кода.

## Правила

### 1. Создание ветки
```bash
# ❌ Запрещено: создавать feat/ до аппрува атома
git checkout -b feat/my-feature  # если атом не approved → ошибка

# ✅ Разрешено: после аппрува
nexus atom approve vault/delivery/auth/jwt/v1
git checkout -b feat/auth_jwt_v1 main
```

### 2. Коммиты
- Формат: `<type>(<atom_id>): <summary>`
- Пример: `feat(auth/jwt/v1): add refresh endpoint`
- Тело коммита: обязательно `origin_spec`, `content_hash`, `fsm_transition`.
- 1 коммит = 1 атом или 1 связанный артефакт (код/тест/док).

### 3. Мердж и архивация
- **Полный архив** → `squash and merge` в `main`. Атом перемещается `changes/ → atoms/`, статус `completed`.
- **Частичный архив** (`--partial`) → создаётся PR с автогенерированными атомами-преемниками (`backlog/`, `tech_debt/`). Мерджится только `completed` часть.
- **Откат** → `git revert` коммита архивации. Система автоматически возвращает атом в `in_progress` и инвалидирует кэш.

### 4. Параллельность
- **Изоляция**: агенты пишут только в свои `feat/` ветки. Конфликты решаются через `rebase --onto spec/{id}`.
- **Блокировки**: если `depends_on` не в `completed`, CI держит PR в статусе `blocked`. Ручной форс-мердж запрещён хуком.
- **Разрешение коллизий**: приоритет у `content_hash`. При совпадении хэшей → авто-ребейз + валидация графа. Если граф ломается → PR отклоняется с диагностикой.

### 5. Тегирование и релизы
- Теги ставятся на **состояние спеков**, а не только на код: `specs/v2.1.0`, `roadmap/m3-q2`.
- Семвер привязан к контрактам:
  - `MAJOR` → breaking change в `api_contract` (удаление/переименование поля)
  - `MINOR` → новый атом или `extends` без ломки
  - `PATCH` → исправление сценария, тестов, документации

## Интеграция с CI
```yaml
# .github/workflows/spec-validate.yml
name: Spec Validation
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: nexus validate --all  # Валидация против registry.yaml
      - run: nexus check-manifests  # Проверка целостности манифестов
      - run: nexus check-graph  # Детекция циклов, битых ссылок
```

## Нарушения
| Нарушение | Реакция системы |
|-----------|----------------|
| Прямой пуш в `main` | Git ruleset блокирует + алерт в чат |
| Коммит без `atom_id` в заголовке | `pre-commit` хук отклоняет + подсказка формата |
| Изменение `manifest.yaml` без обновления кода | CI-чек `check-manifests` падает + список расхождений |
| Циклическая зависимость в графе | `nexus check-graph` детектирует + предлагает разрыв |

## Статус
✅ Активно. Применяется ко всем коммитам в `vault/` и `src/`.

---
id: ENG-023
type: analysis
status: active
tags: [architecture, review, workflow]
traces:
  analyzes: [vault/context, vault/meta, vault/delivery]
  related_to: [principle/vault_ssot, principle/atom_container, principle/dynamic_registry]
created: 2026-04-11
---
# Анализ структуры `vault/` и клиентский путь

## 📊 Текущая структура

```
vault/
├── context/                          # Знание, правила, проблемы
│   ├── principles/                   # 6 архитектурных принципов
│   ├── architecture/                 # Обзорные документы
│   ├── problems/                     # Выявленные проблемы (критика OpenSpec)
│   └── governance/                   # Правила процесса (git, агенты, CI)
├── meta/                             # Мета-информация системы
│   ├── registry.yaml                 # Реестр типов, профилей, FSM
│   ├── system.yaml                   # Конфигурация ядра
│   ├── requirements/                 # Требования к ядру (4 документа)
│   ├── decisions/                    # ADR (4 решения)
│   └── nuances_log.md                # Журнал эволюции концепции
└── delivery/                         # Атомы доставки (пока пуст, есть шаблон)
    └── atom_template/
        └── _template.md
```

---

## ✅ Оценка: Логичность и непротиворечивость

| Критерий | Оценка | Обоснование |
|----------|--------|-------------|
| **Разделение ответственности** | ✅ Сильное | `context/` (знание), `meta/` (управление системой), `delivery/` (исполнение) — чёткие границы |
| **Иерархичность** | ✅ Оптимальная | Глубина 3-4 уровня. Не плоская (хаос), не глубокая (бюрократия) |
| **Связность** | ✅ Высокая | Каждый файл имеет `_meta.yaml` с `traces.*`, `id`, `status`. Граф строится автоматически |
| **Расширяемость** | ✅ Конфигурируемая | `registry.yaml` позволяет добавлять типы без смены структуры папок |
| **Поиск и навигация** | ✅ ID-based + фильтрация | `[[id]]` ссылки, `type`, `status`, `tags` — достаточно для точного поиска |
| **Целостность при росте** | ✅ Логическая архивация | Файлы не двигаются. `status: archived` скрывает из активного поиска, сохраняет историю |

### ⚠️ Обнаруженные нюансы (требуют внимания)

| Нюанс | Влияние | Решение |
|-------|---------|---------|
| **`context/governance/` пока пуст** (кроме git-правила) | Нет правил для агентов, CI, ревью | Добавить `agent_workflow.md`, `ci_rules.md`, `review_protocol.md` |
| **`delivery/` пуст** | Нет примеров рабочих атомов | Создать первый атом-доставку (например, `vault/delivery/core/parser/v1/`) |
| **`_meta.yaml` не везде** | Принципы/требования/ADR имеют фронтматтер в Markdown, но нет отдельного `_meta.yaml` | **Решение**: Для лёгких узлов фронтматтер в `.md` допустим. Для `delivery`-атомов — отдельный `_meta.yaml` обязателен |
| **Нет `research/` или `funnel/`** | Некуда быстро кидать сырые идеи/заметки | Добавить `vault/context/funnel/` для быстрого захвата |
| **`nuances_log.md` монолитный** | При росте станет нечитаемым | Разбить на `vault/meta/nuances/2026-04-11.md`, `2026-04-12.md` и т.д. |

---

## 🔄 Как будет развиваться структура

### Фаза 1: Концепция (сейчас)
- ✅ Принципы, требования, ADR, реестр
- ❌ Нет реальных атомов доставки
- ❌ Нет ядра (парсер, валидатор, CLI)

### Фаза 2: Ядро (следующая)
- ✅ Парсер `vault/` → индекс
- ✅ Резолвер ссылок `[[id]]`
- ✅ Валидатор против `registry.yaml`
- ✅ CLI: `list`, `trace`, `create`, `validate`
- ✅ Первый атом доставки: `vault/delivery/core/parser/v1/`

### Фаза 3: Интеграция
- ✅ Git-хуки (pre-commit валидация)
- ✅ GitHub Actions (CI-чеки)
- ✅ Вебхук к Linear/Jira (синхронизация статусов)
- ✅ Агенты пишут через `nexus capture`

### Фаза 4: Масштабирование
- ✅ Динамический рендеринг `{{query: ...}}` в обзорах
- ✅ Графовый движок (NetworkX/Neo4j)
- ✅ Worktree-менеджер для параллельных агентов
- ✅ Дашборд «реактора» (метрики, Mass Index, Reaction Rate)

---

## 🧭 Путь клиента (пользователя)

### Сценарий 1: Быстрая идея (30 секунд)
```bash
# Ты в метро, пришла мысль
echo "Добавить хеджирование через опционы при волатильности > 30%" >> vault/context/funnel/2026-04-11_14-30.md

# Или через CLI (когда будет реализован)
nexus capture --type note --content "Хеджирование через опционы при VIX > 30%"
# → Автоматически создаёт файл с _meta.yaml, id, status: raw
```

### Сценарий 2: Исследование → Эпик → Атом (несколько дней)
```bash
# 1. Создаёшь исследование
nexus create --type research_log --id research/options_hedge_study
# → vault/context/research/options_hedge_study/
# → Наполняешь: hypothesis.md, data.md, findings.md

# 2. Синтезируешь в эпик
nexus promote research/options_hedge_study → vault/roadmap/epics/options_hedge_v1/
# → Копирует выводы, создаёт epic с метриками, списком атомов

# 3. Декомпозируешь на атомы
nexus decompose vault/roadmap/epics/options_hedge_v1/ 
  --output delivery
# → Генерирует:
#    vault/delivery/options/pricing/v1/
#    vault/delivery/options/risk_limits/v1/
#    vault/delivery/options/execution/v1/
```

### Сценарий 3: Работа с атомом доставки (спринт)
```bash
# 1. Берёшь атом
nexus atom open vault/delivery/options/pricing/v1/
# → Показывает: spec.md, adr.md, test_plan.md, tasks.md

# 2. Аппрувишь
nexus atom approve vault/delivery/options/pricing/v1/
# → status: approved, разблокирует создание ветки

# 3. Создаёшь ветку
nexus atom start vault/delivery/options/pricing/v1/
# → git checkout -b feat/options_pricing_v1 main

# 4. Работаешь, коммитишь
# → Каждый коммит привязан к атому, manifest.yaml обновляется

# 5. Завершаешь
nexus atom complete vault/delivery/options/pricing/v1/
# → status: completed, обновляет epic, синкает с Jira/Linear
```

### Сценарий 4: Навигация и поиск
```bash
# Найти все активные концепции
nexus list --type concept --status active

# Проследить происхождение атома
nexus trace vault/delivery/options/pricing/v1/ --direction upstream
# → research/options_hedge_study → epic/options_hedge_v1 → atom/pricing/v1

# Найти всё по тегу
nexus search --tag options --include-archived

# Отрендерить обзор
nexus render vault/context/architecture/overview.md
# → Заменяет {{query: ...}} на актуальные выдержки из графа
```

---

## 🔗 Как связывать записи (сейчас и далее)

### Сейчас (вручную, через Markdown)
1. **Wiki-ссылки**: `[[id]]` в контенте.
   ```markdown
   Это решение основано на [[principle/atom_container]] и разрешает проблему [[problem/openspec_monolith]].
   ```
2. **Фронтматтер `traces`**:
   ```yaml
   traces:
     resolves: [problem/openspec_monolith]
     related_to: [principle/vault_ssot]
     supersedes: [spec/old_approach]
   ```
3. **Теги**: `tags: [core, delivery, ssot]` — для фильтрации.

### Далее (автоматически, через ядро)
1. **Резолвер `[[id]]`**: При рендеринге/чтении подставляет путь + статус + превью.
2. **Граф-билдер**: Автоматически строит DAG по `traces.*` и `[[id]]`.
3. **Валидатор связей**: При коммите проверяет, что все `[[id]]` существуют, нет циклов, статусы совместимы.
4. **Обратные ссылки**: Автоматически показывает, кто ссылается на текущий узел.

---

## 📥 Куда добавлять новую информацию

| Тип контента | Куда | Формат | Статус по умолчанию |
|--------------|------|--------|---------------------|
| **Сырая идея/заметка** | `vault/context/funnel/` | `.md` с фронтматтером | `raw` |
| **Исследование** | `vault/context/research/{id}/` | Папка: `hypothesis.md`, `findings.md`, `_meta.yaml` | `raw` |
| **Проблема** | `vault/context/problems/` | `.md` с фронтматтером | `active` |
| **Требование к системе** | `vault/meta/requirements/` | `.md` с фронтматтером | `draft` |
| **Архитектурное решение (ADR)** | `vault/meta/decisions/` | `.md` с фронтматтером | `proposed` |
| **Атом доставки (фича/баг)** | `vault/delivery/{domain}/{id}/` | Папка: `_meta.yaml`, `spec.md`, `adr.md`, `manifest.yaml` | `draft` |
| **Правило процесса** | `vault/context/governance/` | `.md` с фронтматтером | `draft` |
| **Обзорный документ** | `vault/context/architecture/` | `.md` с `{{query: ...}}` шаблонами | `draft` |

---

## 🛠 Как добавлять информацию (практика)

### Быстрый способ (сейчас, без CLI)
1. Создай файл в нужной папке.
2. Скопируй фронтматтер из ближайшего аналога.
3. Заполни `id`, `type`, `status`, `tags`, `traces`.
4. Напиши контент.
5. Закоммить: `git add vault/... && git commit -m "docs(vault): add ..."`

### Через CLI (когда будет реализован)
```bash
# 1. Создать узел
nexus create --type note --id funnel/quick_idea_042 \
  --content "Добавить поддержку WebSocket для стриминга сигналов"

# 2. Добавить связи
nexus link funnel/quick_idea_042 --to principle/atom_container --type inspires

# 3. Промоутить в атом
nexus promote funnel/quick_idea_042 → vault/delivery/infra/ws_streaming/v1/

# 4. Валидировать
nexus validate --all
```

---

## ✅ Итог: Структура логична и непротиворечива

| Сильная сторона | Почему работает |
|-----------------|----------------|
| **Разделение `context/meta/delivery`** | Знание, управление, исполнение — не смешиваются |
| **ID-based навигация** | Ссылки не ломаются при росте, архивации, рефакторинге |
| **Динамический реестр** | Новые типы добавляются без смены структуры папок |
| **Логическая архивация** | История сохраняется, активная зона не захламляется |
| **Журнал нюансов** | Концепция документируется в процессе, не постфактум |

| Что добавить в ближайших итерациях | Приоритет |
|-----------------------------------|-----------|
| `vault/context/funnel/` для быстрого захвата идей | 🔴 Высокий |
| Разбить `nuances_log.md` на файлы по датам | 🟡 Средний |
| Первый реальный атом доставки (`core/parser/v1`) | 🔴 Высокий |
| Правила для агентов (`governance/agent_workflow.md`) | 🟡 Средний |
| CLI: `create`, `list`, `trace`, `validate` | 🔴 Высокий |

**Вердикт**: Структура готова к использованию. Ядро (парсер, валидатор, CLI) превратит её из «документации» в «работающую систему».

---
id: ENG-016
type: analysis
status: active
---

# Global Asset Store Strategy

## 1. Концепция
Разделение хранилищ на **Локальное (Local Registry)** и **Глобальное (Global Marketplace)**.

| Уровень | Название | Роль |
|---------|----------|------|
| **L1: Локальное** | `asset_registry` | Кастомизации, переопределения, черновики. Живет внутри `vault/`. |
| **L2: Глобальное** | `Nexus Hub` | Публикация, версионирование, доверие. Отдельный сервис/репо. |

## 2. Архитектура Магазина (Nexus Hub)

### Федеративная модель реестров
Система поддерживает множественные источники (`sources.yaml`):
```yaml
sources:
  - name: official
    url: "registry://nexus-atom/official"
    trust_level: high
  - name: community
    url: "registry://nexus-atom/community"
    trust_level: medium
```

### Поток установки
1. `nexus search skill <name> --source all`
2. `nexus install skill <name>@version`
3. Файлы скачиваются в кэш и линкуются в проект.
4. Версии фиксируются в `lock.yaml`.

## 3. Безопасность
- **Подпись:** Скиллы подписываются автором.
- **Sandboxing:** Исполнение только через API ядра.
- **Аудит:** `nexus audit` проверяет промпты на инъекции.

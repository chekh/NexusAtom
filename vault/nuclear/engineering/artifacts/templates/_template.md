---
id: template/atom
type: template
status: active
tags: [delivery, boilerplate, generation]
traces:
  used_by: [requirement/atom_as_container]
created: 2026-04-11
---
# Шаблон атома доставки

> Этот файл — шаблон для генерации новых атомов через `nexus atom create`. Не редактировать вручную.

```markdown
---
id: {{domain}}/{{name}}/v{{version}}
type: atom
status: draft
version: "{{version}}"
domain: "{{domain}}"
title: "{{title}}"
description: "{{description}}"
owner: "{{owner}}"
created: "{{date}}"
depends_on: []
traces:
  epic: []
  story: []
  adr: []
  tests: []
  docs: []
external_refs:
  jira: null
  linear: null
  notion: null
---
# {{title}}

## Контекст
{{Введение: бизнес-цель, пользователи, ограничения}}

## Спецификация (Spec)
{{Требования, сценарии (Gherkin), API-контракт}}

```python
# API Contract (Pydantic v2)
from pydantic import BaseModel, Field

class {{ModelName}}(BaseModel):
    {{fields}}
```

## Архитектурное решение (ADR)
{{Почему выбран этот подход? Какие альтернативы рассмотрены?}}

## План тестирования (Test Plan)
{{Сценарии тестов, критерии приемки, данные}}

## План реализации (Tasks)
- [ ] {{Задача 1}}
- [ ] {{Задача 2}}
- [ ] {{Задача 3}}

## Манифест (Manifest)
{{Список файлов в репозитории, которые изменит этот атом}}
```

## Правила заполнения
1. `id`: Формат `{{domain}}/{{name}}/v{{version}}`. Уникален в рамках `vault/`.
2. `depends_on`: Список `id` атомов, от которых зависит этот. Граф проверит циклы.
3. `traces.*`: Ссылки на эпики, стори, ADR, тесты, доки. Используется для навигации и агрегации.
4. `external_refs`: Привязка к внешним трекерам (Jira/Linear). Для синхронизации статусов.
5. Секции `Spec`, `ADR`, `Test Plan` — обязательны для профиля `delivery`.
6. `manifest.yaml` генерируется автоматически при первом коммите кода.

## Пример использования
```bash
nexus atom create \
  --type atom \
  --domain auth \
  --name jwt_refresh \
  --version 1 \
  --title "Реализация обновления JWT-токена" \
  --description "Добавить эндпоинт /auth/refresh для пролонгации сессии" \
  --owner alice
```

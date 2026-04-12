---
id: template/funnel_note
type: template
status: active
tags: [template, funnel, quick_capture]
traces:
  used_by: [meta/structure_analysis]
created: 2026-04-11
---
# Шаблон быстрой заметки (Funnel)

> Для быстрого захвата идей, заметок, наблюдений. Не требует строгой валидации.

```markdown
---
id: funnel/{{short_id}}
type: note
status: raw
tags: []
created: {{date}}
traces:
  inspired_by: []
  related_to: []
---
# {{title}}

{{Контент: сырая мысль, наблюдение, вопрос, ссылка}}

## Контекст
{{Откуда пришла идея? Какая проблема/возможность?}}

## Следующие шаги
- [ ] {{Действие 1}}
- [ ] {{Действие 2}}
```

## Правила
1. `id`: Уникальный, краткий, без пробелов. Пример: `funnel/ws_streaming_idea`.
2. `status`: Всегда `raw` при создании. Меняется на `refined` при анализе, `archived` при отклонении.
3. `traces`: Добавляй связи, если видишь отношение к другим узлам. Не обязательно при быстром захвате.
4. **Не перегружай**: Это черновик. Детали — в `research/` или `delivery/`.

## Пример использования
```bash
# Вручную
echo "---
id: funnel/ws_streaming_idea
type: note
status: raw
tags: [infra, realtime]
created: 2026-04-11
---
# WebSocket для стриминга сигналов

Идея: Добавить поддержку WebSocket для push-уведомлений о сигналах.
Почему: Сейчас поллинг каждые 5с — лишняя нагрузка, задержка.

## Контекст
Пользователи жалуются на задержку алертов. Конкуренты уже используют WS.

## Следующие шаги
- [ ] Исследовать библиотеки: websockets, aiohttp, fastapi-websocket
- [ ] Оценить нагрузку на сервер
- [ ] Промоутить в исследование: research/ws_feasibility_v1
" > vault/context/funnel/ws_streaming_idea.md

# Или через CLI (когда будет реализован)
nexus capture --type note --id funnel/ws_streaming_idea \
  --content "WebSocket для стриминга сигналов — снизить задержку алертов" \
  --tags infra,realtime
```

## Что дальше?
- Если идея перспективна → `nexus promote funnel/ws_streaming_idea → research/ws_feasibility_v1`
- Если отклонена → `nexus archive funnel/ws_streaming_idea --reason "out_of_scope"`
- Если нужна доработка → оставить `raw`, добавить `traces.related_to` для контекста

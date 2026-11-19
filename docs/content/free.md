---
title: Free numbers
description: Public numbers and their SMS — client.free. No API key needed.
navigation:
  order: 4
---

## list

Countries, the numbers of the selected country and the SMS of the selected number, in one call.

```python
def list(*, country: int | None = None, number: str | None = None, page: int | None = None, count: int | None = None) -> FreeList
```

| Option | Type | Default | Description |
|---|---|---|---|
| `country` | `int` | `44` (server) | Country code; an unknown one falls back to the first available. |
| `number` | `str` | first number | Number **without** the country code, as the keys of `numbers`. |
| `page` | `int` | `1` | Page of `messages`. |
| `count` | `int` | server default | SMS per page, 10–500. |

`FreeList`:

- `countries`: `list` of `{country, country_text, country_original}`
- `numbers`: `dict[str, {country, country_original, full_number, data_humans, is_archive}]`, keyed by the short number
- `messages`: a paginator of `{id, text, in_number, my_number, code, created_at, data_humans}` plus `number` and `country`; `code` is `-` when no code was found

```python
numbers = client.free.list(country=44)["numbers"]
short = next(iter(numbers), None)
if short:
    messages = client.free.list(country=44, number=short, count=20)["messages"]
    for sms in messages["data"]:
        print(sms["in_number"], sms["code"], sms["text"])
```

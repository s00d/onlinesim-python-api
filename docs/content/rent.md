---
title: Rent
description: Rent a number for days and receive every SMS sent to it — client.rent.
navigation:
  order: 2
---

A rent keeps a number for `days` days. Its SMS come in `RentItem["messages"]`, newest first.

`RentItem`: `{tzid, status, number, country, sum, days, hours, time, time_seconds?, extension, extend, messages, start_time, stop_time, day_extend?, …}` —
`sum` is the price paid in USD (a number; the server sends a decimal string), `time` minutes left, `time_seconds` seconds left,
`extension` `0` not extendable / `1` extendable / `2` auto-extension, `extend` maps days to the extension price (`{}` when not extendable),
`messages` is `list[RentSms]`: `{id, service, text, code, created_at}`.

## get

Rent a number and charge the balance.

```python
def get(country: int = 7, days: int = 1, extension: bool = True) -> RentItem
```

| Param | Type | Default | Description |
|---|---|---|---|
| `country` | `int` | `7` | Country code. |
| `days` | `int` | `1` | One of the tariff's `days` keys. |
| `extension` | `bool` | `True` | `False` makes the rent non-extendable for good. |

```python
rent = client.rent.get(7, 7)
print(rent["tzid"], rent["number"], rent["sum"])
```

Errors: `NoNumberError`; `ApiError` `UNDEFINED_DAYS`, `UNDEFINED_COUNTRY`, `WARNING_LOW_BALANCE`, `INTERVAL_CONCURRENT_REQUESTS_ERROR`, `TRY_AGAIN_LATER`.

## state

All rents of the account.

```python
def state() -> list[RentItem]
```

```python
for rent in client.rent.state():
    print(rent["number"], rent["messages"][0]["code"] if rent["messages"] else None)
```

## state_one

One rent.

```python
def state_one(tzid: int) -> RentItem
```

```python
messages = client.rent.state_one(tzid)["messages"]
```

Errors: `ApiError` `ERROR_NO_OPERATIONS` for an unknown tzid.

## extend

Extend a rent by `days` days and charge the balance. Only rents created with `extension=True`.

```python
def extend(tzid: int, days: int = 1) -> RentItem
```

```python
rent = client.rent.extend(tzid, 3)
print(rent["stop_time"])
```

Errors: `ApiError` `TRY_AGAIN_LATER` (not extendable, unknown tzid or period, a repeat within 10 s), `WARNING_LOW_BALANCE`.

## close

Return the number before the period ends. A rent that is not confirmed yet and has no SMS can be closed only after 120 s; US numbers cannot be closed early.

```python
def close(tzid: int) -> bool
```

```python
client.rent.close(tzid)
```

Errors: `ApiError` `ERROR_NO_OPERATIONS`, `NO_COMPLETE_TZID`, `NO_CLOSE_RENT_US`, `TRY_AGAIN_LATER`.

## tariffs

Rent prices of every country, keyed by country code. No API key needed.

```python
def tariffs() -> dict[str, RentTariff]
```

`RentTariff`: `{code, name, enabled, new, position, extend, confirm?, days, count, ext_counts?}` — `days` maps rent days to the price in USD, `count` to the numbers available.

```python
tariffs = client.rent.tariffs()
```

## tariffs_one

Rent prices of one country.

```python
def tariffs_one(country: int = 7) -> RentTariff
```

```python
days = client.rent.tariffs_one(7)["days"]
print(days.get("7"))  # price of 7 days
```

Errors: `ApiError` `NO_COUNTRY` for a country without rent.

---
title: Numbers
description: Order a number, read its SMS, close it — client.numbers.
navigation:
  order: 1
---

An operation (`tzid`) is one ordered number. Order it with `get`/`get_with_number`, read the SMS with `state_one` or `wait_code`, finish it with `close` (or `ban`). Countries are phone codes (`7`, `44`, …), services are slugs (`google`, `vkcom`, …) as returned by `tariffs`.

## price

Price of one number, USD; `None` when the country has no price for the service.

```python
def price(service: str, country: int = 7) -> float | None
```

| Param | Type | Default | Description |
|---|---|---|---|
| `service` | `str` | — | Service slug. |
| `country` | `int` | `7` | Country code. |

```python
usd = client.numbers.price("google", 44)
```

Errors: `ApiError` `ERROR_NO_SERVICE`, `UNDEFINED_COUNTRY`.

## get

Order a number; returns the operation id. Freezes the price on the balance.

```python
def get(service: str, country: int = 7, *, reject: Sequence[str | int] | None = None) -> int
```

| Param | Type | Default | Description |
|---|---|---|---|
| `service` | `str` | — | Service slug. |
| `country` | `int` | `7` | Country code. |
| `reject` | `Sequence[str \| int]` | profile list | Number prefixes to skip, e.g. `["4470"]`. |

```python
tzid = client.numbers.get("google", 44, reject=["4470"])
```

Errors: `NoNumberError`; `ApiError` `WARNING_LOW_BALANCE`, `ERROR_NO_SERVICE`, `UNDEFINED_COUNTRY`, `EXCEEDED_CONCURRENT_OPERATIONS`, `INTERVAL_CONCURRENT_REQUESTS_ERROR`, `TRY_AGAIN_LATER`.

## get_with_number

Same as `get`, but returns the number right away.

```python
def get_with_number(service: str, country: int = 7, *, reject: Sequence[str | int] | None = None) -> NumberOrder
```

Returns `NumberOrder`: `{tzid, number, country, time, service, title?, guard_interval_remaining_seconds?}` — `number` with `+`, `time` in seconds left.

```python
order = client.numbers.get_with_number("google", 44)
print(order["tzid"], order["number"])
```

Errors: as `get`.

## state

All operations of the account; `[]` when there are none.

```python
def state(*, message_to_code: bool = True, order_by: Literal["asc", "desc"] = "asc", msg_list: bool = False) -> list[Operation]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `message_to_code` | `bool` | `True` | `msg` is the code only; `False` — the full SMS text. |
| `order_by` | `"asc" \| "desc"` | `"asc"` | Order of operations. |
| `msg_list` | `bool` | `False` | `msg` is a list of all SMS (`list[OperationSms]`). |

`Operation`: `{tzid, response, number?, service?, country?, sum?, time?, msg?, guard_interval_remaining_seconds?, …}`.
`response` is the state: `TZ_INPOOL` (number being assigned), `TZ_NUM_WAIT` (waiting for SMS), `TZ_NUM_ANSWER` (SMS arrived), `TZ_OVER_OK` (finished), `ERROR_NO_ITEMS` (failed). `msg` is absent until the first SMS. The server caches answers for a few seconds.

```python
for op in client.numbers.state(order_by="desc"):
    print(op["tzid"], op["response"], op.get("msg"))
```

## state_one

One operation.

```python
def state_one(tzid: int, *, message_to_code: bool = True, msg_list: bool = False) -> Operation
```

```python
op = client.numbers.state_one(tzid)
if op["response"] == "TZ_NUM_ANSWER":
    print(op.get("msg"))
```

Errors: `ApiError` `ERROR_NO_OPERATIONS` when the operation does not exist (any more).

## wait_code

Poll the operation until a code arrives, then close it and return the code.

```python
def wait_code(tzid: int, *, interval: float = 5.0, timeout: float = 600.0, keep_open: bool = False,
              full_message: bool = False, since: str | None = None,
              sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic) -> str
```

| Option | Type | Default | Description |
|---|---|---|---|
| `interval` | `float` | `5.0` | Poll interval, seconds. |
| `timeout` | `float` | `600.0` | Give up after, seconds. |
| `keep_open` | `bool` | `False` | Call `next(tzid)` instead of `close(tzid)`, to wait for another SMS. |
| `full_message` | `bool` | `False` | Return the full SMS text instead of the code. |
| `since` | `str \| None` | `None` | Ignore this value (the previous code). |
| `sleep`, `clock` | callables | `time.sleep`, `time.monotonic` | Injectable for tests. |

A transient `TransportError` is retried until the timeout; any `ApiError` is raised at once. The same function is available standalone as `onlinesimru.wait_code(numbers, tzid, ...)`.

```python
first = client.numbers.wait_code(tzid, keep_open=True)
second = client.numbers.wait_code(tzid, since=first)
```

Errors: `TimeoutError`; `ApiError` with code `TZ_OVER_OK` or `ERROR_NO_ITEMS` when the operation ended without a new code; any other `ApiError` from `state_one`/`close`/`next`.

## next

Switch the operation to its next SMS and keep it open (for services that send several SMS).

```python
def next(tzid: int) -> bool
```

```python
client.numbers.next(tzid)
```

## close

Finish the operation. An operation without SMS can be closed only after its guard interval (`guard_interval_remaining_seconds`); every attempt locks the tzid for 5 s.

```python
def close(tzid: int) -> bool
```

```python
client.numbers.close(tzid)
```

Errors: `ApiError` `NO_COMPLETE_TZID`, `INTERVAL_CONCURRENT_REQUESTS_ERROR`, `ERROR_WRONG_TZID`.

## ban

Finish the operation and report the number as bad. Only before any SMS arrived.

```python
def ban(tzid: int) -> bool
```

```python
client.numbers.ban(tzid)
```

Errors: as `close`.

## tariffs

Services, prices and stock of every country, keyed by country code. No API key needed. The answer is large (a few MB); prefer `tariffs_one`.

```python
def tariffs() -> dict[str, CountryStat]
```

`CountryStat`: `{name, locale_name?, position, code, other?, new, enabled, services}`; `services` maps `service_<slug>` to `{count, popular, code, price, id, service, slug}`.

```python
countries = client.numbers.tariffs()
print(len(countries), "countries")
```

## tariffs_one

Services, prices and stock of one country.

```python
def tariffs_one(country: int = 7) -> CountryStat
```

```python
uk = client.numbers.tariffs_one(44)
for s in uk["services"].values():
    print(s["slug"], s["price"], s["count"])
```

Errors: `ApiError` `NO_COUNTRY`.

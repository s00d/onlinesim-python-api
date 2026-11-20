# Numbers

> Order a number, read its SMS, close it — client.numbers.

An operation (`tzid`) is one ordered number. Order it with `get`/`get_with_number`, read the SMS with `state_one` or `wait_code`, finish it with `close` (or `ban`). Countries are phone codes (`7`, `44`, …), services are slugs (`google`, `vkcom`, …) as returned by `tariffs`.

## price

Price of one number, USD; `None` when the country has no price for the service.

```python
def price(service: str, country: int = 7) -> float | None
```

<table>
<thead>
  <tr>
    <th>
      Param
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Default
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      <code>
        service
      </code>
    </td>
    
    <td>
      <code>
        str
      </code>
    </td>
    
    <td>
      —
    </td>
    
    <td>
      Service slug.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        country
      </code>
    </td>
    
    <td>
      <code>
        int
      </code>
    </td>
    
    <td>
      <code>
        7
      </code>
    </td>
    
    <td>
      Country code.
    </td>
  </tr>
</tbody>
</table>

```python
usd = client.numbers.price("google", 44)
```

Errors: `ApiError` `ERROR_NO_SERVICE`, `UNDEFINED_COUNTRY`.

## get

Order a number; returns the operation id. Freezes the price on the balance.

```python
def get(service: str, country: int = 7, *, reject: Sequence[str | int] | None = None) -> int
```

<table>
<thead>
  <tr>
    <th>
      Param
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Default
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      <code>
        service
      </code>
    </td>
    
    <td>
      <code>
        str
      </code>
    </td>
    
    <td>
      —
    </td>
    
    <td>
      Service slug.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        country
      </code>
    </td>
    
    <td>
      <code>
        int
      </code>
    </td>
    
    <td>
      <code>
        7
      </code>
    </td>
    
    <td>
      Country code.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        reject
      </code>
    </td>
    
    <td>
      <code>
        Sequence[str | int]
      </code>
    </td>
    
    <td>
      profile list
    </td>
    
    <td>
      Number prefixes to skip, e.g. <code>
        ["4470"]
      </code>
      
      .
    </td>
  </tr>
</tbody>
</table>

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

<table>
<thead>
  <tr>
    <th>
      Option
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Default
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      <code>
        message_to_code
      </code>
    </td>
    
    <td>
      <code>
        bool
      </code>
    </td>
    
    <td>
      <code>
        True
      </code>
    </td>
    
    <td>
      <code>
        msg
      </code>
      
       is the code only; <code>
        False
      </code>
      
       — the full SMS text.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        order_by
      </code>
    </td>
    
    <td>
      <code>
        "asc" | "desc"
      </code>
    </td>
    
    <td>
      <code>
        "asc"
      </code>
    </td>
    
    <td>
      Order of operations.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        msg_list
      </code>
    </td>
    
    <td>
      <code>
        bool
      </code>
    </td>
    
    <td>
      <code>
        False
      </code>
    </td>
    
    <td>
      <code>
        msg
      </code>
      
       is a list of all SMS (<code>
        list[OperationSms]
      </code>
      
      ).
    </td>
  </tr>
</tbody>
</table>

`Operation`: `{tzid, response?, number?, service?, country?, sum?, time?, msg?, guard_interval_remaining_seconds?, …}`.
`response` is the state (absent when no number could be issued): `TZ_INPOOL` (number being assigned), `TZ_NUM_WAIT` (waiting for SMS), `TZ_NUM_ANSWER` (SMS arrived), `TZ_OVER_OK` (finished), `ERROR_NO_ITEMS` (failed). `msg` is absent until the first SMS. The server caches answers for a few seconds.

```python
for op in client.numbers.state(order_by="desc"):
    print(op["tzid"], op.get("response"), op.get("msg"))
```

## state_one

One operation.

```python
def state_one(tzid: int, *, message_to_code: bool = True, msg_list: bool = False) -> Operation
```

```python
op = client.numbers.state_one(tzid)
if op.get("response") == "TZ_NUM_ANSWER":
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

<table>
<thead>
  <tr>
    <th>
      Option
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Default
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      <code>
        interval
      </code>
    </td>
    
    <td>
      <code>
        float
      </code>
    </td>
    
    <td>
      <code>
        5.0
      </code>
    </td>
    
    <td>
      Poll interval, seconds.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        timeout
      </code>
    </td>
    
    <td>
      <code>
        float
      </code>
    </td>
    
    <td>
      <code>
        600.0
      </code>
    </td>
    
    <td>
      Give up after, seconds.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        keep_open
      </code>
    </td>
    
    <td>
      <code>
        bool
      </code>
    </td>
    
    <td>
      <code>
        False
      </code>
    </td>
    
    <td>
      Call <code>
        next(tzid)
      </code>
      
       instead of <code>
        close(tzid)
      </code>
      
      , to wait for another SMS.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        full_message
      </code>
    </td>
    
    <td>
      <code>
        bool
      </code>
    </td>
    
    <td>
      <code>
        False
      </code>
    </td>
    
    <td>
      Return the full SMS text instead of the code.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        since
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      <code>
        None
      </code>
    </td>
    
    <td>
      Ignore this value (the previous code).
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        sleep
      </code>
      
      , <code>
        clock
      </code>
    </td>
    
    <td>
      callables
    </td>
    
    <td>
      <code>
        time.sleep
      </code>
      
      , <code>
        time.monotonic
      </code>
    </td>
    
    <td>
      Injectable for tests.
    </td>
  </tr>
</tbody>
</table>

Transient errors are retried until the timeout: `TransportError`, and `ApiError` `TRY_AGAIN_LATER` (the HTTP 429 rate limit), `ERROR_UNDEFINED` and `INTERVAL_CONCURRENT_REQUESTS_ERROR`. Any other `ApiError` is raised at once. The same function is available standalone as `onlinesimru.wait_code(numbers, tzid, ...)`.

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

Errors: `ApiError` `ERROR_WRONG_TZID` (not an operation of your account), `ERROR_NO_TZID`.

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

Errors: as `close`; `ApiError` with code `"0"` when the operation already has an SMS — nothing is changed then.

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

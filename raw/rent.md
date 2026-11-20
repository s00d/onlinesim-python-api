# Rent

> Rent a number for days and receive every SMS sent to it — client.rent.

A rent keeps a number for `days` days. Its SMS come in `RentItem["messages"]`, newest first.

`get` reserves the price (it shows in `zbalance`): the rent starts with `status` `0` and `checked` `False` and waits up to 20 minutes for its first SMS. The first SMS that is not a `notify` notice confirms it (`status` `1`) and charges the price; without one the rent closes and the reservation is released. Some countries (`confirm` in `tariffs`, e.g. US numbers) are confirmed and charged at once.

`RentItem`: `{tzid, status, number, country, sum, days, hours, time, time_seconds?, extension, extend, messages, start_time, stop_time, day_extend?, …}` —
`sum` is the cost in USD incl. extensions (a number; `rent.state` gets it from the server as a decimal string), `time` minutes left, `time_seconds` seconds left,
`extension` `0` not extendable / `1` extendable / `2` auto-extension, `extend` maps days to the extension price (`{}` when not extendable),
`messages` is `list[RentSms]`: `{id, service, text, code, created_at}` — `code` is `""` when no code was found and the integer `0` for a `notify` SMS (a prohibited sender).

## get

Rent a number. The price is reserved; the first SMS charges it.

```python
def get(country: int = 7, days: int = 1, extension: bool = True) -> RentItem
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
        days
      </code>
    </td>
    
    <td>
      <code>
        int
      </code>
    </td>
    
    <td>
      <code>
        1
      </code>
    </td>
    
    <td>
      One of the tariff's <code>
        days
      </code>
      
       keys.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        extension
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
        False
      </code>
      
       makes the rent non-extendable for good.
    </td>
  </tr>
</tbody>
</table>

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

Extend a rent by `days` days and charge the balance at once. Only confirmed rents (`status` `1` or `4`) created with `extension=True`.

```python
def extend(tzid: int, days: int = 1) -> RentItem
```

```python
rent = client.rent.extend(tzid, 3)
print(rent["stop_time"])
```

Errors: `ApiError` `TRY_AGAIN_LATER` (unknown tzid, not confirmed yet or closed, not extendable, unknown period, a repeat within 10 s), `WARNING_LOW_BALANCE`.

## close

Return the number before the period ends. A rent that is not confirmed yet (`status` `0`) and has no SMS can be closed only after 120 s; then, or with only `notify` SMS, the reservation is released. With a real SMS the rent is confirmed (charged) and closed. A confirmed rent closes without a refund. US numbers cannot be closed early.

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

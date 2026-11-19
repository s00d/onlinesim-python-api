---
title: onlinesim-python-api
description: Typed, zero-dependency Python client for the OnlineSim API — SMS numbers, rent, account and free numbers.
---

## Install

Python 3.9 or newer. The PyPI package is `onlinesimru`; it uses only the standard library (`urllib`, `json`) and ships type hints (`py.typed`).

::code-group
```bash [pip]
pip install onlinesimru
```

```bash [uv]
uv add onlinesimru
```
::

## Quick start

Check the balance, order a number, wait for the SMS code.

```python
import os

from onlinesimru import OnlineSim

client = OnlineSim(os.environ["ONLINESIM_KEY"])

b = client.user.balance()
print(f"available: {b['balance'] - b['zbalance']} USD")

order = client.numbers.get_with_number("google", 44)
print(f"enter {order['number']} in the app")

# Polls every 5 s for up to 10 min, then closes the operation.
code = client.numbers.wait_code(order["tzid"])
print(f"code: {code}")
```

The client is synchronous. Results are plain dicts typed as `TypedDict`s (`Balance`, `NumberOrder`, …), so editors and mypy know the keys.

## Client options

```python
from onlinesimru import OnlineSim

client = OnlineSim("your-api-key", lang="en", timeout=15)
```

| Option | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str \| None` | `None` | First positional argument. Sent as `Authorization: Bearer <api_key>`, never in the URL. Not needed for tariffs and free numbers. |
| `base_url` | `str` | `https://onlinesim.host/api/` | API base; trailing slash optional. |
| `lang` | `str` | `en` | Language of server texts (`lang` query parameter). |
| `dev_id` | `str \| int \| None` | `None` | Partner developer id (`dev_id`), sent only when set. |
| `timeout` | `float` | `30` | Per-request timeout, seconds. |
| `transport` | `Transport` | `urllib_transport` | Sends the HTTP requests: a custom TLS setup, a proxy, or a fake in tests. |

Sections: [`client.numbers`](/numbers), [`client.rent`](/rent), [`client.user`](/user), [`client.free`](/free). Webhook bodies are parsed by the standalone [`parse_webhook`](/webhooks).

Returned dicts keep the server's snake_case field names. Two things are normalised: money that the server sends as a decimal string (`balance`, rent `sum`) becomes a number, and maps that arrive as an empty PHP array `[]` become `{}`.

### Transport

A transport is any callable `(HttpRequest) -> HttpResponse`. `HttpRequest` has `method`, `url`, `headers`, `body` (bytes or `None`) and `timeout` (seconds); `HttpResponse` has `status` and `body` (bytes). Return the response for every HTTP status and raise `OSError` on network errors. The default `urllib_transport` takes an optional `ssl.SSLContext`:

```python
import functools
import ssl

from onlinesimru import OnlineSim, urllib_transport

ctx = ssl.create_default_context(cafile="/etc/ssl/corp-ca.pem")
client = OnlineSim("your-api-key", transport=functools.partial(urllib_transport, context=ctx))
```

## Error handling

Every error extends `OnlineSimError`.

| Class | When | Attributes |
|---|---|---|
| `ApiError` | The API answered with an error code (also a wrong key, HTTP 456). | `code`, `message` |
| `NoNumberError` | `NO_NUMBER` / `NO_NUMBER_FOR_FORWARD`: no number right now. Subclass of `ApiError`. | `code`, `message` |
| `TransportError` | Network error, request timeout, or a body that is not JSON. | `status` (`None` without a response), `body` (first 500 chars) |
| `TimeoutError` | `wait_code` got no code within its `timeout`. Also a built-in `TimeoutError`. | — |

```python
from onlinesimru import ApiError, NoNumberError, TransportError

try:
    client.numbers.get("google", 44)
except NoNumberError:
    pass  # try another country or later
except ApiError as error:
    print(error.code, error.message)  # e.g. WARNING_LOW_BALANCE
except TransportError as error:
    print("network", error.status, error.body)
```

`message` is the server's text when it sends one, otherwise a short English description of the code (`ERROR_MESSAGES`), otherwise the code itself. Profile validation failures become `ApiError` with code `VALIDATION_ERROR`.

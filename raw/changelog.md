# Changelog

> Release notes of onlinesim-python-api (PyPI onlinesimru).

The full history is in [CHANGELOG.md](https://github.com/s00d/onlinesim-python-api/blob/master/CHANGELOG.md).

## 3.1.1

- Fixed: `wait_code` no longer crashes on an operation without `response`; types against the current API (`Profile` `number`/`country`, optional `Operation["response"]`, `RentSms["code"]` `0` for `notify` SMS, nullable free-list and payment fields); `payment_history()["paylist"]` is kept when it arrives as a list.
- `wait_code` retries `TRY_AGAIN_LATER` (rate limit), `ERROR_UNDEFINED` and `INTERVAL_CONCURRENT_REQUESTS_ERROR`.
- `MockOnlineSim` follows the backend more closely: rent reservation and confirmation, `setOperationRevise` and `closeRentNum` answers, missing vs wrong key — see [Testing](/testing).

## 3.1.0

- New: `MockOnlineSim`, an offline fake of the API for your tests — see [Testing](/testing).

## 3.0.0

A rewrite with a new API; 2.x code does not run unchanged.

- One client, `OnlineSim(api_key)`, with the sections as attributes: `client.numbers`, `client.rent`, `client.user`, `client.free`.
- Zero runtime dependencies (standard library `urllib`), Python 3.9+, type hints with `TypedDict` results and `py.typed`.
- The key is sent as a Bearer header, never in the URL.
- Typed errors: `ApiError`, `NoNumberError`, `TransportError`, `TimeoutError`.
- `numbers.wait_code` has a real interval and timeout in seconds, `keep_open`, `since`, and retries network errors.
- `rent.get` creates extendable rents by default (`extension=True`).
- New: `user.set_webhook_url` / `clear_webhook_url` / `webhook_logs`, `parse_webhook`.
- Removed: the proxy API, `numbers.repeat`, `numbers.service`, `numbers.service_number`, `rent.port_reload`, `user.create_empty`, the old free-number methods (use `free.list`), `Driver` and the per-service classes.

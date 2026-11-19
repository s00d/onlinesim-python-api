---
title: Changelog
description: Release notes of onlinesim-python-api (PyPI onlinesimru).
navigation:
  order: 6
---

The full history is in [CHANGELOG.md](https://github.com/s00d/onlinesim-python-api/blob/master/CHANGELOG.md).

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

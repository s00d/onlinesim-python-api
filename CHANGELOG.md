# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0]

A rewrite. The public API changed; see the [docs](https://s00d.github.io/onlinesim-python-api/).

### Removed
- The proxy API (`ProxyService`, `Driver.proxy()`, deprecated by the backend).
- `numbers.repeat` (getNumRepeat), `numbers.service` (getService), `numbers.service_number` (getServiceNumber): no backend route.
- `rent.port_reload`: deprecated no-op on the backend.
- `user.create_empty` (pay/createEmpty).
- The old free-number methods (getFreeCountryList / getFreePhoneList / getFreeMessageList): the backend returns empty data; use `free.list`.
- `Driver`, `API` and the per-service classes (`NumbersService`, `RentNumbersService`, `UserService`, `FreeNumbersService`), `RequestException`.
- Runtime dependencies `httpx`, `pydantic`, `dacite`; `requirements.txt`, `pytest.ini`, `deploy.sh`, `DEPLOYMENT.md`, `example/`, the live-API tests.

### Changed
- One client: `OnlineSim(api_key, *, base_url, lang, dev_id, timeout, transport)`; sections are attributes (`client.numbers`, `client.rent`, `client.user`, `client.free`).
- The API key is sent as `Authorization: Bearer <key>`, never in the query string. `base_url` is the full API base (`https://onlinesim.host/api/`).
- Errors: `OnlineSimError` → `ApiError` (`code`, `message`), `NoNumberError` (subclass of `ApiError`), `TransportError` (`status`, `body`), `TimeoutError` (also a built-in `TimeoutError`).
- `numbers.wait_code(tzid, *, interval, timeout, keep_open, full_message, since, sleep, clock)`, times in seconds.
- `numbers.get` / `get_with_number` take `reject=` as a keyword; `get_with_number` returns `{tzid, number, country, time, service}`.
- `numbers.state(*, message_to_code, order_by, msg_list)` / `state_one(tzid, ...)` take booleans; `order_by` is lowercase.
- `rent.get(country, days, extension)`: `extension` defaults to `True` (the server default; `False` makes the rent non-extendable for good).
- Results are plain dicts typed as `TypedDict`s; money parsed to numbers (`user.balance()["balance"]`, rent `sum`).
- Python ≥ 3.9, zero runtime dependencies (stdlib `urllib`), `py.typed`, hatchling build, `__version__` from the installed metadata.

### Fixed
- `lang` was also sent as `dev_id`; `dev_id` is sent only when set.
- `getService` was requested as `/apigetService`; old URL building is gone.
- `NO_NUMBER` / `NO_NUMBER_FOR_FORWARD` are mapped to `NoNumberError`; error messages come from the server or a fallback table.
- `response` is stripped from successful results.
- `getNum` was sent as POST; every call except the profile webhook update is a GET with query parameters.
- Booleans were sent as `true`/`false`; now `1`/`0`. `reject` is a comma list; unset parameters are omitted.
- `wait_code` polled with a broken counter; it now uses a deadline with an injectable clock.
- An HTTP 456 wrong-key answer is an `ApiError`; non-JSON answers and network errors raise `TransportError`.
- `state()` returns `[]` instead of raising when there are no operations.
- Empty maps sent by PHP as `[]` (rent `extend`, `paylist`, free `numbers`, country `services`) are returned as `{}`.
- Rent requests always send `pagination=0`, so `messages` is a flat list.
- `pytest.ini` used the `[tool:pytest]` header and was ignored; `.venv` was not git-ignored; `py.typed` was declared but missing.

### Added
- `user.set_webhook_url(url)`, `user.clear_webhook_url()`, `user.webhook_logs(page)`.
- `parse_webhook(payload)` for inbound `receiving_sms` / `rent_sms` webhooks.
- Injectable `transport` (`HttpRequest` → `HttpResponse`) and per-request `timeout`.
- Offline test suite (fake transport, fake clock), docs examples type-checked with mypy, opt-in integration test, CI on Python 3.9–3.13 with ruff and mypy.
- New documentation site (Nuxt Content).

## [2.1.0] - 2025-08-10
### Added
- API domain replacement capability through `base_url` parameter in `API` class constructor
- `base_url` parameter allows using alternative domains for API endpoints
- Comprehensive test coverage for custom domain functionality
- New test file `tests/test_custom_domain.py` with unit tests for API domain replacement

### Changed
- Updated pydantic dependency to support both v1 and v2 (>=1.10.0,<3.0.0)
- Enhanced test infrastructure with pytest, pytest-cov, and pytest-mock
- Migrated from setup.py to modern pyproject.toml configuration
- Replaced legacy setuptools with modern build system
- Updated GitHub Actions workflow to use modern actions and PyPI API tokens
- Centralized version management in pyproject.toml, removed _version.py


## [2.0.1] - 2022-02-06
### Added
- refactoring, thanks to [RTHeLL](https://github.com/RTHeLL)

## [1.0.5] - 2019-09-21
### Added
- add ban

## [1.0.5] - 2019-09-21
### Added
- full message

## [1.0.1] - 2019-08-06
### Added
- multiple driver

## [1.0.1] - 2019-08-06
### Changed
- remove async

## [1.0.0] - 2019-08-05
### Added
- Project






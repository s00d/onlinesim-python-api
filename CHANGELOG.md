# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1]

Aligned with the regenerated backend API spec.

### Fixed
- `numbers.wait_code` no longer crashes with `KeyError` on a getState operation without `response` (absent while no number is issued); it keeps polling.
- Types: `Profile["number"]` is `int | None` and `Profile["country"]` is `str | None` (they were swapped); `Operation["response"]` is optional; `RentSms["code"]` is `str | int` (the integer `0` for a `notify` SMS, returned as sent); `FreeCountry` `country_text`/`country_original`, `FreeNumber["country_original"]`, `PaymentOrder` `currency`/`form_text` accept `None`.
- `user.payment_history()` no longer drops `paylist` when the server sends it as a JSON array (ids 0, 1, 2…); it is returned as sent.
- `numbers.wait_code` retries `ApiError` `TRY_AGAIN_LATER` (HTTP 429 rate limit), `ERROR_UNDEFINED` and `INTERVAL_CONCURRENT_REQUESTS_ERROR` until its timeout instead of raising at once.
- Error messages: `"0"` (ban not applied, the operation already has an SMS), `ACCOUNT_CLEANED`, `USER_NOT_ACTIVATED`, `ERROR_UNDEFINED`, `FORWARD_NOT_SUPPORTED` added; `ERROR_NO_KEY`, `NO_NUMBER_FOR_FORWARD`, `ACCOUNT_IDENTIFICATION_REQUIRED`, `API_DISABLED` (no longer sent) removed; `NoNumberError` only for `NO_NUMBER`; `ERROR_WRONG_KEY` reads "Wrong or missing API key".
- `MockOnlineSim` follows the backend: `setOperationRevise` answers `{"tzid":"N","response":"1"}` and `ERROR_WRONG_TZID` / `ERROR_NO_TZID`; `setOperationOk` tzid `0` → `ERROR_NO_TZID`; a missing key is HTTP 200 `ERROR_WRONG_KEY` (456 only for a wrong key, also on public endpoints); `getNum` with `number` adds `title`, `response_text`, `guard_interval_remaining_seconds`. Rent: `getRentNum` reserves the price (`status` 0) and the first non-`notify` SMS confirms and charges it, unknown country → `UNDEFINED_COUNTRY`, `sum` a number in getRentNum/extendRentState and a string in getRentState, `guard_interval_remaining_seconds` with `number`; `extendRentState` refusals are all `TRY_AGAIN_LATER`; `closeRentNum` unknown tzid → `ERROR_NO_OPERATIONS`, releases the reservation of an unconfirmed rent. Webhook-log params: `code` `""` without a code, rent `number` in full digits, rent `time_left` in minutes, `time_start` per type. `profile.php` accepts any `scheme://…` URL. `getPaymentHistory` adds `forms`/`buttons`; `getFreeList` lists 44 first, clamps `count` to 10..500, sends ISO-8601 `created_at` and `ignore`/`content`. `MockRent` gained `initial_days` and `status`, `MockSms` gained `at`.
- Docs: rent reservation and `sum`, available = balance − max(zbalance, 0), `ban` answer `"0"`, webhook `number`/`time_left`/`time_start`, the `wait_code` retry policy, the mock's behaviour.

## [3.1.0]

### Added
- `MockOnlineSim`: a built-in, in-process fake of the OnlineSim API for testing integrations offline — no network, key, money or clock. `mock.client()` returns a normal `OnlineSim` wired to it (`mock.transport` is the fake transport). It answers every endpoint the SDK calls like the real backend (HTTP 456 for a wrong key, string/int `response`, decimal-string money, `[]` for empty maps) and keeps balance, operations and rents. Test helpers: `add_sms`, `add_sms_after` (lets `wait_code` run with `interval=0`), `fail_next`, `fail_next_transport`, `set_balance`, `balance`, `operations`, `rents`, `requests`, `reset`. Part of the main package (`from onlinesimru import MockOnlineSim`). See the [testing guide](https://s00d.github.io/onlinesim-python-api/testing).
- Packaging checks in CI: `twine check --strict`, `check-wheel-contents`, `pyroma` (10/10), and a smoke test that installs the built wheel into a fresh venv and runs the README "Testing" example on Python 3.9 and 3.13.
- Releases are published by `.github/workflows/release.yml` with PyPI trusted publishing (OIDC, no API token) and get a GitHub release with the changelog section.

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






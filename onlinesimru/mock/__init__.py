"""In-process fake OnlineSim API for tests: :class:`MockOnlineSim`."""

from __future__ import annotations

import copy
import json
from typing import Any, List, Mapping, Optional, Union
from urllib.parse import parse_qsl, urlsplit

from ..client import DEFAULT_TIMEOUT, HttpRequest, HttpResponse, OnlineSim
from ._handlers import PUBLIC_PATHS, ROUTES
from ._state import (
    MockFailure,
    MockOperation,
    MockOperationStatus,
    MockPrices,
    MockRent,
    MockRentSms,
    MockRentTariff,
    MockRequest,
    MockSms,
    MockState,
    from_mills,
    to_mills,
)

__all__ = [
    "MOCK_BASE_URL",
    "MockOnlineSim",
    "MockOperation",
    "MockOperationStatus",
    "MockPrices",
    "MockRent",
    "MockRentSms",
    "MockRentTariff",
    "MockRequest",
    "MockSms",
]

MOCK_BASE_URL = "https://mock.onlinesim.invalid/api/"
"""Base URL of clients made by :meth:`MockOnlineSim.client`. Never contacted: the mock answers in-process."""


class MockOnlineSim:
    """In-process fake OnlineSim API for tests: no network, no key, no money, no clock.

    It is a transport (:attr:`transport`) that answers like the real backend; :meth:`client` returns a normal
    :class:`~onlinesimru.OnlineSim` wired to it. Test helpers add SMS, queue failures and expose the state.

    >>> mock = MockOnlineSim(balance=10)
    >>> client = mock.client()
    >>> tzid = client.numbers.get("google", 44)
    >>> mock.add_sms_after(tzid, "Your code: 123-456", 2)
    >>> client.numbers.wait_code(tzid, interval=0)
    '123456'
    """

    def __init__(
        self,
        *,
        api_key: str = "mock-key",
        balance: float = 100,
        prices: Optional[Mapping[int, Mapping[str, float]]] = None,
        rent_tariffs: Optional[Mapping[int, MockRentTariff]] = None,
        guard_interval: int = 0,
    ) -> None:
        """
        :param api_key: Key the mock accepts as ``Authorization: Bearer <api_key>``.
        :param balance: Starting balance, USD.
        :param prices: Number prices, country -> service -> USD; replaces the defaults.
        :param rent_tariffs: Rent tariffs, country -> ``{"days": {days: USD}, "extend": 0|1}``; replaces the defaults.
        :param guard_interval: Seconds. ``> 0``: an operation without SMS, or an unconfirmed rent without any SMS,
            cannot be closed (``NO_COMPLETE_TZID``).
        """
        self._state = MockState(
            api_key=api_key, balance=balance, prices=prices, rent_tariffs=rent_tariffs, guard_interval=guard_interval
        )

    def client(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = MOCK_BASE_URL,
        lang: str = "en",
        dev_id: Union[str, int, None] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> OnlineSim:
        """A normal client wired to the mock. ``api_key`` defaults to the mock's key; pass another one (``""`` for
        none) to test a wrong key."""
        key = self._state.api_key if api_key is None else api_key
        return OnlineSim(key, base_url=base_url, lang=lang, dev_id=dev_id, timeout=timeout, transport=self.transport)

    def transport(self, request: HttpRequest) -> HttpResponse:
        """The fake transport; pass ``transport=mock.transport`` when you build the client yourself. Any base URL
        works."""
        url = urlsplit(request.url)
        at = url.path.find("/api/")
        req = MockRequest(
            method=request.method.upper(),
            path=url.path.lstrip("/") if at < 0 else url.path[at + 5 :],
            query=dict(parse_qsl(url.query, keep_blank_values=True)),
            body=None if request.body is None else json.loads(request.body),
        )
        state = self._state
        state.requests.append(req)

        failure = state.take_failure(req.path)
        if failure is not None:
            if failure.code is not None:
                return _json({"response": failure.code})
            return _text(failure.status, "Mock transport failure")

        handler = ROUTES.get(req.path)
        if handler is None:
            return _text(404, "Not Found")
        # A wrong key is HTTP 456 (public endpoints check a sent key too); no key at all is HTTP 200.
        auth = _authorization(request.headers)
        if auth is not None and auth != f"Bearer {state.api_key}":
            return _json({"response": "ERROR_WRONG_KEY"}, 456)
        if auth is None and req.path not in PUBLIC_PATHS:
            return _json({"response": "ERROR_WRONG_KEY"})
        return _json(handler(state, req))

    def add_sms(self, tzid: int, text: str, *, service: Optional[str] = None) -> None:
        """An SMS arrives now at number operation or rent ``tzid``. Raises ``ValueError`` when there is no open
        operation or rent with that id."""
        if not self._state.deliver(tzid, text, service):
            raise ValueError(f"MockOnlineSim: no open operation or rent {tzid}")

    def add_sms_after(self, tzid: int, text: str, polls: int, *, service: Optional[str] = None) -> None:
        """The SMS arrives after ``polls`` state requests for ``tzid`` (getState / rent getRentState, listing it
        alone or with others): with ``polls=2`` the third poll sees it. Lets ``wait_code`` run with
        ``interval=0``."""
        if tzid not in self._state.operations and tzid not in self._state.rents:
            raise ValueError(f"MockOnlineSim: no operation or rent {tzid}")
        self._state.schedule(tzid, text, polls, service)

    def fail_next(self, code: str, *, endpoint: Optional[str] = None) -> None:
        """The next request (to ``endpoint`` only, e.g. ``getNum.php``, when given) answers ``{"response": code}``."""
        self._state.failures.append(MockFailure(endpoint, code=code))

    def fail_next_transport(self, *, status: int = 502, endpoint: Optional[str] = None) -> None:
        """The next request (to ``endpoint`` only, when given) fails at transport level: a non-JSON body with HTTP
        ``status``."""
        self._state.failures.append(MockFailure(endpoint, status=status))

    def set_balance(self, usd: float) -> None:
        """Set the total balance, USD."""
        self._state.balance = to_mills(usd)

    def balance(self) -> float:
        """Total balance, USD, including the part frozen by open operations (as ``getBalance`` reports it)."""
        return from_mills(self._state.balance)

    def operations(self) -> List[MockOperation]:
        """Number operations, oldest first (copies)."""
        return copy.deepcopy(list(self._state.operations.values()))

    def rents(self) -> List[MockRent]:
        """Open rents, oldest first (copies)."""
        return copy.deepcopy(list(self._state.rents.values()))

    @property
    def requests(self) -> List[MockRequest]:
        """Every request received, in order (a copy of the log)."""
        return list(self._state.requests)

    def reset(self) -> None:
        """Back to the constructor's state: balance, no operations, rents, logs, schedules or failures."""
        self._state.reset()


def _authorization(headers: Mapping[str, str]) -> Optional[str]:
    return next((v for k, v in headers.items() if k.lower() == "authorization"), None)


def _json(body: Any, status: int = 200) -> HttpResponse:
    return HttpResponse(status, json.dumps(body).encode())


def _text(status: int, body: str) -> HttpResponse:
    return HttpResponse(status, f"<html><body>{status} {body}</body></html>".encode())

"""The client, its transport boundary and the one request function every section calls."""

from __future__ import annotations

import http.client
import json
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple, Union

from .errors import ApiError, NoNumberError, TransportError
from .free import FreeApi
from .numbers import NumbersApi
from .rent import RentApi
from .user import UserApi

try:
    __version__ = version("onlinesimru")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.0.0"

DEFAULT_BASE_URL = "https://onlinesim.host/api/"
DEFAULT_TIMEOUT = 30.0
_BODY_EXCERPT = 500

QueryValue = Union[str, int, float, bool, None, Sequence[Union[str, int]]]
"""Query value. ``None``/empty are omitted, booleans become ``1``/``0``, sequences a comma list."""


class RequestFn(Protocol):
    """The one request function the sections hold (``OnlineSim._request``)."""

    def __call__(self, endpoint: str, query: Optional[Mapping[str, QueryValue]] = None, body: Any = None) -> Any: ...


@dataclass(frozen=True)
class HttpRequest:
    """What the client hands to the transport."""

    method: str
    url: str
    headers: Mapping[str, str]
    body: Optional[bytes]
    timeout: float
    """Seconds."""


@dataclass(frozen=True)
class HttpResponse:
    """What the transport returns: any HTTP status, the raw body."""

    status: int
    body: bytes


Transport = Callable[[HttpRequest], HttpResponse]
"""Sends one request. Returns the response for every HTTP status; raises ``OSError`` (or
``http.client.HTTPException``) on network errors and timeouts."""


def urllib_transport(request: HttpRequest, *, context: Optional[ssl.SSLContext] = None) -> HttpResponse:
    """Default transport on ``urllib.request``. Pass ``context`` via ``functools.partial`` for a custom TLS setup."""
    req = urllib.request.Request(  # noqa: S310 - OnlineSim accepts only http(s) base URLs
        request.url, data=request.body, headers=dict(request.headers), method=request.method
    )
    try:
        with urllib.request.urlopen(req, timeout=request.timeout, context=context) as res:  # noqa: S310
            return HttpResponse(res.status, res.read())
    except urllib.error.HTTPError as error:  # any non-2xx status still carries the JSON body
        with error:
            return HttpResponse(error.code, error.read())


class OnlineSim:
    """OnlineSim API client.

    >>> client = OnlineSim("your-api-key")
    >>> client.user.balance()  # doctest: +SKIP
    {'balance': 1442.33, 'zbalance': 1023.41, 'income': 9.78}
    """

    numbers: NumbersApi
    rent: RentApi
    user: UserApi
    free: FreeApi

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        lang: str = "en",
        dev_id: Union[str, int, None] = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: Optional[Transport] = None,
    ) -> None:
        """
        :param api_key: Sent as ``Authorization: Bearer <api_key>``. Not needed for tariffs and free numbers.
        :param base_url: Full API base; trailing slash optional.
        :param lang: Language of server texts (``lang`` query parameter).
        :param dev_id: Partner developer id (``dev_id`` query parameter), sent only when set.
        :param timeout: Per-request timeout, seconds.
        :param transport: Sends the HTTP requests. Default: :func:`urllib_transport`.
        """
        if urllib.parse.urlsplit(base_url).scheme not in ("http", "https"):
            raise ValueError(f"base_url must be an http(s) URL, got {base_url!r}")
        self._api_key = api_key or None
        self._base_url = base_url if base_url.endswith("/") else base_url + "/"
        self._lang = lang
        self._dev_id = None if dev_id is None or dev_id == "" else str(dev_id)
        self._timeout = timeout
        self._transport: Transport = transport or urllib_transport

        self.numbers = NumbersApi(self._request)
        self.rent = RentApi(self._request)
        self.user = UserApi(self._request)
        self.free = FreeApi(self._request)

    def _request(self, endpoint: str, query: Optional[Mapping[str, QueryValue]] = None, body: Any = None) -> Any:
        """Send one request. ``endpoint`` is relative to ``base_url``, suffix included (``getNum.php``).
        A ``body`` switches the request to POST with JSON."""
        params: Dict[str, QueryValue] = {**(query or {}), "lang": self._lang, "dev_id": self._dev_id}
        pairs: List[Tuple[str, str]] = []
        for key, value in params.items():
            encoded = _encode(value)
            if encoded is not None:
                pairs.append((key, encoded))
        url = self._base_url + endpoint + "?" + urllib.parse.urlencode(pairs)

        headers = {"Accept": "application/json", "User-Agent": f"onlinesimru/{__version__} (python)"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        data: Optional[bytes] = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()

        request = HttpRequest("GET" if data is None else "POST", url, headers, data, self._timeout)
        try:
            response = self._transport(request)
        except (OSError, http.client.HTTPException) as error:
            if _is_timeout(error):
                raise TransportError(f"Request timed out after {self._timeout:g} s") from error
            raise TransportError(f"Network error: {error}") from error

        text = response.body.decode("utf-8", "replace")
        try:
            payload = json.loads(text)
        except ValueError:
            raise TransportError(
                f"HTTP {response.status}: response is not JSON", response.status, text[:_BODY_EXCERPT]
            ) from None
        # The body is checked before the status: a wrong key is HTTP 456 with {"response":"ERROR_WRONG_KEY"},
        # the rate limit HTTP 429 with {"response":"TRY_AGAIN_LATER"}.
        if isinstance(payload, dict) and "response" in payload:
            return _unwrap(payload)
        if not 200 <= response.status < 300:
            raise TransportError(f"HTTP {response.status}", response.status, text[:_BODY_EXCERPT])
        return payload


def _unwrap(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Success: strip ``response``, return the rest. Error code: raise."""
    rest = dict(payload)
    response = rest.pop("response")
    if response in (1, "1") and not isinstance(response, bool):
        return rest
    if isinstance(response, dict):
        # profile.php validation errors: {"response":{"webhook_url":["The webhook url must be a valid URL."]}}
        messages = [str(m) for v in response.values() for m in (v if isinstance(v, list) else [v])]
        raise ApiError("VALIDATION_ERROR", "; ".join(messages) or None)
    code = str(response)
    # Debug backends echo the code as `message`; prefer the readable fallback then.
    message = rest.get("message")
    message = message if isinstance(message, str) and message != code else None
    if code == "NO_NUMBER":
        raise NoNumberError(code, message)
    raise ApiError(code, message)


def _encode(value: QueryValue) -> Optional[str]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (str, int, float)):
        return str(value)
    return ",".join(str(v) for v in value) or None


def _is_timeout(error: BaseException) -> bool:
    if isinstance(error, urllib.error.URLError) and isinstance(error.reason, BaseException):
        error = error.reason
    return isinstance(error, (socket.timeout, TimeoutError))

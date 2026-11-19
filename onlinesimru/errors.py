"""Exceptions raised by the SDK. Every one extends :class:`OnlineSimError`."""

from __future__ import annotations

import builtins
from typing import Mapping, Optional


class OnlineSimError(Exception):
    """Base class of every error raised by the SDK."""


class ApiError(OnlineSimError):
    """The API answered with an error code in ``response``."""

    def __init__(self, code: str, message: Optional[str] = None) -> None:
        self.code = code
        """Raw error code, e.g. ``ERROR_WRONG_KEY``."""
        self.message = message or ERROR_MESSAGES.get(code) or code
        super().__init__(self.message)


class NoNumberError(ApiError):
    """No number is available right now (``NO_NUMBER``, ``NO_NUMBER_FOR_FORWARD``)."""


class TransportError(OnlineSimError):
    """Network failure, request timeout, or a response that is not JSON."""

    def __init__(self, message: str, status: Optional[int] = None, body: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        """HTTP status, or ``None`` when no response arrived (network error, timeout)."""
        self.body = body
        """Start of the response body (up to 500 chars), empty when none."""


class TimeoutError(OnlineSimError, builtins.TimeoutError):  # noqa: A001
    """``wait_code`` gave up: no code arrived within its ``timeout``.

    Also a subclass of the built-in ``TimeoutError``.
    """


ERROR_MESSAGES: Mapping[str, str] = {
    "ACCOUNT_BLOCKED": "Account is blocked",
    "ERROR_WRONG_KEY": "Wrong API key",
    "ERROR_NO_KEY": "API key is missing",
    "ERROR_NO_SERVICE": "Service is not specified",
    "API_ACCESS_DISABLED": "API access is disabled in the profile",
    "API_ACCESS_IP": "API access from this IP is not allowed in the profile",
    "ERROR_NO_TZID": "tzid is not specified",
    "ERROR_WRONG_TZID": "Wrong tzid",
    "ERROR_NO_OPERATIONS": "No operations",
    "NO_NUMBER": "No numbers available for this service right now",
    "NO_NUMBER_FOR_FORWARD": "No numbers available for forwarding",
    "NO_COUNTRY": "Country not found",
    "UNDEFINED_COUNTRY": "Unknown country",
    "WARNING_LOW_BALANCE": "Not enough balance",
    "EXCEEDED_CONCURRENT_OPERATIONS": "Too many concurrent operations for this account",
    "INTERVAL_CONCURRENT_REQUESTS_ERROR": "Too many concurrent requests, try again in a few seconds",
    "TRY_AGAIN_LATER": "Temporarily unable to perform the request, try again later",
    "ACCOUNT_IDENTIFICATION_REQUIRED": "Account identification is required",
    "ERROR_PARAMS": "Wrong parameters",
    "API_DISABLED": "API is disabled",
    "NO_COMPLETE_TZID": "The operation cannot be closed yet",
    "NO_CLOSE_RENT_US": "US rent numbers cannot be closed early",
    "UNDEFINED_DAYS": "Unknown rent period",
    "VALIDATION_ERROR": "Validation failed",
    "TZ_OVER_OK": "Operation finished without a new code",
    "ERROR_NO_ITEMS": "Operation failed",
}
"""Fallback messages for error codes the server sends without a ``message``."""

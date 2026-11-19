from __future__ import annotations

import contextlib
import time
from typing import Callable, Optional, Protocol

from .errors import ApiError, TimeoutError, TransportError
from .models import Operation


class _Numbers(Protocol):
    def state_one(self, tzid: int, *, message_to_code: bool = ..., msg_list: bool = ...) -> Operation: ...

    def close(self, tzid: int) -> bool: ...

    def next(self, tzid: int) -> bool: ...


def wait_code(
    numbers: _Numbers,
    tzid: int,
    *,
    interval: float = 5.0,
    timeout: float = 600.0,
    keep_open: bool = False,
    full_message: bool = False,
    since: Optional[str] = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> str:
    """Poll ``numbers.state_one(tzid)`` every ``interval`` seconds until a code different from ``since`` arrives,
    then ``close`` (or ``next`` with ``keep_open``) and return it.

    A finished operation (TZ_OVER_OK, ERROR_NO_ITEMS) without a new code raises ``ApiError`` with that state as the
    code; running out of ``timeout`` seconds raises ``TimeoutError``. ``TransportError`` is retried until the
    timeout; any ``ApiError`` is raised at once. ``sleep`` and ``clock`` are injectable for tests.
    """
    deadline = clock() + timeout
    while True:
        op: Optional[Operation] = None
        with contextlib.suppress(TransportError):  # transient: retried until the timeout
            op = numbers.state_one(tzid, message_to_code=not full_message)

        if op is not None:
            msg = op.get("msg")
            if isinstance(msg, str) and msg and msg != since:
                if keep_open:
                    numbers.next(tzid)
                else:
                    numbers.close(tzid)
                return msg
            if op["response"] in ("TZ_OVER_OK", "ERROR_NO_ITEMS"):
                raise ApiError(op["response"])

        left = deadline - clock()
        if left <= 0:
            raise TimeoutError(f"No code for operation {tzid} within {timeout:g} s")
        sleep(min(interval, left))

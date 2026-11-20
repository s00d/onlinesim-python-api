from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Optional, Sequence, Union, cast

from ._normalize import as_map
from .errors import ApiError
from .models import CountryStat, NumberOrder, Operation
from .wait import wait_code

if TYPE_CHECKING:
    from .client import RequestFn


class NumbersApi:
    """Numbers for receiving SMS: ``client.numbers``."""

    def __init__(self, request: RequestFn) -> None:
        self._request = request

    def price(self, service: str, country: int = 7) -> Optional[float]:
        """Price (USD) of one number of ``service`` in ``country``; ``None`` when the country has no price for it."""
        res = self._request("getPrice.php", {"service": service, "country": country})
        return cast(Optional[float], res.get("price"))

    def get(self, service: str, country: int = 7, *, reject: Optional[Sequence[Union[str, int]]] = None) -> int:
        """Order a number. Returns the operation id (``tzid``)."""
        res = self._request("getNum.php", {"service": service, "country": country, "reject": reject})
        return int(res["tzid"])

    def get_with_number(
        self, service: str, country: int = 7, *, reject: Optional[Sequence[Union[str, int]]] = None
    ) -> NumberOrder:
        """Order a number and get it right away together with the operation id."""
        # `number` is a presence flag on getNum: sent here only.
        res = self._request("getNum.php", {"service": service, "country": country, "reject": reject, "number": 1})
        return cast(NumberOrder, res)

    def state(
        self, *, message_to_code: bool = True, order_by: Literal["asc", "desc"] = "asc", msg_list: bool = False
    ) -> List[Operation]:
        """All operations of the account; ``[]`` when there are none."""
        query = {"message_to_code": message_to_code, "orderby": order_by, "msg_list": msg_list, "number": 1}
        try:
            return cast(List[Operation], self._request("getState.php", query))
        except ApiError as error:
            if error.code == "ERROR_NO_OPERATIONS":
                return []
            raise

    def state_one(self, tzid: int, *, message_to_code: bool = True, msg_list: bool = False) -> Operation:
        """One operation. Raises ``ApiError("ERROR_NO_OPERATIONS")`` when it does not exist (any more)."""
        query = {"tzid": tzid, "message_to_code": message_to_code, "msg_list": msg_list, "number": 1}
        ops = self._request("getState.php", query)
        if not ops:
            raise ApiError("ERROR_NO_OPERATIONS")
        return cast(Operation, ops[0])

    def next(self, tzid: int) -> bool:
        """Switch the operation to its next SMS and keep it open."""
        self._request("setOperationRevise.php", {"tzid": tzid})
        return True

    def close(self, tzid: int) -> bool:
        """Finish the operation."""
        self._request("setOperationOk.php", {"tzid": tzid})
        return True

    def ban(self, tzid: int) -> bool:
        """Finish the operation and report the number as bad. After an SMS arrived nothing changes and
        ``ApiError("0")`` is raised."""
        self._request("setOperationOk.php", {"tzid": tzid, "ban": True})
        return True

    def tariffs(self) -> Dict[str, CountryStat]:
        """Services, prices and stock of every country, keyed by country code. No key needed."""
        res = as_map(self._request("getNumbersStats.php", {"country": "all"}))
        return {code: _country(c) for code, c in res.items()}

    def tariffs_one(self, country: int = 7) -> CountryStat:
        """Services, prices and stock of one country. No key needed."""
        return _country(self._request("getNumbersStats.php", {"country": country}))

    def wait_code(
        self,
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
        """Poll the operation until an SMS code arrives, then close it (or ``next`` with ``keep_open``).

        See :func:`onlinesimru.wait_code`. Times are in seconds.
        """
        return wait_code(
            self,
            tzid,
            interval=interval,
            timeout=timeout,
            keep_open=keep_open,
            full_message=full_message,
            since=since,
            sleep=sleep,
            clock=clock,
        )


def _country(c: Dict[str, object]) -> CountryStat:
    return cast(CountryStat, {**c, "services": as_map(c.get("services"))})

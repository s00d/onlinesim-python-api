from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from ._normalize import as_map
from .models import FreeList

if TYPE_CHECKING:
    from .client import RequestFn


class FreeApi:
    """Public free numbers: ``client.free``. No key needed."""

    def __init__(self, request: RequestFn) -> None:
        self._request = request

    def list(
        self,
        *,
        country: Optional[int] = None,
        number: Optional[str] = None,
        page: Optional[int] = None,
        count: Optional[int] = None,
    ) -> FreeList:
        """Countries, the numbers of the selected country and the SMS of the selected number."""
        res = self._request("getFreeList", {"country": country, "number": number, "page": page, "count": count})
        return cast(
            FreeList,
            {"countries": res.get("countries"), "numbers": as_map(res.get("numbers")), "messages": res.get("messages")},
        )

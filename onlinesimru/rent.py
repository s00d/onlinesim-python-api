from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, cast

from ._normalize import as_map, num
from .errors import ApiError
from .models import RentItem, RentTariff

if TYPE_CHECKING:
    from .client import RequestFn

# Always sent: flat `messages` list and `time_seconds`.
_DETAIL = {"pagination": 0, "number": 1}


class RentApi:
    """Rented numbers: ``client.rent``."""

    def __init__(self, request: RequestFn) -> None:
        self._request = request

    def get(self, country: int = 7, days: int = 1, extension: bool = True) -> RentItem:
        """Rent a number for ``days`` days. ``extension=False`` makes the rent non-extendable for good."""
        res = self._request(
            "rent/getRentNum.php", {"country": country, "days": days, "extension": extension, **_DETAIL}
        )
        return _rent_item(res["item"])

    def state(self) -> List[RentItem]:
        """All rents of the account."""
        res = self._request("rent/getRentState.php", dict(_DETAIL))
        return [_rent_item(r) for r in res["list"]]

    def state_one(self, tzid: int) -> RentItem:
        """One rent. Raises ``ApiError("ERROR_NO_OPERATIONS")`` when it does not exist."""
        res = self._request("rent/getRentState.php", {"tzid": tzid, **_DETAIL})
        if not res["list"]:
            raise ApiError("ERROR_NO_OPERATIONS")
        return _rent_item(res["list"][0])

    def extend(self, tzid: int, days: int = 1) -> RentItem:
        """Extend a rent by ``days`` days (only rents created with ``extension=True``)."""
        res = self._request("rent/extendRentState.php", {"tzid": tzid, "days": days, **_DETAIL})
        return _rent_item(res["item"])

    def tariffs(self) -> Dict[str, RentTariff]:
        """Rent prices of every country, keyed by country code. No key needed."""
        return as_map(self._request("rent/tariffsRent.php"))

    def tariffs_one(self, country: int = 7) -> RentTariff:
        """Rent prices of one country. Raises ``ApiError("NO_COUNTRY")`` for a country without rent. No key needed."""
        res = self._request("rent/tariffsRent.php", {"country": country})
        # An unknown country answers `[]`.
        if not isinstance(res, dict) or "code" not in res:
            raise ApiError("NO_COUNTRY")
        return cast(RentTariff, res)

    def close(self, tzid: int) -> bool:
        """Return the number before the rent period ends."""
        self._request("rent/closeRentNum.php", {"tzid": tzid})
        return True


def _rent_item(raw: Dict[str, Any]) -> RentItem:
    messages = raw.get("messages")
    return cast(
        RentItem,
        {
            **raw,
            "sum": num(raw.get("sum")) or 0,
            "extend": as_map(raw.get("extend")),
            "messages": messages if isinstance(messages, list) else [],
        },
    )

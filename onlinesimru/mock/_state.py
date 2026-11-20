"""State of the mock backend. :class:`MockState` is the single owner of everything the fake API remembers:
balance, operations, rents, the profile's webhook URL and its delivery log, scheduled SMS, the failure queue and
the request log. Handlers (``_handlers.py``) read and change it only through this object.

Deterministic: ids and numbers come from a counter, timestamps from a fixed epoch plus that counter.
Money is kept in integer thousandths of a USD ("mills") so sums never drift.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Mapping, Optional, TypedDict

MockPrices = Dict[int, Dict[str, float]]
"""Prices of numbers: country code -> service slug -> USD."""


class MockRentTariff(TypedDict):
    """Rent tariff of one country: rent days -> USD, and whether rents can be extended (``1``) or not (``0``)."""

    days: Dict[int, float]
    extend: int


@dataclass
class MockSms:
    """One SMS received by an operation or a rent."""

    service: str
    text: str
    code: Optional[str]
    """Code extracted from ``text`` (first run of 4-8 digits), ``None`` when there is none."""
    at: int
    """Seconds after the mock epoch when it arrived."""


@dataclass
class MockRentSms(MockSms):
    """One SMS of a rent."""

    id: int
    created_at: str


MockOperationStatus = Literal["TZ_NUM_WAIT", "TZ_NUM_ANSWER", "TZ_OVER_OK"]


@dataclass
class MockOperation:
    """A number operation as the mock stores it."""

    tzid: int
    service: str
    country: int
    number: str
    """Full number with ``+``."""
    sum: float
    """Price, USD. Frozen while open; spent on close after an SMS, refunded on close without one."""
    status: MockOperationStatus
    messages: List[MockSms] = field(default_factory=list)
    cursor: int = 0
    """Index of the SMS shown in ``msg``; ``next`` (setOperationRevise) moves it past the last one."""


@dataclass
class MockRent:
    """A rent as the mock stores it. Closed rents are removed."""

    tzid: int
    country: int
    number: str
    """Number without the country code, as the backend sends it for rents."""
    days: int
    """Total rent days: the initial period plus extensions."""
    sum: float
    """Total cost incl. extensions, USD. Frozen while ``status`` is 0."""
    extension: bool
    initial_days: int
    """The initial period (``days`` of getRentNum)."""
    status: int = 0
    """``0``: reserved, waiting for the first SMS; ``1``: confirmed by an SMS that is not ``notify``, price charged."""
    messages: List[MockRentSms] = field(default_factory=list)
    """Oldest first."""


@dataclass(frozen=True)
class MockRequest:
    """One request the mock received."""

    method: str
    path: str
    """Path relative to ``/api/``, e.g. ``getNum.php``, ``rent/getRentNum.php``, ``getFreeList``."""
    query: Dict[str, str]
    body: Any = None
    """Parsed JSON body of a POST, ``None`` for GET."""


@dataclass(frozen=True)
class MockFailure:
    """A queued failure: the next matching request answers ``{"response": code}``, or (``code`` is ``None``)
    a non-JSON HTTP ``status``."""

    endpoint: Optional[str]
    code: Optional[str] = None
    status: int = 502


@dataclass
class _ScheduledSms:
    text: str
    service: Optional[str]
    polls: int
    """getState/getRentState polls of this tzid still to pass before the SMS arrives."""


DEFAULT_PRICES: Mapping[int, Mapping[str, float]] = {
    7: {"vkcom": 0.5, "telegram": 1.2, "google": 0.3},
    44: {"google": 0.2, "vkcom": 0.36},
}

DEFAULT_RENT_TARIFFS: Mapping[int, MockRentTariff] = {
    7: {"days": {1: 1.0, 3: 2.5, 7: 5.0}, "extend": 1},
}

MOCK_USER_ID = 1
OPERATION_TIME = 1200
"""Seconds an operation stays open, as reported in ``time``. The mock has no clock, so it never runs down."""
RENT_FIRST_SMS_MINUTES = 20
"""Minutes an unconfirmed rent waits for its first SMS (``stop_time`` = start + this)."""
NOTIFY = "notify"
"""Sender of a rent SMS from a prohibited sender: it gets the integer ``code`` ``0`` and does not confirm the rent."""

_EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc)


def stamp(seconds: int = 0) -> str:
    """``YYYY-MM-DD HH:MM:SS`` at ``seconds`` after the fixed mock epoch."""
    return (_EPOCH + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")


_DIGIT_GAP = re.compile(r"([0-9])[\s-]+(?=[0-9])")
_CODE = re.compile(r"(?<![0-9])[0-9]{4,8}(?![0-9])")


def extract_code(text: str) -> Optional[str]:
    """The code rule shared by every SDK mock: dashes/spaces between digits are removed, then the first run of
    4-8 digits (not part of a longer run) is the code; ``None`` when there is none."""
    match = _CODE.search(_DIGIT_GAP.sub(r"\1", text))
    return match.group(0) if match else None


def to_mills(usd: float) -> int:
    return round(usd * 1000)


def from_mills(mills: int) -> float:
    return mills / 1000


def short_number(id_: int) -> str:
    """Short (country-less) number for an id: deterministic, 9 digits."""
    return str(900_000_000 + id_)


class MockState:
    """Everything the fake backend remembers. One instance per :class:`~onlinesimru.MockOnlineSim`."""

    def __init__(
        self,
        *,
        api_key: str,
        balance: float,
        prices: Optional[Mapping[int, Mapping[str, float]]],
        rent_tariffs: Optional[Mapping[int, MockRentTariff]],
        guard_interval: int,
    ) -> None:
        self.api_key = api_key
        self.guard_interval = guard_interval
        self.prices: MockPrices = {c: dict(s) for c, s in (DEFAULT_PRICES if prices is None else prices).items()}
        self.rent_tariffs: Dict[int, MockRentTariff] = {
            c: {"days": dict(t["days"]), "extend": t["extend"]}
            for c, t in (DEFAULT_RENT_TARIFFS if rent_tariffs is None else rent_tariffs).items()
        }
        self._start_balance = to_mills(balance)

        self.balance = 0
        """Total balance incl. the frozen part, mills."""
        self.frozen = 0
        """Frozen by open operations and unconfirmed rents, mills."""
        self.operations: Dict[int, MockOperation] = {}
        self.rents: Dict[int, MockRent] = {}
        self.webhook_url: Optional[str] = None
        self.webhook_logs: List[Dict[str, Any]] = []
        self.requests: List[MockRequest] = []
        self.failures: List[MockFailure] = []
        self.scheduled: Dict[int, List[_ScheduledSms]] = {}
        self.seq = 0
        """Source of tzids, numbers, message ids and timestamps."""
        self.reset()

    def reset(self) -> None:
        self.balance = self._start_balance
        self.frozen = 0
        self.operations = {}
        self.rents = {}
        self.webhook_url = None
        self.webhook_logs = []
        self.requests = []
        self.failures = []
        self.scheduled = {}
        self.seq = 0

    @property
    def available(self) -> int:
        """Available balance (total minus frozen), mills."""
        return self.balance - self.frozen

    def peek_id(self) -> int:
        """The id the next operation/rent will get."""
        return self.seq + 1

    def next_id(self) -> int:
        self.seq += 1
        return self.seq

    def take_failure(self, path: str) -> Optional[MockFailure]:
        """Remove and return the first queued failure that applies to ``path``."""
        for i, failure in enumerate(self.failures):
            if failure.endpoint is None or failure.endpoint == path:
                return self.failures.pop(i)
        return None

    def deliver(self, tzid: int, text: str, service: Optional[str] = None) -> bool:
        """An SMS arrives at operation or rent ``tzid`` now. Returns ``False`` when there is no open one."""
        code = extract_code(text)
        op = self.operations.get(tzid)
        if op is not None and op.status != "TZ_OVER_OK":
            sms = MockSms(op.service if service is None else service, text, code, self.seq)
            op.messages.append(sms)
            op.status = "TZ_NUM_ANSWER"
            # Activation: `+<digits>`, seconds left, the order time.
            self._webhook("receiving_sms", tzid, op.country, op.number, sms, OPERATION_TIME, stamp(op.tzid))
            return True
        rent = self.rents.get(tzid)
        if rent is not None:
            id_ = self.next_id()
            rent_sms = MockRentSms("other" if service is None else service, text, code, id_, id_, stamp(id_))
            rent.messages.append(rent_sms)
            if rent.status == 0 and rent_sms.service != NOTIFY:
                # The first real SMS confirms the rent: the reservation is charged.
                cost = to_mills(rent.sum)
                self.frozen -= cost
                self.balance -= cost
                rent.status = 1
            # Rent: full number in digits without `+`, minutes left, the SMS time.
            minutes_left = rent.days * 24 * 60 if rent.status == 1 else RENT_FIRST_SMS_MINUTES
            number = f"{rent.country}{rent.number}"
            self._webhook("rent_sms", tzid, rent.country, number, rent_sms, minutes_left, stamp(id_))
            return True
        return False

    def schedule(self, tzid: int, text: str, polls: int, service: Optional[str] = None) -> None:
        self.scheduled.setdefault(tzid, []).append(_ScheduledSms(text, service, polls))

    def poll(self, tzid: int) -> None:
        """One state poll of ``tzid``: delivers the scheduled SMS whose polls ran out, counts down the rest."""
        pending = self.scheduled.get(tzid)
        if not pending:
            return
        due = [s for s in pending if s.polls <= 0]
        rest = [s for s in pending if s.polls > 0]
        for s in rest:
            s.polls -= 1
        if rest:
            self.scheduled[tzid] = rest
        else:
            del self.scheduled[tzid]
        # Dropped silently when the operation was closed meanwhile: a real SMS would not arrive either.
        for s in due:
            self.deliver(tzid, s.text, s.service)

    def _webhook(
        self, type_: str, tzid: int, country: int, number: str, sms: MockSms, time_left: int, time_start: str
    ) -> None:
        """No HTTP call: the mock only records what the backend would have sent."""
        if not self.webhook_url:
            return
        time = stamp(sms.at)
        self.webhook_logs.append(
            {
                "id": len(self.webhook_logs) + 1,
                "user_id": MOCK_USER_ID,
                "webhook_url": self.webhook_url,
                "type": type_,
                "params": {
                    "webhook_type": type_,
                    "operation_id": tzid,
                    "user_id": MOCK_USER_ID,
                    "country_code": country,
                    "number": number,
                    "sender": sms.service,
                    "message": sms.text,
                    "code": sms.code or "",
                    "time_start": time_start,
                    "time_left": time_left,
                },
                "status": "success",
                "error": None,
                "created_at": time,
                "updated_at": time,
            }
        )

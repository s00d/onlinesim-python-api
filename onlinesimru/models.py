"""Wire types.

They mirror the schemas of the OnlineSim OpenAPI spec (snake_case field names as sent by the server), with these
client-side normalisations: decimal-string money (``balance``, rent ``sum`` in ``rent.state``) becomes a number, and
maps the server may send as an empty PHP array ``[]`` become ``{}`` (``payment_history()["paylist"]`` is left as sent:
a JSON array when its ids are 0, 1, 2...). Keys of the ``total=False`` parts may be absent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

# ----- numbers -----

OperationStatus = Literal["TZ_INPOOL", "TZ_NUM_WAIT", "TZ_NUM_ANSWER", "TZ_OVER_OK", "ERROR_NO_ITEMS"]
"""State of a number operation (``Operation["response"]``)."""


class OperationSms(TypedDict, total=False):
    """One SMS of an operation when ``msg_list`` is set."""

    service: str
    msg: str
    text: str
    code: str


class _OperationRequired(TypedDict):
    tzid: int


class Operation(_OperationRequired, total=False):
    """Number operation (getState item)."""

    response: OperationStatus
    """Absent when no number could be issued."""
    number: str
    service: str
    country: int
    sum: float
    time: int
    """Seconds left."""
    form: str
    subscription_package_id: Optional[int]
    webhook_url: Optional[str]
    msg: Union[str, List[OperationSms], bool]
    """Absent until an SMS arrives. Code (or full text) by default, a list with ``msg_list``."""
    extend: int
    guard_interval_remaining_seconds: int
    """Seconds until the operation may be closed."""


class _NumberOrderRequired(TypedDict):
    tzid: int
    number: str
    """Full number with ``+``, e.g. ``+447459608320``."""
    country: int
    time: int
    """Seconds left."""
    service: str


class NumberOrder(_NumberOrderRequired, total=False):
    """Result of ``numbers.get_with_number``."""

    title: str
    guard_interval_remaining_seconds: int


class ServiceStat(TypedDict):
    count: Union[int, str]
    """Numbers in stock; ``"?"`` when unknown."""
    popular: bool
    code: int
    price: float
    id: int
    service: str
    """Display name."""
    slug: str
    """Service id for ``numbers.get`` / ``numbers.price``."""


class _CountryStatRequired(TypedDict):
    name: str
    position: int
    code: int
    new: bool
    enabled: bool
    services: Dict[str, ServiceStat]
    """Map ``service_<slug>`` -> service."""


class CountryStat(_CountryStatRequired, total=False):
    locale_name: str
    other: Union[float, bool]
    """Price of other services; ``False`` when not set."""


# ----- rent -----


class RentSms(TypedDict):
    id: int
    service: str
    """Sender. ``notify``: a notice about a prohibited sender (does not confirm the rent); ``init``: record of a rent
    confirmed at once."""
    text: str
    code: Union[str, int]
    """Code found in the text, ``""`` when none; the integer ``0`` for a ``notify`` SMS."""
    created_at: str


class _RentItemRequired(TypedDict):
    tzid: int
    status: int
    number: str
    country: int
    sum: float
    """Cost of the rent incl. extensions, USD (the server sends a number or a decimal string). Reserved while
    ``status`` is 0, charged once confirmed."""
    days: int
    hours: int
    time: int
    """Minutes left."""
    extension: int
    """0 - not extendable, 1 - extendable, 2 - auto-extension."""
    start_time: str
    stop_time: str
    extend: Dict[str, float]
    """Days -> extension price; ``{}`` when not extendable."""
    messages: List[RentSms]
    """SMS, newest first."""


class RentItem(_RentItemRequired, total=False):
    """Rent operation."""

    time_seconds: int
    """Seconds left."""
    guard_interval_remaining_seconds: int
    days_autoextend: int
    rent: int
    checked_time: Optional[str]
    checked: bool
    freeze: bool
    reload: Optional[int]
    m_ext: bool
    day_extend: float
    """Price of one day of extension; 0 when not configured."""
    webhook_url: Optional[str]


class _RentTariffRequired(TypedDict):
    code: int
    name: str
    enabled: bool
    new: bool
    position: int
    extend: int
    days: Dict[str, float]
    """Rent days -> price, USD."""
    count: Dict[str, int]
    """Rent days -> numbers available."""


class RentTariff(_RentTariffRequired, total=False):
    confirm: bool
    ext_counts: Dict[str, int]


# ----- user -----


class _BalanceRequired(TypedDict):
    balance: float
    """Total balance, USD. Includes ``zbalance``: available = balance - max(zbalance, 0)."""
    zbalance: float
    """Sum frozen by numbers and rents in progress; may be negative."""


class Balance(_BalanceRequired, total=False):
    income: float
    """Partner income."""


class _ProfileRequired(TypedDict):
    id: int


class Profile(_ProfileRequired, total=False):
    hash_id: Optional[str]
    name: Optional[str]
    username: Optional[str]
    email: Optional[str]
    email_verified_at: Optional[str]
    apikey: str
    api_access: Union[bool, Dict[str, Any]]
    """``True``, or a map of allowed IPs."""
    locale: str
    currency: str
    number_country: Optional[int]
    number_reject: Union[List[str], Dict[str, str], None]
    webhook_url: Optional[str]
    number: Optional[int]
    country: Optional[str]
    number_region: Optional[int]
    is_api: bool
    active: str
    block: int
    disable: bool
    verify: int
    ugroup: int
    sub: int
    first_login: bool
    is_project_subscription: bool
    resetCount: Optional[int]
    created_at: str
    notification_at: Optional[str]


# ``from`` is a Python keyword, so the paginator fields are declared with the functional syntax.
_PaginatorFields = TypedDict(
    "_PaginatorFields",
    {
        "current_page": int,
        "from": Optional[int],
        "to": Optional[int],
        "last_page": int,
        "per_page": int,
        "total": int,
    },
)


class _PaginatorLinks(TypedDict, total=False):
    first_page_url: str
    last_page_url: str
    next_page_url: Optional[str]
    prev_page_url: Optional[str]
    path: str
    links: List[Dict[str, Any]]


class Paginator(_PaginatorFields, _PaginatorLinks):
    """Laravel paginator fields; the subclasses add the typed ``data`` list."""


class PaymentOrder(TypedDict, total=False):
    id: int
    sum: str
    """Decimal string, e.g. ``"89.00"``."""
    currency: Optional[str]
    stat: int
    form_text: Optional[str]
    status_text: str
    created_at: str


class PaymentOrders(Paginator):
    data: List[PaymentOrder]


class _PaymentHistoryRequired(TypedDict):
    orders: PaymentOrders
    paylist: Union[Dict[str, Any], List[Any]]
    """Payment methods by group id; a list when the ids are 0, 1, 2... (the server sends a JSON array then)."""


class PaymentHistory(_PaymentHistoryRequired, total=False):
    domains: List[str]
    forms: Dict[str, str]
    currency: Dict[str, float]
    buttons: Dict[str, List[float]]


WebhookType = Literal["receiving_sms", "rent_sms"]


class WebhookPayload(TypedDict):
    """Inbound webhook body as normalised by ``parse_webhook``: missing fields are ``None``."""

    webhook_type: Optional[WebhookType]
    operation_id: Optional[int]
    user_id: Optional[int]
    country_code: Optional[int]
    number: Optional[str]
    sender: Optional[str]
    message: Optional[str]
    code: Optional[str]
    time_start: Optional[str]
    time_left: Optional[int]


class WebhookLog(TypedDict):
    id: int
    user_id: int
    webhook_url: str
    type: WebhookType
    params: Dict[str, Any]
    """Payload as sent by the server (not normalised)."""
    status: Literal["success", "fail", "pending"]
    error: Optional[str]
    created_at: str
    updated_at: str


class WebhookLogs(Paginator):
    data: List[WebhookLog]


# ----- free -----


class FreeCountry(TypedDict):
    country: int
    country_text: Optional[str]
    country_original: Optional[str]


class FreeNumber(TypedDict):
    country: int
    country_original: Optional[str]
    full_number: str
    data_humans: str
    is_archive: bool


class FreeMessage(TypedDict):
    id: int
    text: str
    in_number: str
    """Sender."""
    my_number: str
    code: str
    """``-`` when no code was found."""
    created_at: str
    data_humans: str


class FreeMessages(Paginator):
    data: List[FreeMessage]
    number: Optional[str]
    country: int


class FreeList(TypedDict):
    countries: List[FreeCountry]
    numbers: Dict[str, FreeNumber]
    """Keyed by number without the country code."""
    messages: FreeMessages

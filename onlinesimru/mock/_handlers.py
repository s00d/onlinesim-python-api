"""The mock's routes: endpoint path (relative to ``/api/``) -> handler. A handler gets the state and the request
and returns the JSON body the real backend would send (HTTP 200). Shapes follow the OpenAPI spec and the live
captures: ``response`` as int or string per endpoint, decimal-string money, ``[]`` for empty maps.
Auth, queued failures, 456 and 404 are the transport's job (``MockOnlineSim``), not the handlers'.
"""

from __future__ import annotations

import urllib.parse
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple

from ._state import (
    MOCK_USER_ID,
    OPERATION_TIME,
    MockOperation,
    MockRent,
    MockRequest,
    MockSms,
    MockState,
    extract_code,
    from_mills,
    short_number,
    stamp,
    to_mills,
)

Handler = Callable[[MockState, MockRequest], Any]

PUBLIC_PATHS = frozenset({"getNumbersStats.php", "rent/tariffsRent.php", "getFreeList"})
"""Endpoints that answer without a key."""

_COUNTRY_NAMES: Mapping[int, Tuple[str, str]] = {7: ("russia", "Russia"), 44: ("united_kingdom", "United Kingdom")}


def _error(code: str) -> Dict[str, Any]:
    return {"response": code}


def _flag(req: MockRequest, key: str) -> bool:
    return req.query.get(key, "0") != "0"


def _int(req: MockRequest, key: str, fallback: int) -> int:
    try:
        return int(req.query[key])
    except (KeyError, ValueError):
        return fallback


def _decimal(mills: int, digits: int = 3) -> str:
    """USD with ``digits`` decimals, as the backend sends ``balance``."""
    return f"{from_mills(mills):.{digits}f}"


def _country_name(code: int) -> Tuple[str, str]:
    return _COUNTRY_NAMES.get(code, (f"country_{code}", f"Country {code}"))


def _paginate(items: Sequence[Any], page: int, per_page: int, path: str) -> Dict[str, Any]:
    """Laravel paginator over ``items``."""
    total = len(items)
    last_page = max(1, -(-total // per_page))
    data = list(items[(page - 1) * per_page : page * per_page])

    def url(p: int) -> str:
        return f"https://onlinesim.host/api/{path}?page={p}"

    return {
        "current_page": page,
        "data": data,
        "first_page_url": url(1),
        "from": (page - 1) * per_page + 1 if data else None,
        "last_page": last_page,
        "last_page_url": url(last_page),
        "links": [],
        "next_page_url": url(page + 1) if page < last_page else None,
        "path": f"https://onlinesim.host/api/{path}",
        "per_page": per_page,
        "prev_page_url": url(page - 1) if page > 1 else None,
        "to": (page - 1) * per_page + len(data) if data else None,
        "total": total,
    }


# ----- numbers -----


def _msg_of(sms: MockSms, to_code: bool) -> str:
    return (sms.code or sms.text) if to_code else sms.text


def _operation_view(state: MockState, op: MockOperation, req: MockRequest) -> Dict[str, Any]:
    to_code = _flag(req, "message_to_code")
    is_open = op.status != "TZ_OVER_OK"
    view: Dict[str, Any] = {
        "country": op.country,
        "sum": op.sum,
        "service": op.service,
        "number": op.number,
        "subscription_package_id": None,
        "webhook_url": state.webhook_url,
        "response": op.status,
        "tzid": op.tzid,
        "time": OPERATION_TIME if is_open else 0,
        "form": "index",
    }
    if _flag(req, "msg_list"):
        if op.messages:
            view["msg"] = [{"service": s.service, "msg": _msg_of(s, to_code)} for s in op.messages]
    elif op.cursor < len(op.messages):
        view["msg"] = _msg_of(op.messages[op.cursor], to_code)
    if "number" in req.query:
        view["guard_interval_remaining_seconds"] = state.guard_interval if is_open and not op.messages else 0
    return view


def _get_price(state: MockState, req: MockRequest) -> Any:
    prices = state.prices.get(_int(req, "country", 7))
    if prices is None:
        return _error("UNDEFINED_COUNTRY")
    return {"response": "1", "price": prices.get(req.query.get("service", ""))}


def _get_num(state: MockState, req: MockRequest) -> Any:
    country = _int(req, "country", 7)
    service = req.query.get("service", "")
    prices = state.prices.get(country)
    if prices is None:
        return _error("UNDEFINED_COUNTRY")
    price = prices.get(service)
    if price is None:
        return _error("ERROR_NO_SERVICE")
    cost = to_mills(price)
    if state.available < cost:
        return _error("WARNING_LOW_BALANCE")

    number = f"+{country}{short_number(state.peek_id())}"
    reject = [p for p in req.query.get("reject", "").split(",") if p]
    if any(number[1:].startswith(prefix) for prefix in reject):
        return _error("NO_NUMBER")

    tzid = state.next_id()
    state.frozen += cost
    state.operations[tzid] = MockOperation(tzid, service, country, number, price, "TZ_NUM_WAIT")
    if "number" not in req.query:
        return {"response": 1, "tzid": tzid}
    return {
        "response": 1,
        "tzid": tzid,
        "number": number,
        "country": country,
        "time": OPERATION_TIME,
        "service": service,
    }


def _get_state(state: MockState, req: MockRequest) -> Any:
    if "tzid" in req.query:
        one = state.operations.get(_int(req, "tzid", -1))
        ops = [] if one is None else [one]
    else:
        ops = list(state.operations.values())
    for op in ops:
        state.poll(op.tzid)
    if not ops:
        return _error("ERROR_NO_OPERATIONS")
    ops.sort(key=lambda o: o.tzid, reverse=req.query.get("orderby") == "desc")
    return [_operation_view(state, op, req) for op in ops]


def _set_operation_revise(state: MockState, req: MockRequest) -> Any:
    tzid = _int(req, "tzid", 0)
    op = state.operations.get(tzid)
    # Always succeeds, even for unknown tzids, like the backend.
    if op is not None and op.status != "TZ_OVER_OK":
        op.cursor = len(op.messages)
        op.status = "TZ_NUM_WAIT"
    return {"response": 1, "tzid": tzid}


def _set_operation_ok(state: MockState, req: MockRequest) -> Any:
    tzid = _int(req, "tzid", 0)
    op = state.operations.get(tzid)
    if op is None or op.status == "TZ_OVER_OK":
        return _error("ERROR_WRONG_TZID")
    received = bool(op.messages)
    if _flag(req, "ban") and received:
        return {"response": "0"}
    if not received and state.guard_interval > 0:
        return _error("NO_COMPLETE_TZID")
    cost = to_mills(op.sum)
    state.frozen -= cost
    if received:
        state.balance -= cost
    op.status = "TZ_OVER_OK"
    return {"response": 1, "tzid": tzid}


def _country_stat(state: MockState, code: int) -> Dict[str, Any]:
    name, locale = _country_name(code)
    services = {
        f"service_{slug}": {
            "count": 100,
            "popular": False,
            "code": code,
            "price": price,
            "id": i + 1,
            "service": slug,
            "slug": slug,
        }
        for i, (slug, price) in enumerate(state.prices.get(code, {}).items())
    }
    return {
        "name": name,
        "position": code,
        "code": code,
        "other": False,
        "new": False,
        "enabled": True,
        "services": services or [],
        "locale_name": locale,
    }


def _get_numbers_stats(state: MockState, req: MockRequest) -> Any:
    if req.query.get("country") == "all":
        return {str(code): _country_stat(state, code) for code in sorted(state.prices)} or []
    code = _int(req, "country", 7)
    return _country_stat(state, code) if code in state.prices else _error("NO_COUNTRY")


# ----- rent -----


def _rent_item(state: MockState, rent: MockRent, req: MockRequest) -> Dict[str, Any]:
    tariff = state.rent_tariffs.get(rent.country)
    days = dict(sorted(tariff["days"].items())) if tariff is not None else {}
    extendable = rent.extension and tariff is not None and tariff["extend"] == 1
    start = rent.tzid
    item: Dict[str, Any] = {
        "status": 1,
        "extension": 1 if rent.extension else 0,
        "messages": [
            {"id": m.id, "service": m.service, "text": m.text, "code": m.code or "", "created_at": m.created_at}
            for m in reversed(rent.messages)
        ],
        "webhook_url": state.webhook_url,
        "sum": _decimal(to_mills(rent.sum), 2),
        "country": rent.country,
        "start_time": stamp(start),
        "stop_time": stamp(start + rent.days * 86_400),
        "checked_time": stamp(start),
        "number": rent.number,
        "days_autoextend": 0,
        "rent": 1,
        "tzid": rent.tzid,
        "time": rent.days * 24 * 60,
        "days": rent.days,
        "hours": rent.days * 24,
        "extend": days if extendable else [],
        "checked": True,
        "reload": None,
        "day_extend": days.get(1, 0) if extendable else 0,
        "m_ext": False,
        "freeze": False,
    }
    if "number" in req.query:
        item["time_seconds"] = rent.days * 86_400
    return item


def _get_rent_num(state: MockState, req: MockRequest) -> Any:
    country = _int(req, "country", 7)
    tariff = state.rent_tariffs.get(country)
    if tariff is None:
        return _error("NO_COUNTRY")
    days = _int(req, "days", 1)
    price = tariff["days"].get(days)
    if price is None:
        return _error("UNDEFINED_DAYS")
    if state.available < to_mills(price):
        return _error("WARNING_LOW_BALANCE")
    tzid = state.next_id()
    state.balance -= to_mills(price)
    # `extension` defaults to 1 on the server; `0` makes the rent non-extendable for good.
    rent = MockRent(tzid, country, short_number(tzid), days, price, req.query.get("extension") != "0")
    state.rents[tzid] = rent
    return {"response": 1, "item": _rent_item(state, rent, req)}


def _get_rent_state(state: MockState, req: MockRequest) -> Any:
    if "tzid" in req.query:
        one = state.rents.get(_int(req, "tzid", -1))
        rents = [] if one is None else [one]
    else:
        rents = list(state.rents.values())
    for rent in rents:
        state.poll(rent.tzid)
    return {"response": 1, "list": [_rent_item(state, r, req) for r in rents]}


def _extend_rent_state(state: MockState, req: MockRequest) -> Any:
    rent = state.rents.get(_int(req, "tzid", 0))
    if rent is None:
        return _error("ERROR_WRONG_TZID")
    tariff = state.rent_tariffs.get(rent.country)
    if not rent.extension or tariff is None or tariff["extend"] != 1:
        return _error("TRY_AGAIN_LATER")
    days = _int(req, "days", 1)
    price = tariff["days"].get(days)
    if price is None:
        return _error("UNDEFINED_DAYS")
    if state.available < to_mills(price):
        return _error("WARNING_LOW_BALANCE")
    state.balance -= to_mills(price)
    rent.days += days
    rent.sum = from_mills(to_mills(rent.sum) + to_mills(price))
    return {"response": 1, "item": _rent_item(state, rent, req)}


def _close_rent_num(state: MockState, req: MockRequest) -> Any:
    tzid = _int(req, "tzid", 0)
    if state.rents.pop(tzid, None) is None:
        return _error("ERROR_WRONG_TZID")
    state.scheduled.pop(tzid, None)
    return {"response": "1"}


def _tariffs_rent(state: MockState, req: MockRequest) -> Any:
    def tariff(code: int) -> Any:
        t = state.rent_tariffs.get(code)
        if t is None:
            return []
        days = dict(sorted(t["days"].items()))
        count = {d: 100 for d in days}
        return {
            "code": code,
            "enabled": True,
            "name": _country_name(code)[0],
            "new": False,
            "position": code,
            "count": count,
            "days": days,
            "extend": t["extend"],
            "confirm": False,
            "ext_counts": count,
        }

    if "country" in req.query:
        return tariff(_int(req, "country", 0))
    return {str(code): tariff(code) for code in sorted(state.rent_tariffs)} or []


# ----- user -----


def _get_balance(state: MockState, req: MockRequest) -> Any:
    res: Dict[str, Any] = {"response": "1", "balance": _decimal(state.balance), "zbalance": from_mills(state.frozen)}
    if "income" in req.query:
        res.update(income=0, income_usd="0.000")
    return res


def _get_profile(state: MockState, req: MockRequest) -> Any:
    return {
        "response": "1",
        "profile": {
            "id": MOCK_USER_ID,
            "hash_id": "mock",
            "name": "mock@example.com",
            "username": "mock@example.com",
            "email": "mock@example.com",
            "email_verified_at": stamp(),
            "active": "true",
            "apikey": state.api_key,
            "api_access": True,
            "is_api": True,
            "number": None,
            "country": None,
            "locale": "en",
            "currency": "USD",
            "number_region": None,
            "number_country": None,
            "number_reject": [],
            "ugroup": 1,
            "verify": 0,
            "block": 0,
            "resetCount": None,
            "created_at": stamp(),
            "notification_at": None,
            "first_login": False,
            "sub": 0,
            "disable": False,
            "webhook_url": state.webhook_url,
            "is_project_subscription": False,
        },
    }


def _is_http_url(value: str) -> bool:
    try:
        url = urllib.parse.urlsplit(value)
        return url.scheme in ("http", "https") and bool(url.hostname)
    except ValueError:
        return False


def _profile(state: MockState, req: MockRequest) -> Any:
    body = req.body
    profile = body.get("profile") if isinstance(body, dict) else None
    if req.method != "POST" or not isinstance(profile, dict):
        return _error("ERROR_PARAMS")
    if "webhook_url" in profile:
        url = profile["webhook_url"]
        if url is not None and (not isinstance(url, str) or not _is_http_url(url)):
            return {"response": {"webhook_url": ["The webhook url must be a valid URL."]}}
        state.webhook_url = url
    return {"response": "1", "user": {"id": MOCK_USER_ID, "webhook_url": state.webhook_url}}


def _webhook_logs(state: MockState, req: MockRequest) -> Any:
    return {"response": "1", "data": _paginate(state.webhook_logs[::-1], _int(req, "page", 1), 10, "webhook-logs")}


def _get_payment_history(state: MockState, req: MockRequest) -> Any:
    return {
        "response": "1",
        "orders": _paginate([], _int(req, "page", 1), 10, "getPaymentHistory.php"),
        "paylist": [],
        "domains": [],
        "currency": {"USD": 1},
    }


# ----- free -----

# country -> (name, text, short number -> [(sender, text)])
_FREE: Mapping[int, Tuple[str, str, Mapping[str, List[Tuple[str, str]]]]] = {
    7: ("russia", "Russia", {"9001234567": [("Telegram", "Telegram code: 51423")]}),
    44: (
        "united_kingdom",
        "United Kingdom",
        {
            "7459608320": [
                ("Amazon", "Amazon: Use 195895 to reset your password."),
                ("Microsoft", "Microsoft access code: 2991"),
            ]
        },
    ),
}


def _get_free_list(state: MockState, req: MockRequest) -> Any:
    codes = list(_FREE)
    wanted = _int(req, "country", 44)
    country = wanted if wanted in _FREE else codes[0]
    name, _text, by_number = _FREE[country]
    numbers = {
        n: {
            "country": country,
            "country_original": name,
            "data_humans": "1 day ago",
            "full_number": f"{country}{n}",
            "is_archive": False,
        }
        for n in by_number
    }
    asked = req.query.get("number")
    number = asked if asked is not None and asked in by_number else next(iter(by_number))
    messages = [
        {
            "id": i + 1,
            "text": text,
            "in_number": sender,
            "my_number": number,
            "created_at": stamp(i),
            "data_humans": "1 day ago",
            "code": extract_code(text) or "-",
        }
        for i, (sender, text) in enumerate(by_number[number])
    ]
    page = _paginate(messages, _int(req, "page", 1), _int(req, "count", 10), "getFreeList")
    return {
        "response": 1,
        "countries": [{"country": c, "country_text": _FREE[c][1], "country_original": _FREE[c][0]} for c in codes],
        "numbers": numbers,
        "messages": {**page, "number": number, "country": country},
    }


ROUTES: Mapping[str, Handler] = {
    "getPrice.php": _get_price,
    "getNum.php": _get_num,
    "getState.php": _get_state,
    "setOperationRevise.php": _set_operation_revise,
    "setOperationOk.php": _set_operation_ok,
    "getNumbersStats.php": _get_numbers_stats,
    "rent/getRentNum.php": _get_rent_num,
    "rent/getRentState.php": _get_rent_state,
    "rent/extendRentState.php": _extend_rent_state,
    "rent/closeRentNum.php": _close_rent_num,
    "rent/tariffsRent.php": _tariffs_rent,
    "getBalance.php": _get_balance,
    "getProfile.php": _get_profile,
    "profile.php": _profile,
    "webhook-logs": _webhook_logs,
    "getPaymentHistory.php": _get_payment_history,
    "getFreeList": _get_free_list,
}

"""MockOnlineSim through the real client: every endpoint, every control helper."""

from __future__ import annotations

from typing import Callable

import pytest

from onlinesimru import (
    ApiError,
    HttpRequest,
    MockOnlineSim,
    MockRequest,
    NoNumberError,
    OnlineSim,
    TransportError,
)


def no_sleep(_seconds: float) -> None:
    pass


# ----- auth and transport -----


def test_wrong_or_missing_key_is_http_456_mapped_to_api_error() -> None:
    mock = MockOnlineSim()
    for api_key in ("nope", ""):
        with pytest.raises(ApiError) as error:
            mock.client(api_key=api_key).user.balance()
        assert error.value.code == "ERROR_WRONG_KEY"


def test_tariffs_and_free_numbers_need_no_key() -> None:
    client = MockOnlineSim().client(api_key="")
    assert client.numbers.tariffs_one(44)["code"] == 44
    assert client.rent.tariffs_one(7)["code"] == 7
    assert client.free.list()["messages"]["country"] == 44


def test_transport_of_a_hand_built_client_with_any_base_url() -> None:
    mock = MockOnlineSim(api_key="k", balance=5)
    client = OnlineSim("k", transport=mock.transport)
    assert client.user.balance() == {"balance": 5, "zbalance": 0, "income": 0}
    assert mock.requests == [MockRequest("GET", "getBalance.php", {"income": "1", "lang": "en"}, None)]


def test_unknown_endpoint_is_a_non_json_404() -> None:
    res = MockOnlineSim().transport(HttpRequest("GET", "https://x.test/api/nope.php", {}, None, 1))
    assert res.status == 404
    with pytest.raises(TransportError) as error:
        MockOnlineSim().client()._request("nope.php")
    assert error.value.status == 404


# ----- numbers -----


def test_price() -> None:
    client = MockOnlineSim().client()
    assert client.numbers.price("telegram", 7) == 1.2
    assert client.numbers.price("nope", 7) is None
    assert code_of(lambda: client.numbers.price("google", 999)) == "UNDEFINED_COUNTRY"


def test_get_freezes_the_price_and_numbers_are_deterministic() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    assert client.numbers.get("google", 44) == 1
    assert client.numbers.get_with_number("vkcom") == {
        "tzid": 2,
        "number": "+7900000002",
        "country": 7,
        "time": 1200,
        "service": "vkcom",
    }
    assert [r.query.get("number") for r in mock.requests] == [None, "1"]
    assert client.user.balance() == {"balance": 100, "zbalance": 0.7, "income": 0}
    assert [(o.tzid, o.number, o.status) for o in mock.operations()] == [
        (1, "+44900000001", "TZ_NUM_WAIT"),
        (2, "+7900000002", "TZ_NUM_WAIT"),
    ]


def code_of(call: Callable[[], object]) -> str:
    """The ApiError code raised by ``call()``."""
    with pytest.raises(ApiError) as error:
        call()
    return error.value.code


def test_get_errors_unknown_country_service_low_balance_reject() -> None:
    mock = MockOnlineSim(balance=0.25)
    client = mock.client()
    assert code_of(lambda: client.numbers.get("google", 999)) == "UNDEFINED_COUNTRY"
    assert code_of(lambda: client.numbers.get("nope", 7)) == "ERROR_NO_SERVICE"
    assert code_of(lambda: client.numbers.get("google", 7)) == "WARNING_LOW_BALANCE"
    with pytest.raises(NoNumberError):
        client.numbers.get("google", 44, reject=["4490", "7"])
    assert mock.requests[-1].query["reject"] == "4490,7"
    # a non-matching reject passes; the rejected attempt did not consume a number
    assert client.numbers.get_with_number("google", 44, reject=["4480"])["number"] == "+44900000001"
    # 0.25 - 0.2 frozen = 0.05 available
    assert code_of(lambda: client.numbers.get("google", 44)) == "WARNING_LOW_BALANCE"


def test_state_list_one_and_lifecycle() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    assert client.numbers.state() == []
    a = client.numbers.get("google", 44)
    b = client.numbers.get("vkcom", 7)
    one = client.numbers.state_one(a)
    assert one["tzid"] == a
    assert one["response"] == "TZ_NUM_WAIT"
    assert one["number"] == "+44900000001"
    assert one["sum"] == 0.2
    assert one["guard_interval_remaining_seconds"] == 0
    assert "msg" not in one

    mock.add_sms(a, "Your Google code is G-123 456. Do not share it.")
    one = client.numbers.state_one(a)
    assert (one["response"], one.get("msg")) == ("TZ_NUM_ANSWER", "123456")
    full = client.numbers.state_one(a, message_to_code=False)
    assert full.get("msg") == "Your Google code is G-123 456. Do not share it."
    assert [o["tzid"] for o in client.numbers.state(order_by="desc")] == [b, a]

    client.numbers.close(a)
    closed = client.numbers.state_one(a)
    assert (closed["response"], closed.get("time")) == ("TZ_OVER_OK", 0)
    assert code_of(lambda: client.numbers.state_one(999)) == "ERROR_NO_OPERATIONS"


def test_full_text_without_code_next_and_msg_list() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    tzid = client.numbers.get("telegram")
    mock.add_sms(tzid, "Welcome!", service="telegram")
    assert client.numbers.state_one(tzid).get("msg") == "Welcome!"
    client.numbers.next(tzid)
    waiting = client.numbers.state_one(tzid)
    assert waiting["response"] == "TZ_NUM_WAIT"
    assert "msg" not in waiting
    mock.add_sms(tzid, "code 98765")
    assert client.numbers.state_one(tzid).get("msg") == "98765"
    assert client.numbers.state_one(tzid, msg_list=True).get("msg") == [
        {"service": "telegram", "msg": "Welcome!"},
        {"service": "telegram", "msg": "98765"},
    ]
    assert client.numbers.next(424242) is True  # always succeeds, like the backend


def test_close_spends_or_refunds_and_ban_after_sms_answers_0() -> None:
    mock = MockOnlineSim(balance=10)
    client = mock.client()
    paid = client.numbers.get("telegram")
    empty = client.numbers.get("telegram")
    mock.add_sms(paid, "1111")
    assert code_of(lambda: client.numbers.ban(paid)) == "0"
    client.numbers.close(paid)
    client.numbers.close(empty)
    assert client.user.balance() == {"balance": 8.8, "zbalance": 0, "income": 0}
    assert mock.balance() == 8.8
    assert code_of(lambda: client.numbers.close(paid)) == "ERROR_WRONG_TZID"
    assert code_of(lambda: client.numbers.close(999)) == "ERROR_WRONG_TZID"
    banned = client.numbers.get("google")
    assert client.numbers.ban(banned) is True
    assert next(o.status for o in mock.operations() if o.tzid == banned) == "TZ_OVER_OK"


def test_guard_interval_blocks_close_without_sms() -> None:
    mock = MockOnlineSim(guard_interval=120)
    client = mock.client()
    tzid = client.numbers.get("google")
    assert client.numbers.state_one(tzid).get("guard_interval_remaining_seconds") == 120
    assert code_of(lambda: client.numbers.close(tzid)) == "NO_COMPLETE_TZID"
    mock.add_sms(tzid, "5555")
    assert client.numbers.state_one(tzid).get("guard_interval_remaining_seconds") == 0
    assert client.numbers.close(tzid) is True


def test_wait_code_with_add_sms_after_and_zero_interval() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    tzid = client.numbers.get("google", 44)
    mock.add_sms_after(tzid, "Your code: 4321", 2)
    assert client.numbers.wait_code(tzid, interval=0, sleep=no_sleep) == "4321"
    assert [r.path for r in mock.requests] == [
        "getNum.php",
        "getState.php",
        "getState.php",
        "getState.php",
        "setOperationOk.php",
    ]
    assert mock.operations()[0].status == "TZ_OVER_OK"


def test_wait_code_keep_open_and_since_polls_listing_all_count_too() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    tzid = client.numbers.get("google", 44)
    mock.add_sms_after(tzid, "1111", 0)
    first = client.numbers.wait_code(tzid, interval=0, sleep=no_sleep, keep_open=True)
    mock.add_sms_after(tzid, "2222", 1)
    client.numbers.state()  # one poll of every operation
    assert client.numbers.wait_code(tzid, interval=0, sleep=no_sleep, since=first) == "2222"


def test_tariffs_from_prices() -> None:
    client = MockOnlineSim().client()
    tariffs = client.numbers.tariffs()
    assert list(tariffs) == ["7", "44"]
    assert tariffs["44"]["services"]["service_vkcom"] == {
        "count": 100,
        "popular": False,
        "code": 44,
        "price": 0.36,
        "id": 2,
        "service": "vkcom",
        "slug": "vkcom",
    }
    assert code_of(lambda: client.numbers.tariffs_one(1)) == "NO_COUNTRY"
    empty = MockOnlineSim(prices={1: {}}).client()
    assert empty.numbers.tariffs_one(1)["services"] == {}  # `[]` on the wire


# ----- rent -----


def test_rent_get_state_extend_close() -> None:
    mock = MockOnlineSim(balance=10)
    client = mock.client()
    rent = client.rent.get(7, 3)
    assert (rent["tzid"], rent["number"], rent["sum"], rent["days"]) == (1, "900000001", 2.5, 3)
    assert (rent["time"], rent["extension"], rent["messages"]) == (3 * 1440, 1, [])
    assert rent.get("time_seconds") == 3 * 86400
    assert rent["extend"] == {"1": 1, "3": 2.5, "7": 5}
    assert mock.balance() == 7.5

    mock.add_sms(rent["tzid"], "Bank: 777 888", service="bank")
    mock.add_sms(rent["tzid"], "no code here")
    state = client.rent.state_one(rent["tzid"])
    assert [(m["service"], m["code"]) for m in state["messages"]] == [("other", ""), ("bank", "777888")]  # newest first

    extended = client.rent.extend(rent["tzid"], 1)
    assert (extended["days"], extended["sum"]) == (4, 3.5)
    assert mock.balance() == 6.5

    fixed = client.rent.get(7, 1, False)
    assert (fixed["extension"], fixed["extend"]) == (0, {})
    assert code_of(lambda: client.rent.extend(fixed["tzid"])) == "TRY_AGAIN_LATER"
    assert [r["tzid"] for r in client.rent.state()] == [rent["tzid"], fixed["tzid"]]

    client.rent.close(fixed["tzid"])
    assert [r.tzid for r in mock.rents()] == [rent["tzid"]]
    assert code_of(lambda: client.rent.state_one(fixed["tzid"])) == "ERROR_NO_OPERATIONS"
    assert code_of(lambda: client.rent.close(fixed["tzid"])) == "ERROR_WRONG_TZID"


def test_rent_errors() -> None:
    client = MockOnlineSim(balance=1.5).client()
    assert code_of(lambda: client.rent.get(44)) == "NO_COUNTRY"
    assert code_of(lambda: client.rent.get(7, 2)) == "UNDEFINED_DAYS"
    assert code_of(lambda: client.rent.get(7, 3)) == "WARNING_LOW_BALANCE"


def test_rent_add_sms_after_and_tariffs() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    tzid = client.rent.get()["tzid"]
    mock.add_sms_after(tzid, "6060", 1)
    assert client.rent.state_one(tzid)["messages"] == []
    message = client.rent.state()[0]["messages"][0]
    assert (message["code"], message["service"]) == ("6060", "other")
    count = {"1": 100, "3": 100, "7": 100}
    assert client.rent.tariffs() == {
        "7": {
            "code": 7,
            "enabled": True,
            "name": "russia",
            "new": False,
            "position": 7,
            "count": count,
            "days": {"1": 1, "3": 2.5, "7": 5},
            "extend": 1,
            "confirm": False,
            "ext_counts": count,
        }
    }
    assert code_of(lambda: client.rent.tariffs_one(44)) == "NO_COUNTRY"


# ----- user and free -----


def test_profile_webhook_set_validate_clear_and_logs() -> None:
    mock = MockOnlineSim(api_key="secret")
    client = mock.client()
    profile = client.user.profile()
    assert (profile["id"], profile.get("apikey"), profile.get("webhook_url")) == (1, "secret", None)
    with pytest.raises(ApiError) as error:
        client.user.set_webhook_url("ftp://x")
    assert (error.value.code, error.value.message) == ("VALIDATION_ERROR", "The webhook url must be a valid URL.")
    client.user.set_webhook_url("https://example.com/hook")
    last = mock.requests[-1]
    assert (last.method, last.path) == ("POST", "profile.php")
    assert last.body == {"profile": {"webhook_url": "https://example.com/hook"}}
    assert client.user.profile().get("webhook_url") == "https://example.com/hook"

    tzid = client.numbers.get("google", 44)
    mock.add_sms(tzid, "code 1234")
    rent = client.rent.get()
    mock.add_sms(rent["tzid"], "code 5678")
    logs = client.user.webhook_logs()
    assert (logs["total"], logs["current_page"], logs["per_page"]) == (2, 1, 10)
    assert [(log["type"], log["params"]["operation_id"], log["params"]["code"]) for log in logs["data"]] == [
        ("rent_sms", rent["tzid"], "5678"),
        ("receiving_sms", tzid, "1234"),
    ]

    client.user.clear_webhook_url()
    assert client.user.profile().get("webhook_url") is None


def test_balance_includes_frozen_and_payment_history_is_empty() -> None:
    mock = MockOnlineSim(balance=3)
    client = mock.client()
    client.numbers.get("telegram")
    assert client.user.balance() == {"balance": 3, "zbalance": 1.2, "income": 0}
    history = client.user.payment_history()
    assert history["paylist"] == {}
    assert (history["orders"]["data"], history["orders"]["total"], history["orders"]["current_page"]) == ([], 0, 1)


def test_free_list() -> None:
    client = MockOnlineSim().client()
    uk = client.free.list()
    assert [c["country"] for c in uk["countries"]] == [7, 44]
    assert list(uk["numbers"]) == ["7459608320"]
    assert (uk["messages"]["number"], uk["messages"]["country"], uk["messages"]["total"]) == ("7459608320", 44, 2)
    assert uk["messages"]["data"][0]["code"] == "195895"
    ru = client.free.list(country=7)
    assert (ru["messages"]["data"][0]["code"], ru["messages"]["data"][0]["my_number"]) == ("51423", "9001234567")


# ----- control API -----


def test_fail_next_once_optionally_for_one_endpoint() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    mock.fail_next("NO_NUMBER", endpoint="getNum.php")
    assert client.user.balance()["balance"] == 100  # other endpoint: untouched
    with pytest.raises(NoNumberError):
        client.numbers.get("google")
    assert client.numbers.get("google") == 1
    mock.fail_next("TRY_AGAIN_LATER")
    assert code_of(client.user.profile) == "TRY_AGAIN_LATER"


def test_fail_next_transport_once_and_wait_code_retries_it() -> None:
    mock = MockOnlineSim()
    client = mock.client()
    mock.fail_next_transport()
    with pytest.raises(TransportError) as error:
        client.user.balance()
    assert error.value.status == 502

    tzid = client.numbers.get("google")
    mock.add_sms(tzid, "3030")
    mock.fail_next_transport(status=503, endpoint="getState.php")
    assert client.numbers.wait_code(tzid, interval=0, sleep=no_sleep) == "3030"


def test_unknown_ids_set_balance_requests_log_and_reset() -> None:
    mock = MockOnlineSim(balance=1)
    client = mock.client(lang="ru")
    with pytest.raises(ValueError, match="no open operation or rent 5"):
        mock.add_sms(5, "x")
    with pytest.raises(ValueError, match="no operation or rent 5"):
        mock.add_sms_after(5, "x", 1)
    mock.set_balance(50)
    assert mock.balance() == 50
    tzid = client.numbers.get("telegram")
    client.numbers.close(tzid)
    with pytest.raises(ValueError):
        mock.add_sms(tzid, "late")  # closed
    assert mock.requests[0] == MockRequest("GET", "getNum.php", {"service": "telegram", "country": "7", "lang": "ru"})

    mock.fail_next("NO_NUMBER")
    mock.reset()
    assert mock.balance() == 1
    assert mock.operations() == []
    assert mock.rents() == []
    assert mock.requests == []
    assert client.numbers.get("google", 44) == 1  # ids restart, failure queue cleared


def test_operations_returns_copies() -> None:
    mock = MockOnlineSim()
    mock.client().numbers.get("google")
    mock.operations()[0].status = "TZ_OVER_OK"
    assert mock.operations()[0].status == "TZ_NUM_WAIT"

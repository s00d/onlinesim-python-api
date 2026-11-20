from __future__ import annotations

from .helpers import Reply, fake_client, fixture, ok


def test_balance_income_and_decimal_string() -> None:
    client, fake = fake_client(Reply(fixture("getBalance")))
    assert client.user.balance() == {"balance": 1442.33, "zbalance": 1023.41, "income": 9.78}
    assert fake.last().path == "/api/getBalance.php"
    assert fake.last().query == {"income": "1"}


def test_balance_without_income() -> None:
    client, _ = fake_client(ok(balance="0.000", zbalance=0))
    assert client.user.balance() == {"balance": 0, "zbalance": 0}


def test_profile() -> None:
    client, fake = fake_client(Reply(fixture("getProfile")))
    profile = client.user.profile()
    assert fake.last().path == "/api/getProfile.php"
    assert profile["id"] == 1
    assert profile.get("webhook_url") == "https://example.com/hook"
    assert profile.get("number_reject") == ["333"]


def test_profile_number_int_and_country_string() -> None:
    client, _ = fake_client(ok(profile={"id": 1, "number": 79001234567, "country": "RU"}))
    profile = client.user.profile()
    assert (profile.get("number"), profile.get("country")) == (79001234567, "RU")


def test_payment_history_keeps_list_paylist_and_nullable_order_fields() -> None:
    body = fixture("getPaymentHistory")
    order = {
        "id": 1,
        "sum": "10.00",
        "currency": None,
        "form_text": None,
        "stat": 0,
        "created_at": "2026-06-14 09:12:12",
    }
    paylist = [{"id": 0, "name": "Card"}, {"id": 1, "name": "Crypto"}]
    client, _ = fake_client(Reply({**body, "paylist": paylist, "orders": {**body["orders"], "data": [order]}}))
    history = client.user.payment_history()
    assert history["paylist"] == paylist
    first = history["orders"]["data"][0]
    assert (first.get("currency"), first.get("form_text")) == (None, None)


def test_payment_history_keeps_empty_paylist() -> None:
    client, fake = fake_client(Reply(fixture("getPaymentHistory")))
    history = client.user.payment_history(2)
    assert fake.last().path == "/api/getPaymentHistory.php"
    assert fake.last().query == {"page": "2"}
    assert history["paylist"] == []
    order = history["orders"]["data"][0]
    assert (order.get("id"), order.get("sum")) == (9462, "89.00")


def test_set_webhook_url_posts_json() -> None:
    client, fake = fake_client(ok(user={"id": 2}))
    assert client.user.set_webhook_url("https://example.com/hook") is True
    call = fake.last()
    assert call.method == "POST"
    assert call.path == "/api/profile.php"
    assert call.headers["Content-Type"] == "application/json"
    assert call.headers["Authorization"] == "Bearer test-key"
    assert call.body == {"profile": {"webhook_url": "https://example.com/hook"}}


def test_clear_webhook_url_posts_null() -> None:
    client, fake = fake_client(ok(user={"id": 2}))
    assert client.user.clear_webhook_url() is True
    assert fake.last().method == "POST"
    assert fake.last().body == {"profile": {"webhook_url": None}}


def test_webhook_logs() -> None:
    page = {
        "current_page": 1,
        "data": [
            {
                "id": 7,
                "user_id": 2,
                "webhook_url": "https://example.com/hook",
                "type": "receiving_sms",
                "params": {"webhook_type": "receiving_sms", "operation_id": 1520, "code": "195895"},
                "status": "success",
                "error": None,
                "created_at": "2026-11-19 10:00:01",
                "updated_at": "2026-11-19 10:00:01",
            }
        ],
        "from": 1,
        "to": 1,
        "last_page": 1,
        "per_page": 10,
        "total": 1,
    }
    client, fake = fake_client(ok(data=page))
    assert client.user.webhook_logs() == page
    assert fake.last().path == "/api/webhook-logs"
    assert fake.last().query == {"page": "1"}

from __future__ import annotations

import pytest

from onlinesimru import ApiError

from .helpers import Reply, fake_client, fixture, ok


def test_price() -> None:
    client, fake = fake_client(ok(price=0.36))
    assert client.numbers.price("vkcom", 44) == 0.36
    assert fake.last().path == "/api/getPrice.php"
    assert fake.last().query == {"service": "vkcom", "country": "44"}


def test_price_none() -> None:
    client, _ = fake_client(ok(price=None))
    assert client.numbers.price("vkcom") is None


def test_get_no_number_flag_reject_comma_list() -> None:
    client, fake = fake_client(Reply({"response": 1, "tzid": 1520}))
    assert client.numbers.get("google", 44, reject=["4470", 4471]) == 1520
    assert fake.last().path == "/api/getNum.php"
    assert fake.last().query == {"service": "google", "country": "44", "reject": "4470,4471"}


def test_get_defaults_country_7_and_omits_empty_reject() -> None:
    client, fake = fake_client(Reply({"response": 1, "tzid": 1}))
    client.numbers.get("google", reject=[])
    assert fake.last().query == {"service": "google", "country": "7"}


def test_get_with_number() -> None:
    order = {"tzid": 1520, "number": "+447459608320", "country": 44, "time": 1200, "service": "google"}
    client, fake = fake_client(Reply({"response": 1, **order}))
    assert client.numbers.get_with_number("google", 44) == order
    assert fake.last().query == {"service": "google", "country": "44", "number": "1"}


def test_state_booleans_lowercase_orderby_number_flag() -> None:
    ops = fixture("getState")
    client, fake = fake_client(Reply(ops))
    result = client.numbers.state(order_by="desc", msg_list=True)
    assert result == ops
    assert result[0].get("msg") == "195895"
    assert fake.last().path == "/api/getState.php"
    assert fake.last().query == {"message_to_code": "1", "orderby": "desc", "msg_list": "1", "number": "1"}


def test_state_defaults() -> None:
    client, fake = fake_client(Reply([]))
    client.numbers.state()
    assert fake.last().query == {"message_to_code": "1", "orderby": "asc", "msg_list": "0", "number": "1"}


def test_state_empty_on_no_operations() -> None:
    client, _ = fake_client(Reply({"response": "ERROR_NO_OPERATIONS"}))
    assert client.numbers.state() == []


def test_state_one() -> None:
    op = fixture("getState")[0]
    client, fake = fake_client(Reply([op]))
    assert client.numbers.state_one(594, message_to_code=False) == op
    assert fake.last().query == {"tzid": "594", "message_to_code": "0", "msg_list": "0", "number": "1"}


def test_state_one_raises_no_operations() -> None:
    client, _ = fake_client(Reply({"response": "ERROR_NO_OPERATIONS"}), Reply([]))
    for _ in range(2):
        with pytest.raises(ApiError) as info:
            client.numbers.state_one(1)
        assert info.value.code == "ERROR_NO_OPERATIONS"


def test_next() -> None:
    client, fake = fake_client(ok(tzid="1520"))
    assert client.numbers.next(1520) is True
    assert fake.last().path == "/api/setOperationRevise.php"
    assert fake.last().query == {"tzid": "1520"}


def test_close() -> None:
    client, fake = fake_client(Reply({"response": 1, "tzid": 1520}))
    assert client.numbers.close(1520) is True
    assert fake.last().path == "/api/setOperationOk.php"
    assert fake.last().query == {"tzid": "1520"}


def test_ban() -> None:
    client, fake = fake_client(Reply({"response": 1, "tzid": 1520}))
    assert client.numbers.ban(1520) is True
    assert fake.last().query == {"tzid": "1520", "ban": "1"}


def test_close_no_complete_tzid() -> None:
    client, _ = fake_client(Reply({"response": "NO_COMPLETE_TZID"}))
    with pytest.raises(ApiError) as info:
        client.numbers.close(1)
    assert info.value.code == "NO_COMPLETE_TZID"


def test_tariffs_country_all_normalises_empty_services() -> None:
    uk = fixture("getNumbersStats_44")
    client, fake = fake_client(Reply({"44": uk, "7": {**uk, "code": 7, "services": []}}))
    tariffs = client.numbers.tariffs()
    assert fake.last().path == "/api/getNumbersStats.php"
    assert fake.last().query == {"country": "all"}
    assert tariffs["44"]["services"]["service_vkcom"]["slug"] == "vkcom"
    assert tariffs["7"]["services"] == {}


def test_tariffs_one() -> None:
    uk = fixture("getNumbersStats_44")
    client, fake = fake_client(Reply(uk))
    assert client.numbers.tariffs_one(44) == uk
    assert fake.last().query == {"country": "44"}


def test_tariffs_one_no_country() -> None:
    client, _ = fake_client(Reply({"response": "NO_COUNTRY"}))
    with pytest.raises(ApiError) as info:
        client.numbers.tariffs_one(999)
    assert info.value.code == "NO_COUNTRY"

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from onlinesimru import ApiError

from .helpers import Reply, fake_client, fixture, ok

DETAIL = {"pagination": "0", "number": "1"}


def items() -> List[Dict[str, Any]]:
    return list(fixture("rent_getRentState")["list"])


def test_get_sends_extension_pagination_number_and_parses_sum() -> None:
    client, fake = fake_client(Reply({"response": 1, "item": items()[0]}))
    rent = client.rent.get(7, 3)
    assert fake.last().path == "/api/rent/getRentNum.php"
    assert fake.last().query == {"country": "7", "days": "3", "extension": "1", **DETAIL}
    assert rent["sum"] == 5.14
    assert rent["extend"] == {"1": 14.7, "3": 25.3, "7": 51}
    assert rent["messages"][0]["code"] == "195895"


def test_get_extension_false() -> None:
    client, fake = fake_client(Reply({"response": 1, "item": items()[1]}))
    client.rent.get(7, 1, False)
    assert fake.last().query["extension"] == "0"


def test_state_normalises_sum_and_empty_extend() -> None:
    client, fake = fake_client(Reply(fixture("rent_getRentState")))
    rents = client.rent.state()
    assert fake.last().path == "/api/rent/getRentState.php"
    assert fake.last().query == DETAIL
    assert [r["sum"] for r in rents] == [5.14, 0]
    assert rents[1]["extend"] == {}


def test_state_one() -> None:
    client, fake = fake_client(Reply({"response": 1, "list": [items()[0]]}))
    rent = client.rent.state_one(430)
    assert (rent["tzid"], rent["sum"]) == (430, 5.14)
    assert fake.last().query == {"tzid": "430", **DETAIL}


def test_state_one_empty_list() -> None:
    client, _ = fake_client(Reply({"response": 1, "list": []}))
    with pytest.raises(ApiError) as info:
        client.rent.state_one(1)
    assert info.value.code == "ERROR_NO_OPERATIONS"


def test_extend() -> None:
    client, fake = fake_client(Reply({"response": 1, "item": items()[0]}))
    assert client.rent.extend(430, 3)["tzid"] == 430
    assert fake.last().path == "/api/rent/extendRentState.php"
    assert fake.last().query == {"tzid": "430", "days": "3", **DETAIL}


def test_tariffs() -> None:
    tariffs = fixture("rent_tariffsRent")
    client, fake = fake_client(Reply(tariffs))
    assert client.rent.tariffs() == tariffs
    assert fake.last().path == "/api/rent/tariffsRent.php"
    assert fake.last().query == {}


def test_tariffs_one() -> None:
    ru = fixture("rent_tariffsRent")["7"]
    client, fake = fake_client(Reply(ru))
    assert client.rent.tariffs_one() == ru
    assert fake.last().query == {"country": "7"}


def test_tariffs_one_no_country_for_empty_list() -> None:
    client, _ = fake_client(Reply([]))
    with pytest.raises(ApiError) as info:
        client.rent.tariffs_one(999)
    assert info.value.code == "NO_COUNTRY"


def test_close() -> None:
    client, fake = fake_client(ok())
    assert client.rent.close(430) is True
    assert fake.last().path == "/api/rent/closeRentNum.php"
    assert fake.last().query == {"tzid": "430"}


def test_close_no_close_rent_us() -> None:
    client, _ = fake_client(Reply({"response": "NO_CLOSE_RENT_US"}))
    with pytest.raises(ApiError) as info:
        client.rent.close(1)
    assert info.value.code == "NO_CLOSE_RENT_US"

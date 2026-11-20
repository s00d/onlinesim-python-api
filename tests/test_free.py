from __future__ import annotations

from .helpers import Reply, fake_client, fixture


def test_list_no_php_suffix_only_set_params() -> None:
    client, fake = fake_client(Reply(fixture("getFreeList")))
    result = client.free.list(country=44, number="7459608320", count=20)
    assert fake.last().path == "/api/getFreeList"
    assert fake.last().query == {"country": "44", "number": "7459608320", "count": "20"}
    assert list(result) == ["countries", "numbers", "messages"]
    assert result["numbers"]["7459608320"]["full_number"] == "447459608320"
    assert result["messages"]["data"][0]["code"] == "195895"


def test_list_normalises_empty_numbers() -> None:
    client, fake = fake_client(Reply({"response": 1, "countries": [], "numbers": [], "messages": {"data": []}}))
    assert client.free.list()["numbers"] == {}
    assert fake.last().query == {}


def test_list_accepts_null_country_texts() -> None:
    country = {"country": 999, "country_text": None, "country_original": None}
    client, _ = fake_client(Reply({"response": 1, "countries": [country], "numbers": [], "messages": {"data": []}}))
    assert client.free.list()["countries"] == [country]

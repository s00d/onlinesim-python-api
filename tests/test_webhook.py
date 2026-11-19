from __future__ import annotations

import json

import pytest

from onlinesimru import OnlineSimError, parse_webhook


def test_receiving_sms_json_string() -> None:
    payload = {
        "webhook_type": "receiving_sms",
        "operation_id": 1520,
        "user_id": 2,
        "country_code": 7,
        "number": "+79001234567",
        "sender": "VK",
        "message": "VK: 195895 is your code",
        "code": "195895",
        "time_start": "2026-11-19 10:00:00",
        "time_left": 1100,
    }
    assert parse_webhook(json.dumps(payload)) == payload
    assert parse_webhook(json.dumps(payload).encode()) == payload


def test_lenient() -> None:
    parsed = parse_webhook(
        {"webhook_type": "rent_sms", "operation_id": "430", "code": 2991, "time_left": "soon", "extra": True}
    )
    assert parsed == {
        "webhook_type": "rent_sms",
        "operation_id": 430,
        "user_id": None,
        "country_code": None,
        "number": None,
        "sender": None,
        "message": None,
        "code": "2991",
        "time_start": None,
        "time_left": None,
    }
    assert parse_webhook({"webhook_type": "other"})["webhook_type"] is None
    assert parse_webhook({"user_id": True, "operation_id": 1.5})["user_id"] is None
    assert parse_webhook({"operation_id": 1.5})["operation_id"] is None


@pytest.mark.parametrize("payload", ["not json", "[1,2]", "null"])
def test_raises_only_for_non_objects(payload: str) -> None:
    with pytest.raises(OnlineSimError):
        parse_webhook(payload)


def test_not_object_message() -> None:
    with pytest.raises(OnlineSimError, match="not a JSON object"):
        parse_webhook("[1,2]")

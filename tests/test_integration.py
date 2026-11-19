"""Opt-in integration test against a LOCAL backend. Skipped unless both are set:
  ONLINESIM_IT_BASE=https://on.test/api/  ONLINESIM_IT_KEY=<apikey>
With ONLINESIM_IT_MOCK=1 it also runs the number lifecycle on the provider-free `test` driver
(`spec/verify/backend_mock.php setup` first, a key of a user without webhook_url, teardown after).
"""

from __future__ import annotations

import functools
import json
import os
import re
import ssl
from urllib.parse import urljoin, urlsplit

import pytest

from onlinesimru import ApiError, HttpRequest, NoNumberError, OnlineSim, urllib_transport

BASE = os.environ.get("ONLINESIM_IT_BASE", "")
KEY = os.environ.get("ONLINESIM_IT_KEY", "")
MOCK = os.environ.get("ONLINESIM_IT_MOCK") == "1"
ENABLED = bool(BASE and KEY)

if ENABLED:
    host = urlsplit(BASE).hostname or ""
    if not (host in ("localhost", "127.0.0.1") or host.endswith((".test", ".localhost"))):
        raise RuntimeError(f"refusing non-local integration host {host}")

# Test-only transport: local backends use a self-signed certificate. Not part of the SDK API.
_insecure = ssl.create_default_context()
_insecure.check_hostname = False
_insecure.verify_mode = ssl.CERT_NONE
insecure_transport = functools.partial(urllib_transport, context=_insecure)

read_only = pytest.mark.skipif(not ENABLED, reason="set ONLINESIM_IT_BASE and ONLINESIM_IT_KEY")
lifecycle = pytest.mark.skipif(not (ENABLED and MOCK), reason="also set ONLINESIM_IT_MOCK=1")


@pytest.fixture(scope="module")
def client() -> OnlineSim:
    return OnlineSim(KEY, base_url=BASE, transport=insecure_transport)


@read_only
class TestReadOnly:
    def test_balance(self, client: OnlineSim) -> None:
        b = client.user.balance()
        assert isinstance(b["balance"], (int, float))
        assert isinstance(b["zbalance"], (int, float))

    def test_profile(self, client: OnlineSim) -> None:
        assert isinstance(client.user.profile()["id"], int)

    def test_numbers_tariffs_one(self, client: OnlineSim) -> None:
        uk = client.numbers.tariffs_one(44)
        assert uk["code"] == 44
        assert isinstance(uk["services"], dict)

    def test_numbers_state(self, client: OnlineSim) -> None:
        assert isinstance(client.numbers.state(), list)

    def test_rent_tariffs_one(self, client: OnlineSim) -> None:
        assert client.rent.tariffs_one(7)["code"] == 7

    def test_rent_state(self, client: OnlineSim) -> None:
        for rent in client.rent.state():
            assert isinstance(rent["sum"], (int, float))
            assert isinstance(rent["messages"], list)
            assert isinstance(rent["extend"], dict)

    def test_payment_history(self, client: OnlineSim) -> None:
        history = client.user.payment_history()
        assert isinstance(history["orders"]["data"], list)
        assert isinstance(history["paylist"], dict)

    def test_webhook_logs(self, client: OnlineSim) -> None:
        assert isinstance(client.user.webhook_logs()["data"], list)

    def test_free_list(self, client: OnlineSim) -> None:
        free = client.free.list()
        assert isinstance(free["countries"], list)
        assert isinstance(free["numbers"], dict)

    def test_wrong_key(self) -> None:
        bad = OnlineSim("wrong-key", base_url=BASE, transport=insecure_transport)
        with pytest.raises(ApiError) as info:
            bad.user.balance()
        assert info.value.code == "ERROR_WRONG_KEY"


@lifecycle
class TestLifecycle:
    COUNTRY = 44
    SERVICE = "google"

    def inject_sms(self, tzid: int, text: str) -> None:
        """Inject an SMS through the test driver callback (local backends only, no auth)."""
        body = json.dumps({"id": tzid, "phoneFrom": "VK", "text": text}).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        res = insecure_transport(HttpRequest("POST", urljoin(BASE, "sms_in_getaways/test"), headers, body, 30.0))
        assert res.status == 200

    def test_number_lifecycle(self, client: OnlineSim) -> None:
        assert isinstance(client.numbers.price(self.SERVICE, self.COUNTRY), (int, float))

        tzid = client.numbers.get(self.SERVICE, self.COUNTRY)
        assert isinstance(tzid, int)
        order = client.numbers.get_with_number(self.SERVICE, self.COUNTRY)
        assert re.fullmatch(r"\+?44\d+", order["number"])
        assert order["country"] == self.COUNTRY

        ids = {op["tzid"] for op in client.numbers.state()}
        assert {tzid, order["tzid"]} <= ids
        assert client.numbers.state_one(tzid)["response"].startswith("TZ_")

        # The test driver answers NO_NUMBER to any reject list: proves `reject` is sent.
        with pytest.raises(NoNumberError):
            client.numbers.get(self.SERVICE, self.COUNTRY, reject=["4470"])

        # No SMS yet: the guard interval keeps it open.
        with pytest.raises(ApiError) as info:
            client.numbers.close(order["tzid"])
        assert info.value.code == "NO_COMPLETE_TZID"

        self.inject_sms(tzid, "VK: 195895 is your code")
        assert client.numbers.wait_code(tzid, interval=1, timeout=30) == "195895"

    def test_webhook_url(self, client: OnlineSim) -> None:
        assert client.user.set_webhook_url("https://example.com/hook") is True
        assert client.user.profile().get("webhook_url") == "https://example.com/hook"
        with pytest.raises(ApiError) as info:
            client.user.set_webhook_url("not a url")
        assert info.value.code == "VALIDATION_ERROR"
        assert client.user.clear_webhook_url() is True
        assert client.user.profile().get("webhook_url") is None

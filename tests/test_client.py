from __future__ import annotations

import socket
import urllib.error

import pytest

from onlinesimru import ApiError, HttpRequest, HttpResponse, NoNumberError, OnlineSim, TransportError, __version__

from .helpers import Reply, fake_client, ok


class TestOptionsAndEncoding:
    def test_bearer_header_never_query_plus_lang(self) -> None:
        client, fake = fake_client(ok(price=0.36))
        client.numbers.price("vkcom", 44)
        call = fake.last()
        assert call.headers["Authorization"] == "Bearer test-key"
        assert call.headers["Accept"] == "application/json"
        assert call.headers["User-Agent"] == f"onlinesimru/{__version__} (python)"
        assert "apikey" not in call.params
        assert call.params["lang"] == "en"
        assert "dev_id" not in call.params

    def test_lang_dev_id_and_base_url_without_trailing_slash(self) -> None:
        client, fake = fake_client(ok(price=1), base_url="https://api.test/api", lang="ru", dev_id=42)
        client.numbers.price("vkcom")
        call = fake.last()
        assert call.url.split("?")[0] == "https://api.test/api/getPrice.php"
        assert call.params["lang"] == "ru"
        assert call.params["dev_id"] == "42"

    def test_no_authorization_without_key(self) -> None:
        client, fake = fake_client(ok(price=1), api_key=None)
        client.numbers.price("vkcom")
        assert "Authorization" not in fake.last().headers

    def test_default_base_url(self) -> None:
        seen: list[HttpRequest] = []

        def transport(request: HttpRequest) -> HttpResponse:
            seen.append(request)
            return HttpResponse(200, b'{"response":"1","price":1}')

        OnlineSim("k", transport=transport).numbers.price("vkcom")
        assert seen[0].url.startswith("https://onlinesim.host/api/getPrice.php?")
        assert seen[0].timeout == 30.0
        assert seen[0].method == "GET"
        assert seen[0].body is None

    def test_rejects_non_http_base_url(self) -> None:
        with pytest.raises(ValueError, match="http"):
            OnlineSim("k", base_url="file:///etc/")


class TestResponseHandling:
    def test_no_number(self) -> None:
        client, _ = fake_client(Reply({"response": "NO_NUMBER"}))
        with pytest.raises(NoNumberError) as info:
            client.numbers.get("google", 44)
        assert isinstance(info.value, ApiError)
        assert info.value.code == "NO_NUMBER"
        assert info.value.message == "No numbers available for this service right now"
        assert str(info.value) == info.value.message

    def test_no_number_for_forward(self) -> None:
        client, _ = fake_client(Reply({"response": "NO_NUMBER_FOR_FORWARD"}))
        with pytest.raises(NoNumberError):
            client.numbers.get("google")

    def test_http_456_wrong_key_is_api_error(self) -> None:
        client, _ = fake_client(Reply({"response": "ERROR_WRONG_KEY"}, status=456))
        with pytest.raises(ApiError) as info:
            client.user.balance()
        assert not isinstance(info.value, TransportError)
        assert (info.value.code, info.value.message) == ("ERROR_WRONG_KEY", "Wrong API key")

    def test_server_message_unless_it_echoes_the_code(self) -> None:
        client, _ = fake_client(
            Reply({"response": "TRY_AGAIN_LATER", "message": "Maintenance until 12:00"}),
            Reply({"response": "UNDEFINED_COUNTRY", "message": "UNDEFINED_COUNTRY"}),
            Reply({"response": "SOMETHING_NEW"}),
        )
        expected = [
            ("TRY_AGAIN_LATER", "Maintenance until 12:00"),
            ("UNDEFINED_COUNTRY", "Unknown country"),
            ("SOMETHING_NEW", "SOMETHING_NEW"),
        ]
        for code, message in expected:
            with pytest.raises(ApiError) as info:
                client.numbers.get("x")
            assert (info.value.code, info.value.message) == (code, message)

    def test_validation_object(self) -> None:
        body = {
            "response": {"webhook_url": ["The webhook url must be a valid URL.", "Too long."], "name": ["Required."]}
        }
        client, _ = fake_client(Reply(body))
        with pytest.raises(ApiError) as info:
            client.user.set_webhook_url("nope")
        assert info.value.code == "VALIDATION_ERROR"
        assert info.value.message == "The webhook url must be a valid URL.; Too long.; Required."

    def test_non_json_body(self) -> None:
        client, _ = fake_client(Reply(status=502, raw="<html>Bad gateway</html>"))
        with pytest.raises(TransportError) as info:
            client.user.balance()
        assert (info.value.status, info.value.body) == (502, "<html>Bad gateway</html>")

    def test_body_excerpt_is_cut_to_500_chars(self) -> None:
        client, _ = fake_client(Reply(status=200, raw="x" * 1000))
        with pytest.raises(TransportError) as info:
            client.user.balance()
        assert info.value.body == "x" * 500

    def test_json_error_status_without_response(self) -> None:
        client, _ = fake_client(Reply({"error": "boom"}, status=500))
        with pytest.raises(TransportError) as info:
            client.user.balance()
        assert info.value.status == 500

    def test_network_failure(self) -> None:
        client, _ = fake_client(ConnectionResetError("reset by peer"))
        with pytest.raises(TransportError) as info:
            client.user.balance()
        assert info.value.status is None
        assert str(info.value) == "Network error: reset by peer"

    @pytest.mark.parametrize(
        "error", [socket.timeout("timed out"), TimeoutError(), urllib.error.URLError(socket.timeout("timed out"))]
    )
    def test_request_timeout_is_transport_error(self, error: BaseException) -> None:
        client, _ = fake_client(error, timeout=12.5)
        with pytest.raises(TransportError) as info:
            client.user.balance()
        assert info.value.status is None
        assert str(info.value) == "Request timed out after 12.5 s"

    def test_transport_receives_the_timeout(self) -> None:
        client, fake = fake_client(ok(balance="1", zbalance=0), timeout=7)
        client.user.balance()
        assert fake.last().request.timeout == 7

    def test_programming_errors_are_not_masked(self) -> None:
        client, _ = fake_client(KeyError("bug"))
        with pytest.raises(KeyError):
            client.user.balance()

    def test_bodies_without_response_returned_as_is(self) -> None:
        client, _ = fake_client(Reply([]))
        assert client.numbers.state() == []

    def test_success_strips_response(self) -> None:
        client, _ = fake_client(Reply({"response": 1, "tzid": 5}))
        assert client.numbers.get("x") == 5

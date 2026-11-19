"""Fake transport for the offline tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlsplit

from onlinesimru import HttpRequest, HttpResponse, OnlineSim

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text("utf-8"))


@dataclass
class Reply:
    """A canned answer: a JSON value, or ``raw`` for a non-JSON body."""

    json: Any = None
    status: int = 200
    raw: Optional[str] = None


@dataclass
class Call:
    request: HttpRequest

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def path(self) -> str:
        return urlsplit(self.request.url).path

    @property
    def params(self) -> Dict[str, str]:
        """Every query parameter (each sent once)."""
        return dict(parse_qsl(urlsplit(self.request.url).query))

    @property
    def query(self) -> Dict[str, str]:
        """Query without the ``lang`` every request carries."""
        return {k: v for k, v in self.params.items() if k != "lang"}

    @property
    def headers(self) -> Dict[str, str]:
        return dict(self.request.headers)

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def body(self) -> Any:
        return None if self.request.body is None else json.loads(self.request.body)


@dataclass
class Fake:
    """Answers ``replies`` in order and records every call."""

    replies: List[Union[Reply, BaseException]]
    calls: List[Call] = field(default_factory=list)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.calls.append(Call(request))
        if not self.replies:
            raise AssertionError(f"unexpected request {request.url}")
        reply = self.replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        body = reply.raw if reply.raw is not None else json.dumps(reply.json)
        return HttpResponse(reply.status, body.encode())

    def last(self) -> Call:
        """The only call made; fails when there were more or none."""
        assert len(self.calls) == 1, f"expected 1 request, got {len(self.calls)}"
        return self.calls[0]


def fake_client(*replies: Union[Reply, BaseException], **options: Any) -> Tuple[OnlineSim, Fake]:
    fake = Fake(list(replies))
    kwargs: Dict[str, Any] = {"base_url": "https://api.test/api/", **options}
    kwargs.setdefault("api_key", "test-key")
    return OnlineSim(transport=fake, **kwargs), fake


def ok(**fields: Any) -> Reply:
    """Success body ``{"response": "1", **fields}``."""
    return Reply({"response": "1", **fields})

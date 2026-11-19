from __future__ import annotations

import builtins
from typing import Any, Dict, List, Union

import pytest

from onlinesimru import ApiError, Operation, TimeoutError, TransportError, wait_code

from .helpers import Reply, fake_client

Step = Union[Dict[str, Any], BaseException]


class FakeNumbers:
    """Fake numbers section on a fake clock: ``sleep`` only moves ``now``, nothing really waits."""

    def __init__(self, steps: List[Step]) -> None:
        self.steps = list(steps)
        self.log: List[str] = []
        self.now = 0.0

    def state_one(self, tzid: int, *, message_to_code: bool = True, msg_list: bool = False) -> Operation:
        self.log.append(f"state {tzid} code={message_to_code}")
        step = self.steps.pop(0) if self.steps else {}
        if isinstance(step, BaseException):
            raise step
        op: Operation = {"tzid": tzid, "response": "TZ_NUM_WAIT"}
        op.update(step)  # type: ignore[typeddict-item]
        return op

    def close(self, tzid: int) -> bool:
        self.log.append(f"close {tzid}")
        return True

    def next(self, tzid: int) -> bool:
        self.log.append(f"next {tzid}")
        return True

    def sleep(self, seconds: float) -> None:
        self.log.append(f"sleep {seconds:g}")
        self.now += seconds

    def clock(self) -> float:
        return self.now

    def wait(self, tzid: int = 7, **options: Any) -> str:
        return wait_code(self, tzid, sleep=self.sleep, clock=self.clock, **options)


def test_returns_code_and_closes() -> None:
    t = FakeNumbers([{}, {}, {"response": "TZ_NUM_ANSWER", "msg": "195895"}])
    assert t.wait() == "195895"
    assert t.log == [
        "state 7 code=True",
        "sleep 5",
        "state 7 code=True",
        "sleep 5",
        "state 7 code=True",
        "close 7",
    ]


def test_keep_open_since_full_message() -> None:
    t = FakeNumbers([{"msg": "old"}, {"msg": "Your code is 2991"}])
    assert t.wait(keep_open=True, since="old", full_message=True, interval=1) == "Your code is 2991"
    assert t.log == ["state 7 code=False", "sleep 1", "state 7 code=False", "next 7"]


@pytest.mark.parametrize("status", ["TZ_OVER_OK", "ERROR_NO_ITEMS"])
def test_finished_operation_raises_at_once(status: str) -> None:
    t = FakeNumbers([{"response": status}])
    with pytest.raises(ApiError) as info:
        t.wait()
    assert info.value.code == status
    assert t.log == ["state 7 code=True"]


def test_finished_operation_with_new_code_returns_it() -> None:
    t = FakeNumbers([{"response": "TZ_OVER_OK", "msg": "1234"}])
    assert t.wait() == "1234"


def test_timeout_last_sleep_cut_to_deadline() -> None:
    t = FakeNumbers([])
    with pytest.raises(TimeoutError):
        t.wait(interval=4, timeout=10)
    assert [entry for entry in t.log if entry.startswith("sleep")] == ["sleep 4", "sleep 4", "sleep 2"]
    assert len([entry for entry in t.log if entry.startswith("state")]) == 4
    assert t.now == 10


def test_timeout_error_is_also_builtin_timeout() -> None:
    t = FakeNumbers([])
    with pytest.raises(builtins.TimeoutError):
        t.wait(timeout=0)


def test_retries_transient_transport_error() -> None:
    t = FakeNumbers([TransportError("Network error: reset"), {"msg": "42"}])
    assert t.wait() == "42"
    assert t.log == ["state 7 code=True", "sleep 5", "state 7 code=True", "close 7"]


def test_api_error_raised_at_once() -> None:
    t = FakeNumbers([ApiError("ERROR_NO_OPERATIONS")])
    with pytest.raises(ApiError) as info:
        t.wait()
    assert info.value.code == "ERROR_NO_OPERATIONS"
    assert t.log == ["state 7 code=True"]


def test_exposed_as_client_numbers_wait_code() -> None:
    client, fake = fake_client(
        Reply([{"tzid": 9, "response": "TZ_NUM_ANSWER", "msg": "555"}]), Reply({"response": 1, "tzid": 9})
    )
    assert client.numbers.wait_code(9, sleep=lambda _: None) == "555"
    assert [c.path for c in fake.calls] == ["/api/getState.php", "/api/setOperationOk.php"]

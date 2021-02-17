from typing import List
from onlinesimru.api import Api


class GetForward(Api):
    def get(
        self,
        forward_numbers: List[int] = None,
        service: str = "unlimited_sms",
        region: int = None,
        reject: List[int] = None,
    ):
        return self._get(
            f"/getForward",
            {
                "forward_numbers": forward_numbers,
                "service": service,
                "region": region,
                "reject": reject,
            },
        )["tzid"]

    def state(
        self,
        message_to_code: int = 1,
        orderby: str = "ASC",
        msg_list: bool = True,
        clean: bool = True,
    ):
        return self._get(
            f"/getState",
            {
                "message_to_code": message_to_code,
                "orderby": orderby,
                "msg_list": msg_list,
                "clean": clean,
                "type": "forward",
            },
        )

    def stateOne(
        self,
        tzid: int,
        message_to_code: int = 1,
        orderby: str = "ASC",
        msg_list: bool = True,
        clean: bool = True,
    ):
        return self._get(
            f"/getState",
            {
                "tzid": tzid,
                "message_to_code": message_to_code,
                "orderby": orderby,
                "msg_list": msg_list,
                "clean": clean,
                "type": "forward",
            },
        )

    def close(self, tzid: int):
        return self._get(f"/setOperationOk", {"tzid": tzid})

    def repeat(self, service: int, number: int):
        return self._get(f"/getNumRepeat", {"service": service, "number": number})[
            "tzid"
        ]

    def tariffs(self):
        return self._get(f"/getNumbersStats", {"country": "all"})

    def tariffsOne(self, country: int = 7):
        return self._get(f"/getNumbersStats", {"country": country})

    def service(self):
        return self._get(f"/getService", {})["service"]

    def serviceNumber(self, service: str):
        return self._get(f"/getServiceNumber", {"service": service})["number"]

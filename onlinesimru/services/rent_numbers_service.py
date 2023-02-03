import time
from typing import List, Callable, Optional

from onlinesimru.api import API
from onlinesimru.exceptions import TimeoutException, NoNumberException
from onlinesimru.types.rent_numbers_types import RentNumber, Tariff, Message


class RentNumbersService(API):
    def wait_code(self, tzid: int, timeout: int = 10, max_tries: int = 10, callback: Optional[Callable] = None) -> str:
        last_message = self.get_last_message(tzid=tzid)

        last_code: str = last_message.code if last_message else ''

        counter = 0
        while True:
            time.sleep(timeout)
            counter += 1

            if counter >= max_tries:
                raise TimeoutException("Timeout error")

            last_message = self.get_last_message(tzid=tzid)

            if last_message and last_message.code != last_code:
                last_code = last_message.code
                break

        if callback:
            callback(last_code)

        return last_code

    def rent_new_number(self, country: int = 7, days: int = 1, extension: bool = False):
        return self._get(
            f"/rent/getRentNum",
            {"country": country, "days": days, "extension": extension},
        )["item"]

    def get_numbers(self) -> List[RentNumber]:
        return [
            RentNumber(**number_data) for number_data in self._get(f"/rent/getRentState", {"pagination": False})["list"]
        ]

    def get_last_message(self, tzid: int) -> Optional[Message]:
        messages = self.get_messages(tzid=tzid)

        if messages:
            return messages[0]

        return None

    def get_messages(self, tzid: int) -> List[Message]:
        number_data = self.get_number(tzid)
        return number_data.messages

    def get_number(self, tzid: int) -> RentNumber:
        try:
            return RentNumber(**self._get(f"/rent/getRentState", {"tzid": tzid, "pagination": False})["list"][0])
        except IndexError:
            raise NoNumberException('you do not have a number with the specified tzid')

    def extend_number_rental(self, tzid: int, days: int = 1) -> RentNumber:
        return RentNumber(**self._get(f"/rent/extendRentState", {"tzid": tzid, "days": days})["item"])

    def port_reload(self, tzid: int):
        return self._get(f"/rent/portReload", {"tzid": tzid})

    def get_tariffs(self) -> List[Tariff]:
        return [Tariff(**tariff_data) for _, tariff_data in self._get(f"/rent/tariffsRent", {}).items()]

    def get_tariff(self, country: int = 7) -> Tariff:
        return Tariff(**self._get(f"/rent/tariffsRent", {"country": country}))

    def revoke_number(self, tzid: int):
        return self._get(f"/rent/closeRentNum", {"tzid": tzid})

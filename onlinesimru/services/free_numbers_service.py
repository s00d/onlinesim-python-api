from onlinesimru.api import API


class FreeNumbersService(API):
    def get_countries(self):
        return self._get(f"/getFreeCountryList")["countries"]

    def get_numbers(self, country: int = 7):
        return self._get(f"/getFreePhoneList", {"country": country})["numbers"]

    def get_messages(self, phone: int, page: int = 1):
        return self._get(f"/getFreeMessageList", {"phone": phone, "page": page})[
            "messages"
        ]["data"]

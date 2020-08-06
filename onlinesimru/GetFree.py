from onlinesimru.api import Api


class GetFree(Api):
    def countries(self):
        return self._get(f'/getFreeCountryList')['countries']

    def numbers(self, country: int = 7):
        return self._get(f'/getFreePhoneList', {'country': country})['numbers']

    def messages(self, phone: int, page: int = 1):
        return self._get(f'/getFreeMessageList', {'phone': phone, 'page': page})['messages']['data']

from onlinesimru.api import Api


class GetRent(Api):
    def get(self, country: int = 7, days: int = 1, extension: bool = False):
        return self._get(f'/rent/getRentNum', {'country': country, 'days': days, 'extension': extension})['item']

    def state(self):
        return self._get(f'/rent/getRentState', {'pagination': False})['list']

    def stateOne(self, tzid: int):
        return self._get(f'/rent/getRentState', {'tzid': tzid, 'pagination': False})['list'][0]

    def extend(self, tzid: int, days: int = 1):
        return self._get(f'/rent/extendRentState', {'tzid': tzid, 'days': days})['item']

    def portReload(self, tzid: int):
        return self._get(f'/rent/portReload', {'tzid': tzid})

    def tariffs(self):
        return self._get(f'/rent/tariffsRent', {})

    def tariffsOne(self, country: int = 7):
        return self._get(f'/rent/tariffsRent', {'country': country})

    def close(self, tzid: int):
        return self._get(f'/rent/closeRentNum', {'tzid': tzid})
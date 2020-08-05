from onlinesimru.api import Api


class GetRent(Api):
    async def get(self, country: int = 7, days: int = 1, extension: bool = False):
        return (await self._get(f'/rent/getRentNum', {'country': country, 'days': days, 'extension': extension}))['item']

    async def state(self, orderby: str = 'ASC'):
        return (await self._get(f'/rent/getRentState', {'pagination': False}))['list']

    async def stateOne(self, tzid: int):
        return (await self._get(f'/rent/getRentState', {'tzid': tzid, 'pagination': False}))['list'][0]

    async def extend(self, tzid: int, days: int = 1):
        return (await self._get(f'/rent/extendRentState', {'tzid': tzid, 'days': days}))['item']

    async def portReload(self, tzid: int):
        return await self._get(f'/rent/portReload', {'tzid': tzid})

    async def tariffs(self):
        return await self._get(f'/rent/tariffsRent', {})

    async def tariffsOne(self, country: int = 7):
        return await self._get(f'/rent/tariffsRent', {'country': country})

    async def close(self, tzid: int):
        return await self._get(f'/rent/closeRentNum', {'tzid': tzid})
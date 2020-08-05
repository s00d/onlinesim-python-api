from onlinesimru.api import Api


class GetFree(Api):
    async def countries(self):
        return await self._get(f'/getFreeCountryList')

    async def numbers(self, country: int = 7):
        return await self._get(f'/getFreePhoneList', {'country': country})

    async def messages(self, phone: int, page: int = 1):
        return await self._get(f'/getFreePhoneList', {'phone': phone, 'page': page})
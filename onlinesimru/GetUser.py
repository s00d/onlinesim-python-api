from onlinesimru.api import Api


class GetUser(Api):
    async def balance(self):
        return await self._get(f'/getBalance')

    async def profile(self):
        return await self._get(f'/getProfile', {'income': True})
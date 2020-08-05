from onlinesimru.api import Api


class GetProxy(Api):
    async def get(self, cl:str = 'days', type:str = 'private', connect:str = 'https', count: int = 1, operator:str = None, country: int = 7, city: str = 'any', port_count: int = 1, session: bool = True):
        return (await self._get(f'/proxy/getProxy', {'class': cl, 'type': type, 'connect': connect, 'count': count, 'operator': operator, 'country': country, 'city': city, 'port_count': port_count, 'session': session}))['item']

    async def state(self, orderby: str = 'ASC'):
        return (await self._get(f'/proxy/getState', {'orderby': orderby}))['list']

    async def stateOne(self, tzid: int):
        return (await self._get(f'/proxy/getState', {'tzid': tzid}))['list'][0]

    async def changeIp(self, tzid: int):
        return await self._get(f'/proxy/changeIp', {'tzid': tzid})

    async def changeType(self, tzid: int):
        return (await self._get(f'/proxy/changeType', {'tzid': tzid}))['connect_type']

    async def setComment(self, tzid: int, comment: str = ''):
        return await self._get(f'/proxy/setComment', {'tzid': tzid, 'comment': comment})

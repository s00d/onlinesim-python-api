from onlinesimru.api import Api


class GetForward(Api):
    async def get(self, forward_numbers=None, service: str = 'unlimited_sms', region: int = None, reject=None):
        if reject is None:
            reject = []
        if forward_numbers is None:
            forward_numbers = []
        return (await self._get(f'/getForward', {'forward_numbers': forward_numbers, 'service': service, 'region': region, 'reject': reject}))['tzid']

    async def state(self, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True):
        return await self._get(f'/getState', {'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': 'forward'})

    async def stateOne(self, tzid: int, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True):
        return await self._get(f'/getState', {'tzid': tzid, 'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': 'forward'})

    async def close(self, tzid: int, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True):
        return await self._get(f'/setOperationOk', {'tzid': tzid, 'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean})

    async def repeat(self, service: int, number: int):
        return (await self._get(f'/getNumRepeat', {'service': service, 'number': number}))['tzid']

    async def tariffs(self):
        return await self._get(f'/getNumbersStats', {'country': 'all'})

    async def tariffsOne(self, country: int = 7):
        return await self._get(f'/getNumbersStats', {'country': country})

    async def service(self):
        return (await self._get(f'/getService', {}))['service']

    async def serviceNumber(self, service: str):
        return (await self._get(f'/getServiceNumber', {'service': service}))['number']

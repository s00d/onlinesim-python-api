from onlinesimru.api import Api
import time

class GetNumbers(Api):
    async def price(self, service: str):
        return (await self._get(f'/getPrice', {'service': service}))['price']

    async def get(self, service: str, country: int = 7, reject=None, extension: bool = False):
        if reject is None:
            reject = []
        return (await self._get(f'/getNum', {'service': service, 'country': country, 'reject': reject, 'extension': extension}))['tzid']

    async def state(self, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True, repeat: bool = False):
        type = 'index'
        if repeat:
            type = 'repeat'
        return (await self._get(f'/getState', {'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': type}))

    async def stateOne(self, tzid: int, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True, repeat: bool = False):
        type = 'index'
        if repeat:
            type = 'repeat'
        return (await self._get(f'/getState', {'tzid': tzid, 'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': type}))[0]

    async def next(self, tzid: int):
        return await self._get(f'/setOperationRevise', {'tzid': tzid})

    async def close(self, tzid: int):
        return await self._get(f'/setOperationOk', {'tzid': tzid})

    async def tariffs(self):
        return await self._get(f'/getNumbersStats', {'country': 'all'})

    async def tariffsOne(self, country: int = 7):
        return await self._get(f'/getNumbersStats', {'country': country})

    async def service(self):
        return (await self._get(f'getService', {}))['service']

    async def serviceNumber(self, service: str):
        return (await self._get(f'/getServiceNumber', {'service': service}))['number']

    async def wait_code(self, tzid: int, timeout=10, callback=None, not_end=False):
        __last_code: str = ''
        counter = 0
        while True:
            time.sleep(timeout)
            counter += 1
            if counter >= 10:
                raise ('Timeout error')
            response = await self.stateOne(tzid)
            if response['code'] and not not_end and response['code'] != __last_code:
                __last_code = response['code']
                await self.close(tzid)
                break
            elif response['code'] and not_end and response['code'] != __last_code:
                __last_code = response['code']
                await self.next(tzid)
                break
        if callback:
            callback(__last_code)

        return __last_code

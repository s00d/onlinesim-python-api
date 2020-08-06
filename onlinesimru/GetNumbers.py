from typing import List
from onlinesimru.api import Api
import time

class GetNumbers(Api):
    def price(self, service: str):
        return self._get(f'/getPrice', {'service': service})['price']

    def get(self, service: str, country: int = 7, reject: List[int] = None, extension: bool = False):
        return self._get(f'/getNum', {'service': service, 'country': country, 'reject': reject, 'extension': extension})['tzid']

    def state(self, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True, repeat: bool = False):
        type = 'index'
        if repeat:
            type = 'repeat'
        return self._get(f'/getState', {'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': type})

    def stateOne(self, tzid: int, message_to_code: int = 1, orderby: str = 'ASC', msg_list: bool = True, clean: bool = True, repeat: bool = False):
        type = 'index'
        if repeat:
            type = 'repeat'
        return self._get(f'/getState', {'tzid': tzid, 'message_to_code': message_to_code, 'orderby': orderby, 'msg_list': msg_list, 'clean': clean, 'type': type})[0]

    def next(self, tzid: int):
        return self._get(f'/setOperationRevise', {'tzid': tzid})

    def close(self, tzid: int):
        return self._get(f'/setOperationOk', {'tzid': tzid})

    def tariffs(self):
        return self._get(f'/getNumbersStats', {'country': 'all'})

    def tariffsOne(self, country: int = 7):
        return self._get(f'/getNumbersStats', {'country': country})

    def service(self):
        return self._get(f'getService', {})['service']

    def serviceNumber(self, service: str):
        return self._get(f'/getServiceNumber', {'service': service})['number']

    def wait_code(self, tzid: int, timeout=10, callback=None, not_end=False):
        __last_code: str = ''
        counter = 0
        while True:
            time.sleep(timeout)
            counter += 1
            if counter >= 10:
                raise ('Timeout error')
            response = self.stateOne(tzid)
            if response['code'] and not not_end and response['code'] != __last_code:
                __last_code = response['code']
                self.close(tzid)
                break
            elif response['code'] and not_end and response['code'] != __last_code:
                __last_code = response['code']
                self.next(tzid)
                break
        if callback:
            callback(__last_code)

        return __last_code

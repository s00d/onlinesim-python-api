from typing import List

from onlinesimru.Extentions import TimeoutException
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

    def stateOne(self, tzid: int, message_to_code: int = 1, msg_list: bool = True, clean: bool = True, repeat: bool = False):
        type = 'index'
        if repeat:
            type = 'repeat'
        return self._get(f'/getState', {'tzid': tzid, 'message_to_code': message_to_code, 'msg_list': msg_list, 'clean': clean, 'type': type})[0]

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

    def wait_code(self, tzid: int, timeout=10, callback=None, not_end=False, full_message=False):
        __last_code: str = ''
        _response_type: int = 1
        if full_message:
            _response_type = 0
        counter = 0
        while True:
            time.sleep(timeout)
            counter += 1
            if counter >= 10:
                raise TimeoutException('Timeout error')
            response = self.stateOne(tzid, _response_type, False)
            if 'msg' in response and not not_end and response['msg'] != __last_code:
                __last_code = response['msg']
                self.close(tzid)
                break
            elif 'msg' in response and not_end and response['msg'] != __last_code:
                __last_code = response['msg']
                self.next(tzid)
                break
        if callback:
            callback(__last_code)

        return __last_code

import aiohttp
import asyncio
import aiofiles
import logging
import json

from onlinesimru.Extentions import NoNumberException, Error, RequestException


def create_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                        level=logging.INFO)
    return logging.getLogger(__name__)


logger = create_logger()


class Api:
    __slots__ = ('apikey', 'lang', 'dev_id', 'headers', '_semaphore')

    def __init__(self, apikey: str = '', lang: str = 'en', dev_id: str = None):
        self.apikey = apikey
        self.dev_id = dev_id
        self.lang = lang
        self.headers = {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/84.0.4147.89 Safari/537.36'}
        self._semaphore = asyncio.Semaphore(3)

    async def _get(self, endpoint: str, params: dict = None):
        if params is None:
            params = {}
        params['apikey'] = self.apikey
        params['lang'] = self.lang
        params['dev_id'] = self.dev_id
        payload = {k: v for k, v in params.items() if v is not None}
        async with aiohttp.ClientSession() as session:
            url = f'https://onlinesim.ru/api/' + endpoint + '.php'

            logger.info(f'[GET]: url={url} | data={payload}')
            async with session.get(url, headers=self.headers, params=payload) as response:
                response.raise_for_status()

                data = await response.json()
                if "response" in data:
                    if data.get('response') != '1':
                        raise RequestException(data.get('response'))
                return data

    # async def _post(self, endpoint: str, params: dict = None, path: str = None):
    #     files = None
    #
    #     if path:
    #         async with aiofiles.open(path, 'rb') as content:
    #             files = await content.read()
    #         files = {'file': files}
    #
    #     if params is None:
    #         params = {}
    #     params['apikey'] = self.apikey
    #     params['lang'] = self.lang
    #     params['dev_id'] = self.dev_id
    #     payload = {k: v for k, v in params.items() if v is not None}
    #
    #     if 'attachments' in payload:
    #         payload['attachments'] = json.dumps(payload['attachments'])
    #
    #     async with self._semaphore:
    #         async with aiohttp.ClientSession() as session:
    #             url = f'https://onlinesim.ru/api/' + endpoint + '.php'
    #             data = payload if not path else files
    #
    #             logger.info(f'[POST]: url={url} | data={payload} | files={files}')
    #             async with session.post(url, headers=self.headers, data=data) as response:
    #                 response.raise_for_status()
    #
    #                 return await response.json()

    async def getPrice(self, service: str):
        return await self._get(f'/getPrice', {'service': service})

import logging
import httpx

from onlinesimru.Extentions import NoNumberException, Error, RequestException


logger = logging.getLogger(__name__)


class Api:
    __slots__ = ("apikey", "lang", "dev_id", "headers")

    def __init__(self, apikey: str = "", lang: str = "en", dev_id: str = None):
        self.apikey = apikey
        self.dev_id = dev_id
        self.lang = lang
        self.headers = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 Safari/537.36"
        }

    def _get(self, endpoint: str, params: dict = None):
        if params is None:
            params = {}
        params["apikey"] = self.apikey
        params["lang"] = self.lang
        params["dev_id"] = self.dev_id
        payload = {k: v for k, v in params.items() if v is not None}
        response = httpx.get(
            f"https://onlinesim.ru/api/" + endpoint + ".php",
            headers=self.headers,
            params=payload,
        )
        data = response.json()
        if "response" in data:
            if str(data.get("response")) != "1":
                raise RequestException(data.get("response"))
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
        return await self._get(f"/getPrice", {"service": service})

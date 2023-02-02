import logging
from typing import Any, Dict, Optional

import httpx

from onlinesimru.exceptions import RequestException


logger = logging.getLogger(__name__)


class API:
    __slots__ = ("apikey", "lang", "dev_id", "headers")

    def __init__(self, apikey: str = "", lang: str = "en", dev_id: str = None):
        self.apikey = apikey
        self.dev_id = dev_id
        self.lang = lang
        self.headers = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 Safari/537.36"
        }

    def __get_payload(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        if self.apikey != "":
            params["apikey"] = self.apikey
        params["lang"] = self.lang
        params["dev_id"] = self.dev_id
        return {k: v for k, v in params.items() if v is not None}

    def _get(self, endpoint: str, params: dict = None):
        payload = self.__get_payload(params=params)

        response = httpx.get(
            f"https://onlinesim.ru/api" + endpoint + ".php",
            headers=self.headers,
            params=payload,
        )
        data = response.json()

        if "response" in data:
            if str(data.get("response")) != "1":
                raise RequestException(data.get("response"))

        return data

    def _post(self, endpoint: str, params: dict = None):
        payload = self.__get_payload(params=params)

        response = httpx.post(
            f"https://onlinesim.ru/api" + endpoint + ".php",
            headers=self.headers,
            json=payload,
        )
        data = response.json()

        if "response" in data:
            if str(data.get("response")) != "1":
                raise RequestException(data.get("response"))

        return data

    async def get_price(self, service: str):
        return await self._get(f"/getPrice", {"service": service})

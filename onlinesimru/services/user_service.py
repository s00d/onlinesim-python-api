from dataclasses import dataclass
from onlinesimru.api import API
from typing import List, Optional, Union


@dataclass
class Payment:
    payment: float
    income: float
    spent: float
    now: float


@dataclass
class User:
    id: int
    name: str
    username: str
    email: Optional[str]
    apikey: Optional[str]
    api_access: Optional[Union[str, bool]]
    locale: str
    number_region: Optional[Union[str, int]]
    number_country: Optional[Union[str, int]]
    number_reject: Optional[List[Union[str, int]]]
    ugroup: int
    verify: int
    block: int
    payment: Payment


@dataclass
class Balance:
    balance: float
    zbalance: float
    income: float


class UserService(API):
    def balance(self):
        # return from_dict(data_class=Balance, data=self._get(f'/getBalance', {'income': True}))
        return self._get(f"/getBalance", {"income": True})

    def profile(self):
        return self._get(f"/getProfile")["profile"]

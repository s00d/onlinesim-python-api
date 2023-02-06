from typing import List, Any, Dict, Optional

from pydantic import BaseModel


class Message(BaseModel):
    id: int
    service: str
    text: str
    code: str
    created_at: str


class RentNumber(BaseModel):
    status: int
    extension: int
    messages: List[Message]
    sum: str
    country: int
    checked_time: str
    number: str
    rent: int
    tzid: int
    time: int
    days: int
    hours: int
    extend: Dict[Any, Any]
    checked: bool
    reload: int
    day_extend: int
    m_ext: bool
    freeze: bool


class Tariff(BaseModel):
    code: int
    enabled: bool
    name: str
    new: bool
    position: int
    count: Dict[int, int]
    days: Dict[int, int]
    extend: int
    confirm: Optional[bool]

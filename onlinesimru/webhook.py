from __future__ import annotations

import json
from typing import Any, Mapping, Optional, Union

from ._normalize import integer
from .errors import OnlineSimError
from .models import WebhookPayload


def parse_webhook(payload: Union[str, bytes, Mapping[str, Any]]) -> WebhookPayload:
    """Parse an inbound webhook body (``receiving_sms`` or ``rent_sms``) from JSON text or an already parsed dict.

    Lenient: numeric fields may arrive as strings, missing or malformed fields become ``None``, unknown fields are
    dropped. Raises ``OnlineSimError`` only when the input is not a JSON object at all.
    """
    data: Any = payload
    if isinstance(payload, (str, bytes)):
        try:
            data = json.loads(payload)
        except ValueError:
            raise OnlineSimError("Webhook payload is not valid JSON") from None
    if not isinstance(data, Mapping):
        raise OnlineSimError("Webhook payload is not a JSON object")
    kind = data.get("webhook_type")
    return {
        "webhook_type": kind if kind in ("receiving_sms", "rent_sms") else None,
        "operation_id": integer(data.get("operation_id")),
        "user_id": integer(data.get("user_id")),
        "country_code": integer(data.get("country_code")),
        "number": _str(data.get("number")),
        "sender": _str(data.get("sender")),
        "message": _str(data.get("message")),
        "code": _str(data.get("code")),
        "time_start": _str(data.get("time_start")),
        "time_left": integer(data.get("time_left")),
    }


def _str(value: Any) -> Optional[str]:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None

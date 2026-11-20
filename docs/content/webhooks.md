---
title: Webhooks
description: Receive SMS as HTTP callbacks and parse them with parse_webhook.
navigation:
  order: 5
---

Set a URL with [`client.user.set_webhook_url`](/user#set_webhook_url). For each SMS the server POSTs a JSON body to it: `webhook_type` `receiving_sms` for numbers, `rent_sms` for rents. Delivery attempts are listed by [`client.user.webhook_logs`](/user#webhook_logs).

## parse_webhook

Parse an inbound webhook body from JSON text (`str` or `bytes`) or an already parsed dict.

```python
def parse_webhook(payload: str | bytes | Mapping[str, Any]) -> WebhookPayload
```

Lenient: numeric fields may arrive as strings, missing or malformed fields become `None`, unknown fields are dropped. It raises `OnlineSimError` only when the input is not a JSON object.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

from onlinesimru import parse_webhook


class Hook(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        hook = parse_webhook(body)
        if hook["webhook_type"] == "receiving_sms":
            print(hook["operation_id"], hook["code"])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


HTTPServer(("", 8080), Hook).serve_forever()
```

## Payload fields

| Field | Type | Description |
|---|---|---|
| `webhook_type` | `"receiving_sms" \| "rent_sms" \| None` | Kind of operation. |
| `operation_id` | `int \| None` | `tzid` of the operation or rent. |
| `user_id` | `int \| None` | Account id. |
| `country_code` | `int \| None` | Country code of the number. |
| `number` | `str \| None` | Numbers: `+` and the full number (`+79001234567`), or `hidden`. Rent: the full number in digits without `+` (`79001234567`). |
| `sender` | `str \| None` | Sender of the SMS, e.g. `VK`. |
| `message` | `str \| None` | Full SMS text. |
| `code` | `str \| None` | Code extracted from the SMS; `""` when none was found. |
| `time_start` | `str \| None` | Numbers: when the operation was ordered. Rent: when the SMS arrived. `YYYY-MM-DD HH:MM:SS`. |
| `time_left` | `int \| None` | Time left: seconds for numbers, minutes for rent. |

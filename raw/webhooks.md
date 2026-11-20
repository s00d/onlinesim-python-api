# Webhooks

> Receive SMS as HTTP callbacks and parse them with parse_webhook.

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

<table>
<thead>
  <tr>
    <th>
      Field
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      <code>
        webhook_type
      </code>
    </td>
    
    <td>
      <code>
        "receiving_sms" | "rent_sms" | None
      </code>
    </td>
    
    <td>
      Kind of operation.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        operation_id
      </code>
    </td>
    
    <td>
      <code>
        int | None
      </code>
    </td>
    
    <td>
      <code>
        tzid
      </code>
      
       of the operation or rent.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        user_id
      </code>
    </td>
    
    <td>
      <code>
        int | None
      </code>
    </td>
    
    <td>
      Account id.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        country_code
      </code>
    </td>
    
    <td>
      <code>
        int | None
      </code>
    </td>
    
    <td>
      Country code of the number.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        number
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      Numbers: <code>
        +
      </code>
      
       and the full number (<code>
        +79001234567
      </code>
      
      ), or <code>
        hidden
      </code>
      
      . Rent: the full number in digits without <code>
        +
      </code>
      
       (<code>
        79001234567
      </code>
      
      ).
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        sender
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      Sender of the SMS, e.g. <code>
        VK
      </code>
      
      .
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        message
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      Full SMS text.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        code
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      Code extracted from the SMS; <code>
        ""
      </code>
      
       when none was found.
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        time_start
      </code>
    </td>
    
    <td>
      <code>
        str | None
      </code>
    </td>
    
    <td>
      Numbers: when the operation was ordered. Rent: when the SMS arrived. <code>
        YYYY-MM-DD HH:MM:SS
      </code>
      
      .
    </td>
  </tr>
  
  <tr>
    <td>
      <code>
        time_left
      </code>
    </td>
    
    <td>
      <code>
        int | None
      </code>
    </td>
    
    <td>
      Time left: seconds for numbers, minutes for rent.
    </td>
  </tr>
</tbody>
</table>

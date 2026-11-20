---
title: User
description: Balance, profile, payments and the webhook URL — client.user.
navigation:
  order: 3
---

## balance

Balance in USD.

```python
def balance() -> Balance  # {"balance": float, "zbalance": float, "income"?: float}
```

`balance` includes the sum frozen by numbers and unconfirmed rents in progress (`zbalance`, which may be negative): available = `balance − max(zbalance, 0)`. `income` is the partner income. The server caches the answer for 60 s.

```python
b = client.user.balance()
available = b["balance"] - max(b["zbalance"], 0)
```

Errors: `ApiError` `ERROR_WRONG_KEY`, `ACCOUNT_BLOCKED`, `API_ACCESS_DISABLED`, `API_ACCESS_IP`.

## profile

The account profile.

```python
def profile() -> Profile
```

`Profile`: `{id, name, username, email, locale, currency, number_country, number_reject, webhook_url, api_access, …}`.

```python
profile = client.user.profile()
print(profile.get("email"), profile.get("webhook_url"))
```

## payment_history

Top-up orders (paginated, newest first) and the available payment methods.

```python
def payment_history(page: int = 1) -> PaymentHistory
```

`PaymentHistory`: `{orders, paylist, domains?, forms?, currency?, buttons?}` — `orders` is a paginator of `PaymentOrder`. `PaymentOrder["sum"]` stays a decimal string (`"89.00"`); `currency` and `form_text` may be `None`. `paylist` maps a group id to its payment methods, or is a list when the ids are 0, 1, 2… (the server sends a JSON array then).

```python
orders = client.user.payment_history()["orders"]
print(f"{orders['total']} orders, page {orders['current_page']}/{orders['last_page']}")
```

## set_webhook_url

Set the URL that receives SMS webhooks (see [Webhooks](/webhooks)).

```python
def set_webhook_url(url: str) -> bool
```

```python
client.user.set_webhook_url("https://example.com/onlinesim-hook")
```

Errors: `ApiError` `VALIDATION_ERROR` for an invalid URL; `message` holds the server's field messages.

## clear_webhook_url

Remove the webhook URL, also from operations in progress.

```python
def clear_webhook_url() -> bool
```

```python
client.user.clear_webhook_url()
```

## webhook_logs

Webhook delivery log, newest first, 10 per page.

```python
def webhook_logs(page: int = 1) -> WebhookLogs
```

`WebhookLogs` is a paginator of `WebhookLog`: `{id, user_id, webhook_url, type, params, status, error, created_at, updated_at}` — `type` is `receiving_sms` or `rent_sms`, `status` is `success`, `fail` or `pending`, `params` the payload that was sent.

```python
for log in client.user.webhook_logs()["data"]:
    print(log["created_at"], log["status"], log["error"])
```

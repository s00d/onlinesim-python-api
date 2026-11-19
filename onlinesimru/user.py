from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ._normalize import as_map, num
from .models import Balance, PaymentHistory, Profile, WebhookLogs

if TYPE_CHECKING:
    from .client import RequestFn


class UserApi:
    """Account: ``client.user``."""

    def __init__(self, request: RequestFn) -> None:
        self._request = request

    def balance(self) -> Balance:
        """Balance in USD. ``balance`` includes the frozen ``zbalance``: available = balance - zbalance."""
        res = self._request("getBalance.php", {"income": 1})
        out: Balance = {"balance": num(res.get("balance")) or 0, "zbalance": num(res.get("zbalance")) or 0}
        income = num(res.get("income"))
        if income is not None:
            out["income"] = income
        return out

    def profile(self) -> Profile:
        """Account profile."""
        return cast(Profile, self._request("getProfile.php")["profile"])

    def payment_history(self, page: int = 1) -> PaymentHistory:
        """Top-up orders (paginated, newest first) and the available payment methods."""
        res = self._request("getPaymentHistory.php", {"page": page})
        return cast(PaymentHistory, {**res, "paylist": as_map(res.get("paylist"))})

    def set_webhook_url(self, url: str) -> bool:
        """Set the URL that receives SMS webhooks. Raises ``ApiError("VALIDATION_ERROR")`` for an invalid URL."""
        self._request("profile.php", body={"profile": {"webhook_url": url}})
        return True

    def clear_webhook_url(self) -> bool:
        """Remove the webhook URL (also from operations in progress)."""
        self._request("profile.php", body={"profile": {"webhook_url": None}})
        return True

    def webhook_logs(self, page: int = 1) -> WebhookLogs:
        """Webhook delivery log, newest first, 10 per page."""
        return cast(WebhookLogs, self._request("webhook-logs", {"page": page})["data"])

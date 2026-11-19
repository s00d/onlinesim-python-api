# onlinesim-python-api

[![PyPI](https://img.shields.io/pypi/v/onlinesimru.svg)](https://pypi.org/project/onlinesimru/)
[![CI](https://github.com/s00d/onlinesim-python-api/actions/workflows/ci.yml/badge.svg)](https://github.com/s00d/onlinesim-python-api/actions/workflows/ci.yml)

Typed Python client for the [OnlineSim](https://onlinesim.io) API: SMS numbers, rent, account and free numbers.
Zero runtime dependencies (standard library `urllib`), Python 3.9+, type hints (`py.typed`).

```bash
pip install onlinesimru
```

```python
import os

from onlinesimru import OnlineSim

client = OnlineSim(os.environ["ONLINESIM_KEY"])

b = client.user.balance()
print(f"available: {b['balance'] - b['zbalance']} USD")

order = client.numbers.get_with_number("google", 44)
print(f"enter {order['number']} in the app")
print("code:", client.numbers.wait_code(order["tzid"]))
```

## Testing

`MockOnlineSim` is a built-in offline fake of the API: test your integration without network, key or money.
More in the [testing guide](https://s00d.github.io/onlinesim-python-api/testing).

```python
from onlinesimru import MockOnlineSim

mock = MockOnlineSim(balance=10)
client = mock.client()

tzid = client.numbers.get("google", 44)
mock.add_sms_after(tzid, "Your code: 123-456", 2)  # arrives on the third poll
assert client.numbers.wait_code(tzid, interval=0) == "123456"
assert mock.balance() == 9.8
```

Documentation: **https://s00d.github.io/onlinesim-python-api/** · Changes: [CHANGELOG.md](CHANGELOG.md) · License: Apache-2.0

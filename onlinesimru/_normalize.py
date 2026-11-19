"""Client-side normalisation of server quirks, shared by the sections and ``parse_webhook``."""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Union


def as_map(value: Any) -> Dict[str, Any]:
    """PHP sends an empty map as ``[]``: return ``{}`` for it (and for anything that is not a dict)."""
    return value if isinstance(value, dict) else {}


def num(value: Any) -> Union[int, float, None]:
    """Number from a number or a numeric string (``"1442.330"``); ``None`` when missing or not numeric."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value if math.isfinite(value) else None
    if isinstance(value, str) and value.strip():
        try:
            return int(value)
        except ValueError:
            pass
        try:
            n = float(value)
        except ValueError:
            return None
        return n if math.isfinite(n) else None
    return None


def integer(value: Any) -> Optional[int]:
    """Whole number from a number or a numeric string; ``None`` otherwise."""
    n = num(value)
    return int(n) if n is not None and n == int(n) else None

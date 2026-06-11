import time
from typing import Any

_ocr_cache: dict[int, dict[str, Any]] = {}
_temp_cache: dict[str, dict[str, Any]] = {}


def store_ocr(user_id: int, data: dict[str, Any]) -> None:
    data["_ts"] = time.time()
    _ocr_cache[user_id] = data


def get_ocr(user_id: int) -> dict[str, Any] | None:
    data = _ocr_cache.get(user_id)
    if data and time.time() - data.get("_ts", 0) < 300:
        return data
    _ocr_cache.pop(user_id, None)
    return None


def pop_ocr(user_id: int) -> dict[str, Any] | None:
    data = get_ocr(user_id)
    if data:
        _ocr_cache.pop(user_id, None)
    return data


def store_temp(key: str, data: dict[str, Any], ttl: int = 300) -> None:
    """Store arbitrary temporary data keyed by a string (e.g. UUID)."""
    data["_ts"] = time.time()
    data["_ttl"] = ttl
    _temp_cache[key] = data


def get_temp(key: str) -> dict[str, Any] | None:
    """Retrieve temp data. Returns None if expired or missing."""
    data = _temp_cache.get(key)
    if data and time.time() - data.get("_ts", 0) < data.get("_ttl", 300):
        return data
    _temp_cache.pop(key, None)
    return None


def pop_temp(key: str) -> dict[str, Any] | None:
    """Retrieve and remove temp data atomically."""
    data = get_temp(key)
    if data:
        _temp_cache.pop(key, None)
    return data

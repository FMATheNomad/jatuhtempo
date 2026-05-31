import time
from typing import Any

_ocr_cache: dict[int, dict[str, Any]] = {}


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

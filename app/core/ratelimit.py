import time
from collections import defaultdict

_last_cmd: dict[int, float] = defaultdict(float)


def check_rate_limit(user_id: int, cooldown: float = 1.0) -> bool:
    now = time.time()
    if now - _last_cmd[user_id] < cooldown:
        return False
    _last_cmd[user_id] = now
    return True

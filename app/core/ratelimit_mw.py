import os
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

_rates: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.environ.get("TESTING") == "true":
            return await call_next(request)
        if request.url.path.startswith("/api/"):
            key = request.client.host if request.client else "unknown"
            now = time.time()
            window = settings.api_rate_window_seconds
            rate = settings.api_rate_limit
            _rates[key] = [t for t in _rates[key] if now - t < window]
            if len(_rates[key]) >= rate:
                raise HTTPException(429, "Too many requests")
            _rates[key].append(now)
        return await call_next(request)

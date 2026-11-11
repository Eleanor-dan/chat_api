from __future__ import annotations
import asyncio
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int = 60):
        super().__init__(app)
        self.limit = limit_per_minute
        self._hits: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"

        now = time.monotonic()

        async with self._lock:
            hits = [ t for t in self._hits.get(client, []) if now - t < 60]
            if len(hits) > self.limit:
                return JSONResponse(
                    status_code=429,
                    content = {"detail": "rate limit exceeded, retry later"},
                )
            hits.append(now)
            self._hits[client] = hits

        return await call_next(request )
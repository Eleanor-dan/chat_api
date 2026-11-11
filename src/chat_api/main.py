from __future__ import annotations 
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import __version__
from .deps import get_settings
from .middleware import RequestContextMiddleware
from .ratelimit import RateLimitMiddleware
from .routes import health, chat
from .errors import LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

settings = get_settings()

app = FastAPI(
    title="Chat API",
    version=__version__,
    description="A small OpenAI-compatible chat service with SSE streaming.",
)

app.add_middleware(RateLimitMiddleware, limit_per_minute = settings.rate_limit_per_minute)
app.add_middleware(RequestContextMiddleware)

app.include_router(health.router)
app.include_router(chat.router)

@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "name": "chat-api",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/version", tags=["meta"])
async def version() -> str:
    return __version__

@app.exception_handler(LLMError)
async def handle_llm_error(request: Request, exc: LLMError) ->JSONResponse:
    return JSONResponse(
        status_code=502,
        content={
            "detail": str(exc),
            "request_id": getattr(request.state, "request_id", None),
        }
    )
from __future__ import annotations
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI
from .config import Settings
from .schemas import Usage
from .errors import LLMError

@dataclass
class Completion:
    content: str
    model: str
    usage: Usage | None = None

def _pick(value: Any, default: Any) -> Any:
    return default if value is None else value

class ChatService:
    def __init__(self, settings: Settings, client: Any | None = None ) -> Any:
        self.settings = settings
        self._client = client or AsyncOpenAI(
            api_key=settings.api_key or "not_set",
            base_url=settings.base_url,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )

    async def complete(
            self,
            messages: list[dict[str, str]],
            *,
            model: str | None = None,
            temperature: float | None = None,
            max_tokens: int | None = None,
    )-> Completion:
        try:
            response = await self._client.chat.completions.create(
                messages=messages,
                model=model or self.settings.model,
                temperature=_pick(temperature, self.settings.temperature),
                max_tokens=_pick(max_tokens,self.settings.max_tokens),
            ) 
        except Exception as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc

        if not getattr(response, "choices", None):
            raise LLMError("LLM returned no choices")

        raw_usage = getattr(response, "usage", None)
        usage = None
        if raw_usage is not None:
            usage = Usage(
                prompt_tokens=getattr(raw_usage, "prompt_tokens", None),
                completion_tokens=getattr(raw_usage, "completion_tokens", None),
                total_tokens=getattr(raw_usage, "total_tokens", 0),
            )
    
        return Completion(
            content = response.choices[0].message.content or "",
            model=getattr(response, "model", None) or self.settings.model,
            usage=usage,
        )
    async def stream(
            self,
            messages: list[dict[str, str]],
            *,
            model: str | None = None,
            temperature: float | None = None,
            max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        try:
            chunks = await self._client.chat.completions.create(
                messages=messages,
                model=model or self.settings.model,
                temperature=_pick(temperature, self.settings.temperature),
                max_tokens=_pick(max_tokens,self.settings.max_tokens),
                stream=True,
            )
            async for chunk in chunks:
                choices = getattr(chunk, "choices", None)
                if not choices:
                    continue
                delta = choices[0].delta
                text = getattr(delta, "content", None) if delta else None
                if text:
                    yield text
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"LLM stream failed: {exc}") from exc 
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..deps import get_service
from ..errors import LLMError
from ..llm import ChatService
from ..schemas import ChatRequest, ChatResponse
from ..sse import sse

router = APIRouter(prefix="/v1", tags=["chat"])

def _messages(payload: ChatRequest)-> list[dict[str,str]]:
    return [message.model_dump() for message in payload.messages]

@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    service: Annotated[ChatService, Depends(get_service)],
)-> ChatResponse:
    result = await service.complete(
        _messages(payload),
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return ChatResponse(content = result.content, model = result.model, usage = result.usage)

@router.post("/chat/stream")
async def chat_stream(
    payload: ChatRequest,
    service: Annotated[ChatService, Depends(get_service)],
) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        try:
            async for delta in service.stream(
                _messages(payload),
                model=payload.model,
                temperature=payload.temperature,
                max_tokens=payload.max_tokens,
            ):
                yield sse({"delta": delta})
        except LLMError as exc:
            yield sse({"err": str(exc)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # 关键：告诉 Nginx 不要缓冲，否则流式会“攒一批再发”。
            "X-Accel-Buffering": "no",
        }
    )
    
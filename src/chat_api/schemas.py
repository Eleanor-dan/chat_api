from __future__ import annotations
from typing import Literal
from pydantic import Field, BaseModel

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    model: str | None = None
    temperature: float | None = Field(default=None, ge = 0, le = 2)
    max_tokens: int | None = Field(default=None, ge = 1, le = 32768)

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Usage | None = None
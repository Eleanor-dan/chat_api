from __future__ import annotations

from functools import lru_cache
from .config import Settings
from .llm import ChatService

@lru_cache
def get_settings()->Settings:
    return Settings()

@lru_cache
def get_service()->ChatService:
    return ChatService(get_settings())
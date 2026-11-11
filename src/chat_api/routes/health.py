from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends
from ..config import Settings
from ..deps import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/ready")
async def ready(
    setting: Annotated[Settings, Depends(get_settings)]
) -> dict[str,str]:
    return {"status": "ready" if setting.api_key else "missing"}

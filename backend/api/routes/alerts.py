from __future__ import annotations

from fastapi import APIRouter

from api.state import get_full_state

router = APIRouter()


@router.get("/live")
async def live_alerts() -> dict:
    return {"alerts": get_full_state()["alerts"]}

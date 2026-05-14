from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.state import known_location
from graph.signal_optimizer import optimize_signal

router = APIRouter()


@router.get("/{intersection}")
async def signal(intersection: str) -> dict:
    if not known_location(intersection):
        raise HTTPException(status_code=404, detail=f"Unknown intersection: {intersection}")
    return optimize_signal(
        intersection,
        {"N": 1280, "S": 840, "E": 1100, "W": 760},
        {"N": 0.8, "S": 0.35, "E": 0.65, "W": 0.45},
    )

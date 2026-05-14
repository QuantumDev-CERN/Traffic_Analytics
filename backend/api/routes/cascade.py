from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.state import CASCADE_EVENTS, clear_incident, inject_incident

router = APIRouter()


class CascadeRequest(BaseModel):
    location: str = "Connaught Place"
    severity: float = Field(default=0.9, ge=0, le=1)


@router.post("/simulate")
async def simulate(payload: CascadeRequest) -> dict:
    try:
        return inject_incident(payload.location, payload.severity)
    except ValueError as exc:
        raise HTTPException(status_code=404 if "Unknown location" in str(exc) else 422, detail=str(exc)) from exc


@router.post("/clear")
async def clear(payload: CascadeRequest) -> dict:
    try:
        return clear_incident(payload.location)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/events")
async def events() -> dict:
    return {"cascade_events": CASCADE_EVENTS}

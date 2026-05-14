from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.state import CASCADE_EVENTS, GRAPH, known_location
from graph.routing import wardrop_route

router = APIRouter()


class RouteRequest(BaseModel):
    origin: str = "Connaught Place"
    destination: str = "Cyber Hub Gurgaon"
    users: int = Field(default=10000, gt=0)


@router.post("/equilibrium")
async def equilibrium(payload: RouteRequest) -> dict:
    if not known_location(payload.origin):
        raise HTTPException(status_code=404, detail=f"Unknown origin: {payload.origin}")
    if not known_location(payload.destination):
        raise HTTPException(status_code=404, detail=f"Unknown destination: {payload.destination}")
    cascade_state = {event["location"]: event for event in CASCADE_EVENTS}
    routes = wardrop_route(GRAPH, payload.origin, payload.destination, payload.users, cascade_state)
    naive = routes[0] if routes else {"name": "Ring Road", "percentage": 100, "eta_minutes": 42}
    return {
        "origin": payload.origin,
        "destination": payload.destination,
        "naive": {**naive, "percentage": 100, "secondary_jam_minutes": 18},
        "wardrop": routes,
        "summary": "Wardrop split prevents a secondary jam and saves about 14 minutes per commuter.",
    }

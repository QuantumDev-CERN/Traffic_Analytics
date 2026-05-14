from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.state import GRAPH, known_location, register_emergency_alert
from graph.routing import wardrop_route
from graph.signal_optimizer import optimize_signal

router = APIRouter()


class EmergencyRouteRequest(BaseModel):
    origin: str = "India Gate"
    destination: str = "IGI Airport T3"
    vehicle: str = "ambulance"


@router.post("/route")
async def emergency_route(payload: EmergencyRouteRequest) -> dict:
    if not known_location(payload.origin):
        raise HTTPException(status_code=404, detail=f"Unknown origin: {payload.origin}")
    if not known_location(payload.destination):
        raise HTTPException(status_code=404, detail=f"Unknown destination: {payload.destination}")
    routes = wardrop_route(GRAPH, payload.origin, payload.destination, 1, None, k_routes=1)
    signal_plan = optimize_signal(
        payload.origin,
        {"N": 900, "S": 620, "E": 780, "W": 540},
        {"N": 0.8, "S": 0.4, "E": 0.6, "W": 0.3},
        {"direction": "N", "eta_seconds": 45},
    )
    eta = routes[0]["eta_minutes"] if routes else None
    alert = register_emergency_alert(payload.origin, payload.vehicle, eta)
    return {"vehicle": payload.vehicle, "green_corridor": routes[:1], "signal_plan": signal_plan, "alert": alert}

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.state import get_full_state
from ml.predict import heuristic_prediction

router = APIRouter()


@router.get("/{location}")
async def predict_location(location: str) -> dict:
    state = get_full_state()
    item = state["locations"].get(location)
    if not item:
        raise HTTPException(status_code=404, detail=f"Unknown location: {location}")
    prediction = heuristic_prediction(
        {
            "Avg Speed (km/h)": item["speed"],
            "Traffic Volume": item["volume"],
            "instability_index": item["instability_index"],
        }
    )
    forecast = [
        {"minute": minute, "label": prediction["label"], "risk": round(min(1.0, item["load"] + minute / 180), 2)}
        for minute in [15, 30, 45, 60]
    ]
    return {
        "location": location,
        "prediction": prediction,
        "phase": item["phase"],
        "phantom": item["phantom"],
        "forecast_60_min": forecast,
    }

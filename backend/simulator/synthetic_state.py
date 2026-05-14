from __future__ import annotations

import math
from datetime import datetime, timedelta

from graph.locations import LOCATIONS
from insights.phase_transition import check_phase_transition, compute_instability
from insights.phantom_jams import detect_phantom_jam

LEVELS = ["Low", "Medium", "High", "Very High"]


def level_from_load(load: float) -> str:
    if load >= 0.82:
        return "Very High"
    if load >= 0.63:
        return "High"
    if load >= 0.38:
        return "Medium"
    return "Low"


def generate_live_state(now: datetime | None = None) -> dict:
    now = now or datetime.now()
    locations: dict[str, dict] = {}
    for i, (name, loc) in enumerate(LOCATIONS.items()):
        rush = 0.22 if now.hour in [8, 9, 18, 19, 20] else 0.0
        wave = 0.18 * (1 + math.sin((now.minute / 60) * math.tau + i * 0.7))
        load = min(0.96, 0.25 + rush + wave + loc.criticality * 0.25)
        speed = max(12, loc.free_flow_speed * (1.1 - load))
        history = [round(speed + math.sin(j * 1.7 + i) * (3 + load * 6) - j * load * 0.7, 1) for j in range(6)]
        if name == "Akshardham Route":
            history = [60, 40, 55, 35, 42, 24]
            speed = history[-1]
            load = 0.72
        if name == "DND Flyway":
            history = [90, 10, 90, 10, 90, 45]
            speed = history[-1]
            load = 0.66
        instability = compute_instability(history[-5:])
        phase = check_phase_transition(name, history[-5:], load, instability).to_dict()
        phantom = detect_phantom_jam(name, history, accident=False, event=False).to_dict()
        locations[name] = {
            "name": name,
            "lat": loc.lat,
            "lng": loc.lng,
            "load": round(load, 2),
            "congestion": level_from_load(load),
            "speed": round(speed, 1),
            "volume": int(650 + load * 1800),
            "instability_index": round(instability, 2),
            "speed_history": history,
            "phase": phase,
            "phantom": phantom,
            "criticality": loc.criticality,
            "updated_at": (now - timedelta(minutes=i % 4)).isoformat(),
        }
    return locations

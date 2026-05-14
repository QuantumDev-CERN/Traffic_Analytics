from __future__ import annotations


def optimize_signal(
    location: str,
    approaches: dict,
    congestion_state: dict,
    emergency_vehicle: dict | None = None,
) -> dict:
    cycle = 90
    min_green = 10
    max_green = 60

    if emergency_vehicle:
        return {
            "location": location,
            "cycle_seconds": cycle,
            "mode": "emergency_preemption",
            "green_seconds": {
                direction: max_green if direction == emergency_vehicle["direction"] else 0
                for direction in approaches
            },
        }

    total_volume = sum(approaches.values()) or 1
    timings = {}
    for direction, volume in approaches.items():
        cong = congestion_state.get(direction, 0)
        weight = (volume / total_volume) * (1 + 0.3 * cong)
        timings[direction] = max(min_green, min(max_green, int(weight * cycle)))
    return {"location": location, "cycle_seconds": cycle, "mode": "adaptive_webster", "green_seconds": timings}

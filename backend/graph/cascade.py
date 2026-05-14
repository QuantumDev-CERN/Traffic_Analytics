from __future__ import annotations

import heapq
from dataclasses import asdict, dataclass
from typing import Dict, List

import numpy as np


@dataclass
class CascadeEvent:
    arrival_time: float
    location: str
    severity: float
    cause: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["arrival_time"] = round(data["arrival_time"], 1)
        data["severity"] = round(data["severity"], 2)
        return data


def simulate_cascade(
    source_location: str,
    initial_severity: float,
    current_states: Dict[str, float],
    monitoring_node_ids: Dict[str, str],
    route_cache: Dict[tuple[str, str], dict],
    time_horizon: int = 60,
) -> List[CascadeEvent]:
    events: list[CascadeEvent] = []
    queue = [(0.0, source_location, initial_severity, "direct")]
    visited: set[str] = set()

    while queue:
        arr_time, loc, severity, cause = heapq.heappop(queue)
        if arr_time > time_horizon or loc in visited:
            continue

        visited.add(loc)
        events.append(CascadeEvent(arr_time, loc, min(1.0, severity), cause))
        src_node = monitoring_node_ids[loc]

        for other_loc, other_node in monitoring_node_ids.items():
            if other_loc in visited:
                continue

            route = route_cache.get((src_node, other_node))
            if not route:
                continue

            base_travel_time = float(route["travel_time_min"])
            route_length_km = base_travel_time * 0.5
            wave_time = route_length_km / 20.0 * 60
            decay = float(np.exp(-wave_time / 25.0))
            up_severity = severity * decay * 0.7
            if up_severity > 0.10:
                heapq.heappush(queue, (arr_time + wave_time, other_loc, up_severity, "upstream_wave"))

            if base_travel_time < 35:
                diversion_frac = severity * 0.3 * float(np.exp(-base_travel_time / 20.0))
                current_load = current_states.get(other_loc, 0.0)
                new_severity = min(1.0, current_load + diversion_frac)
                delay = 5 + base_travel_time * 0.2
                if diversion_frac > 0.05:
                    heapq.heappush(queue, (arr_time + delay, other_loc, new_severity, "diverted_load"))

    return sorted(events, key=lambda e: e.arrival_time)

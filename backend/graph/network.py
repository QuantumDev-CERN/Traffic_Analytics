from __future__ import annotations

import math
from itertools import combinations

import networkx as nx

from .locations import LOCATIONS


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    radius = 6371.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def monitoring_node_ids() -> dict[str, str]:
    return {name: name for name in LOCATIONS}


def build_demo_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for name, loc in LOCATIONS.items():
        graph.add_node(name, y=loc.lat, x=loc.lng, criticality=loc.criticality)

    for left, right in combinations(LOCATIONS.keys(), 2):
        a = LOCATIONS[left]
        b = LOCATIONS[right]
        distance = haversine_km((a.lat, a.lng), (b.lat, b.lng))
        if distance <= 18 or left == "Connaught Place" or right == "Connaught Place":
            travel_time = max(6.0, distance / 32 * 60)
            capacity = int(900 + 900 * max(a.criticality, b.criticality))
            attrs = {
                "length_km": round(distance, 2),
                "travel_time": travel_time * 60,
                "travel_time_min": travel_time,
                "capacity": capacity,
                "name": f"{left} to {right}",
            }
            graph.add_edge(left, right, **attrs)
            graph.add_edge(right, left, **attrs)

    return graph


def precompute_route_cache(graph: nx.MultiDiGraph | None = None) -> dict[tuple[str, str], dict]:
    graph = graph or build_demo_graph()
    cache: dict[tuple[str, str], dict] = {}
    for source in LOCATIONS:
        for target in LOCATIONS:
            if source == target:
                continue
            try:
                path = nx.shortest_path(graph, source, target, weight="travel_time")
                travel_time = nx.path_weight(graph, path, weight="travel_time") / 60
                cache[(source, target)] = {
                    "path": path,
                    "travel_time_min": round(float(travel_time), 1),
                }
            except nx.NetworkXNoPath:
                continue
    return cache

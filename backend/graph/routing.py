from __future__ import annotations

from typing import Dict, List

import networkx as nx
import numpy as np


def _edge_data(graph, u, v) -> dict:
    data = graph[u][v]
    return data[0] if isinstance(data, dict) and 0 in data else next(iter(data.values()))


def route_name(path: list[str]) -> str:
    if len(path) <= 3:
        return " -> ".join(path)
    return " -> ".join([path[0], path[1], "...", path[-1]])


def bpr_travel_time(graph, path: list, flow: float, cascade_state: Dict | None = None) -> float:
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        data = _edge_data(graph, u, v)
        cap = data.get("capacity", 1500)
        t0 = data.get("travel_time", 60) / 60
        cascade_mult = 1.0
        if cascade_state:
            for event in cascade_state.values():
                if event.get("severity", 0) > 0.5:
                    cascade_mult = max(cascade_mult, 1 + event["severity"] * 0.4)
        total += t0 * cascade_mult * (1 + 0.15 * (flow / cap) ** 4)
    return float(total)


def _join_paths(parts: list[list[str]]) -> list[str]:
    route: list[str] = []
    for part in parts:
        if not part:
            continue
        if route and route[-1] == part[0]:
            route.extend(part[1:])
        else:
            route.extend(part)
    return route


def _candidate_routes(graph, origin_node: str, dest_node: str, k_routes: int) -> list[list[str]]:
    simple_graph = nx.Graph(graph)
    candidates: list[list[str]] = []

    def add(path: list[str]) -> None:
        if path and path not in candidates:
            candidates.append(path)

    try:
        add(nx.shortest_path(simple_graph, origin_node, dest_node, weight="travel_time"))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    waypoints = [
        "India Gate",
        "DND Flyway",
        "Dwarka Sector 21",
        "Lajpat Nagar",
        "Akshardham Route",
        "MG Road Gurgaon",
        "Sector 18 Noida",
    ]
    for waypoint in waypoints:
        if waypoint in {origin_node, dest_node} or waypoint not in simple_graph:
            continue
        try:
            first = nx.shortest_path(simple_graph, origin_node, waypoint, weight="travel_time")
            second = nx.shortest_path(simple_graph, waypoint, dest_node, weight="travel_time")
            add(_join_paths([first, second]))
        except nx.NetworkXNoPath:
            continue
        if len(candidates) >= k_routes:
            break

    return candidates[:k_routes]


def wardrop_route(
    graph,
    origin_node: str,
    dest_node: str,
    total_users: int,
    cascade_state: Dict | None = None,
    k_routes: int = 4,
    max_iterations: int = 30,
) -> List[Dict]:
    candidates = _candidate_routes(graph, origin_node, dest_node, k_routes)

    if not candidates:
        return []

    flows = [float(total_users)] + [0.0] * (len(candidates) - 1)
    times = [bpr_travel_time(graph, p, f, cascade_state) for p, f in zip(candidates, flows)]

    for _ in range(max_iterations):
        times = [bpr_travel_time(graph, p, f, cascade_state) for p, f in zip(candidates, flows)]
        worst = int(np.argmax(times))
        best = int(np.argmin(times))
        if times[worst] - times[best] < 0.3:
            break
        transfer = min(flows[worst] * 0.15, total_users * 0.08)
        flows[worst] -= transfer
        flows[best] += transfer

    return [
        {
            "route_nodes": path,
            "name": route_name(path),
            "users": int(flow),
            "eta_minutes": round(time, 1),
            "percentage": round(100 * flow / total_users, 1),
        }
        for path, flow, time in zip(candidates, flows, times)
        if flow > total_users * 0.05
    ]

from __future__ import annotations

from datetime import datetime

from graph.cascade import simulate_cascade
from graph.locations import LOCATIONS
from graph.locations import as_geojson_points
from graph.network import build_demo_graph, monitoring_node_ids, precompute_route_cache
from insights.hysteresis import recovery_eta
from simulator.synthetic_state import generate_live_state

GRAPH = build_demo_graph()
MONITORING_NODE_IDS = monitoring_node_ids()
ROUTE_CACHE = precompute_route_cache(GRAPH)
INCIDENTS: dict[str, dict] = {}
RECOVERIES: dict[str, dict] = {}
EMERGENCY_ALERTS: list[dict] = []
CASCADE_EVENTS: list[dict] = []


def known_location(location: str) -> bool:
    return location in LOCATIONS


def _alerts_from_locations(locations: dict) -> list[dict]:
    alerts = []
    for name, item in locations.items():
        phase = item.get("phase", {})
        phantom = item.get("phantom", {})
        if phase.get("phase") == "pre_transition":
            alerts.append({"type": "pre_transition", "severity": "high", "location": name, "message": phase["warning_message"]})
        if phantom.get("detected"):
            alerts.append({"type": "phantom", "severity": "critical", "location": name, "message": phantom["message"]})
        if item.get("congestion") == "Very High":
            alerts.append({"type": "congestion", "severity": "high", "location": name, "message": f"{name} is in Very High congestion."})
    for recovery in RECOVERIES.values():
        alerts.append({"type": "recovery", "severity": "medium", "location": recovery["location"], "message": recovery["status"]["message"]})
    alerts.extend(EMERGENCY_ALERTS[-3:])
    for event in CASCADE_EVENTS[:5]:
        alerts.append({"type": "cascade", "severity": "medium", "location": event["location"], "message": f"Cascade impact at T+{event['arrival_time']} min."})
    return alerts[:12]


def get_full_state() -> dict:
    locations = generate_live_state()
    for loc, incident in INCIDENTS.items():
        if loc in locations:
            locations[loc]["congestion"] = "Very High"
            locations[loc]["load"] = max(locations[loc]["load"], incident["severity"])
            locations[loc]["incident"] = incident
    for loc, recovery in RECOVERIES.items():
        if loc in locations:
            locations[loc]["recovery"] = recovery["status"]
    return {
        "timestamp": datetime.now().isoformat(),
        "locations": locations,
        "location_points": as_geojson_points(),
        "incidents": INCIDENTS,
        "recoveries": RECOVERIES,
        "cascade_events": CASCADE_EVENTS,
        "alerts": _alerts_from_locations(locations),
    }


def inject_incident(location: str, severity: float = 0.9) -> dict:
    if not known_location(location):
        raise ValueError(f"Unknown location: {location}")
    if not 0 <= severity <= 1:
        raise ValueError("severity must be between 0 and 1")
    INCIDENTS[location] = {"location": location, "severity": severity, "started_at": datetime.now().isoformat()}
    RECOVERIES.pop(location, None)
    current_states = {name: item["load"] for name, item in generate_live_state().items()}
    events = simulate_cascade(location, severity, current_states, MONITORING_NODE_IDS, ROUTE_CACHE)
    CASCADE_EVENTS.clear()
    CASCADE_EVENTS.extend([event.to_dict() for event in events])
    return {"incident": INCIDENTS[location], "cascade_events": CASCADE_EVENTS}


def clear_incident(location: str) -> dict:
    if not known_location(location):
        raise ValueError(f"Unknown location: {location}")
    incident = INCIDENTS.pop(location, None)
    if incident:
        incident["cleared_at"] = datetime.now().isoformat()
        status = recovery_eta(location, datetime.fromisoformat(incident["cleared_at"]), 2.4, 24).to_dict()
        RECOVERIES[location] = {"location": location, "incident": incident, "status": status}
    return {"cleared": incident is not None, "incident": incident}


def register_emergency_alert(location: str, vehicle: str, eta_minutes: float | int | None) -> dict:
    alert = {
        "type": "emergency",
        "severity": "critical",
        "location": location,
        "message": f"{vehicle.title()} green corridor active from {location}; ETA {eta_minutes or 'unknown'} minutes.",
    }
    EMERGENCY_ALERTS.append(alert)
    return alert

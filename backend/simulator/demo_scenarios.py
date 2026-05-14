from __future__ import annotations

from api.state import get_full_state, inject_incident
from graph.criticality import network_criticality
from graph.signal_optimizer import optimize_signal
from insights.hysteresis import recovery_eta


def cascade_demo() -> dict:
    return inject_incident("Connaught Place", 0.92)


def five_insight_demo() -> dict:
    state = get_full_state()
    return {
        "cascade": cascade_demo(),
        "phase": state["locations"]["DND Flyway"]["phase"],
        "phantom": state["locations"]["Akshardham Route"]["phantom"],
        "criticality": network_criticality()[:5],
        "emergency_signal": optimize_signal("India Gate", {"N": 900, "S": 700, "E": 650, "W": 500}, {}, {"direction": "N"}),
        "recovery": recovery_eta("DND Flyway", None, 2.4, 18).to_dict(),
    }


if __name__ == "__main__":
    print(five_insight_demo())

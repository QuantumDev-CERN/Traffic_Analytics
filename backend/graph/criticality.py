from __future__ import annotations

from .locations import LOCATIONS


def network_criticality() -> list[dict]:
    ranked = sorted(LOCATIONS.values(), key=lambda item: item.criticality, reverse=True)
    return [
        {
            "location": item.name,
            "criticality": item.criticality,
            "risk_label": "Critical" if item.criticality > 0.85 else "High" if item.criticality > 0.72 else "Watch",
        }
        for item in ranked
    ]

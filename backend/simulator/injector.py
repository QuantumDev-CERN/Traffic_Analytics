from __future__ import annotations

from api.state import clear_incident, inject_incident


def inject_phantom(location: str = "Akshardham Route") -> dict:
    return {"location": location, "speed_history": [60, 40, 55, 35, 42, 24]}


__all__ = ["inject_incident", "clear_incident", "inject_phantom"]

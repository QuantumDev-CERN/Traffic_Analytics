from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

import numpy as np

PRE_TRANSITION_THRESHOLD = 0.65


@dataclass
class PhaseAlert:
    location: str
    instability_index: float
    phase: str
    warning_message: Optional[str]
    minutes_to_jam: Optional[int]

    def to_dict(self) -> dict:
        return asdict(self)


def compute_instability(speeds: list[float]) -> float:
    if len(speeds) < 2:
        return 0.0
    arr = np.asarray(speeds, dtype=float)
    return float(np.std(arr) / (np.mean(arr) + 1e-6))


def check_phase_transition(
    location: str,
    recent_speeds: list[float],
    current_congestion_prob: float,
    instability_index: float | None = None,
) -> PhaseAlert:
    instability = compute_instability(recent_speeds) if instability_index is None else instability_index
    mean_speed = float(np.mean(recent_speeds)) if recent_speeds else 0.0

    if instability > PRE_TRANSITION_THRESHOLD and mean_speed > 20:
        minutes_estimate = max(8, int(15 * (1 - min(instability, 0.95))))
        return PhaseAlert(
            location=location,
            instability_index=round(instability, 3),
            phase="pre_transition",
            warning_message=(
                f"PRE-TRANSITION WARNING: {location} approaching phase transition. "
                f"Speed variance spiking at {instability:.2f}; jam expected in about "
                f"{minutes_estimate} minutes."
            ),
            minutes_to_jam=minutes_estimate,
        )

    if mean_speed < 20 or current_congestion_prob > 0.7:
        return PhaseAlert(location, round(instability, 3), "jammed", None, 0)

    return PhaseAlert(location, round(instability, 3), "stable", None, None)

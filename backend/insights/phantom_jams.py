from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

import numpy as np

OSCILLATION_THRESHOLD = 8.0
DECLINING_SPEED_MIN = 35.0


@dataclass
class PhantomJamResult:
    location: str
    detected: bool
    oscillation_score: float
    speed_history: list[float]
    message: Optional[str]
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


def detect_phantom_jam(
    location: str,
    speed_history: list[float],
    accident: bool,
    event: bool,
) -> PhantomJamResult:
    if len(speed_history) < 4:
        return PhantomJamResult(location, False, 0.0, speed_history, None, 0.0)

    speeds = np.asarray(speed_history, dtype=float)
    diffs = np.diff(speeds)
    no_external_cause = not accident and not event
    sign_changes = int(np.sum(np.diff(np.sign(diffs)) != 0))
    is_oscillating = sign_changes >= 2
    is_declining = bool(speeds[-1] < speeds[0] and speeds[-1] < DECLINING_SPEED_MIN)
    oscillation_score = float(np.std(diffs))
    is_significant = oscillation_score > OSCILLATION_THRESHOLD
    detected = no_external_cause and is_oscillating and is_declining and is_significant

    confidence = 0.0
    if detected:
        confidence = min(
            1.0,
            0.3 * (sign_changes / 4)
            + 0.4 * (oscillation_score / 15)
            + 0.3 * ((DECLINING_SPEED_MIN - speeds[-1]) / DECLINING_SPEED_MIN),
        )

    return PhantomJamResult(
        location=location,
        detected=detected,
        oscillation_score=round(oscillation_score, 2),
        speed_history=[float(v) for v in speed_history],
        confidence=round(float(confidence), 2),
        message=(
            f"PHANTOM JAM DETECTED: {location}. No accident or event flags, but "
            f"speed oscillation score is {oscillation_score:.1f}; jam expected in about 10 minutes."
        )
        if detected
        else None,
    )

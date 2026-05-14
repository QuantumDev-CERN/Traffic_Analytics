from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

import numpy as np

BASE_RECOVERY_MINUTES = 30
CAPACITY_DROP_FACTOR = 0.10


@dataclass
class RecoveryStatus:
    location: str
    in_recovery: bool
    recovery_eta_minutes: Optional[int]
    current_capacity_pct: float
    message: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


def recovery_eta(
    location: str,
    incident_cleared_at: Optional[datetime],
    congestion_memory: float,
    current_speed: float,
    free_flow_speed: float = 50.0,
) -> RecoveryStatus:
    if incident_cleared_at is None:
        return RecoveryStatus(location, False, None, 1.0, None)

    minutes_since_clear = max(0.0, (datetime.now() - incident_cleared_at).total_seconds() / 60)
    jam_depth = min(1.0, max(congestion_memory / 3.0, 1 - current_speed / max(free_flow_speed, 1)))
    total_recovery_time = BASE_RECOVERY_MINUTES * (1 + jam_depth)

    if minutes_since_clear >= total_recovery_time:
        return RecoveryStatus(location, False, None, 1.0, None)

    recovery_fraction = 1 - np.exp(-3 * minutes_since_clear / total_recovery_time)
    remaining_minutes = int(np.ceil(total_recovery_time - minutes_since_clear))
    capacity_pct = (1 - CAPACITY_DROP_FACTOR) + CAPACITY_DROP_FACTOR * recovery_fraction

    return RecoveryStatus(
        location=location,
        in_recovery=True,
        recovery_eta_minutes=remaining_minutes,
        current_capacity_pct=round(float(capacity_pct), 2),
        message=(
            f"RECOVERY MODE: {location} incident cleared, but throughput is still "
            f"{int(capacity_pct * 100)}%. Full recovery in about {remaining_minutes} minutes."
        ),
    )

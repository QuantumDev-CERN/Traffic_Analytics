from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from api.main import app
from api import state as app_state


@pytest.fixture(autouse=True)
def reset_demo_state():
    app_state.INCIDENTS.clear()
    app_state.RECOVERIES.clear()
    app_state.EMERGENCY_ALERTS.clear()
    app_state.CASCADE_EVENTS.clear()
    yield
    app_state.INCIDENTS.clear()
    app_state.RECOVERIES.clear()
    app_state.EMERGENCY_ALERTS.clear()
    app_state.CASCADE_EVENTS.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)

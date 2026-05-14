from datetime import datetime, timedelta

from backend.graph.cascade import simulate_cascade
from backend.graph.network import monitoring_node_ids, precompute_route_cache
from backend.insights.hysteresis import recovery_eta
from backend.insights.phase_transition import check_phase_transition
from backend.insights.phantom_jams import detect_phantom_jam


def test_phantom_jam_detects_oscillation():
    result = detect_phantom_jam("Akshardham Route", [60, 40, 55, 35, 42, 24], False, False)
    assert result.detected


def test_phase_transition_flags_variance_before_low_speed():
    result = check_phase_transition("DND Flyway", [90, 10, 90, 10, 90], 0.4)
    assert result.phase == "pre_transition"


def test_recovery_eta_reports_active_recovery():
    result = recovery_eta("DND Flyway", datetime.now() - timedelta(minutes=8), 2.5, 24)
    assert result.in_recovery


def test_cascade_has_multiple_events():
    nodes = monitoring_node_ids()
    cache = precompute_route_cache()
    events = simulate_cascade("Connaught Place", 0.9, {name: 0.45 for name in nodes}, nodes, cache)
    assert len(events) > 1

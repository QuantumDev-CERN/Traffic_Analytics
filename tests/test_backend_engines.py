from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from api.state import GRAPH, MONITORING_NODE_IDS, ROUTE_CACHE, get_full_state, inject_incident
from graph.cascade import simulate_cascade
from graph.criticality import network_criticality
from graph.locations import LOCATIONS, as_geojson_points
from graph.network import build_demo_graph, haversine_km, monitoring_node_ids, precompute_route_cache
from graph.routing import bpr_travel_time, route_name, wardrop_route
from graph.signal_optimizer import optimize_signal
from insights.hysteresis import recovery_eta
from insights.phase_transition import check_phase_transition, compute_instability
from insights.phantom_jams import detect_phantom_jam
from ml.feature_engineering import FEATURE_COLS, build_features, normalize_columns
from ml.predict import heuristic_prediction, predict_congestion
from ml import train as train_module
from simulator.demo_scenarios import cascade_demo, five_insight_demo
from simulator.injector import inject_phantom
from simulator.synthetic_state import generate_live_state, level_from_load


def sample_dataframe() -> pd.DataFrame:
    rows = []
    levels = ["Low", "Medium", "High", "Very High", "Low", "Medium", "High", "Very High", "High", "Medium"]
    for loc in ["Connaught Place", "India Gate"]:
        for i, level in enumerate(levels):
            rows.append(
                {
                    "Timestamp": f"2026-05-01 0{i}:00:00",
                    "Location": loc,
                    "Traffic Volume": 600 + i * 250,
                    "Avg Speed (km/h)": 60 - i * 8,
                    "Rain(mm)": i % 2,
                    "Public Transport Density": 0.4 + i * 0.03,
                    "Weather": "Rain" if i % 2 else "Clear",
                    "Accident": "Yes" if i == 3 else "No",
                    "Event": "Yes" if i == 4 else "No",
                    "Congestion Level": level,
                }
            )
    return pd.DataFrame(rows)


def test_locations_are_16_ncr_monitoring_points():
    assert len(LOCATIONS) == 16
    points = as_geojson_points()
    assert len(points) == 16
    assert points[0].keys() == {"name", "lat", "lng", "criticality"}


def test_network_graph_and_route_cache_cover_monitoring_nodes():
    graph = build_demo_graph()
    assert graph.number_of_nodes() == 16
    assert graph.number_of_edges() > 0
    nodes = monitoring_node_ids()
    assert nodes["Connaught Place"] == "Connaught Place"
    cache = precompute_route_cache(graph)
    assert ("Connaught Place", "India Gate") in cache
    assert cache[("Connaught Place", "India Gate")]["travel_time_min"] > 0
    assert haversine_km((28.6315, 77.2167), (28.6129, 77.2295)) > 0


def test_cascade_engine_direct_diversion_and_time_horizon():
    states = {name: 0.4 for name in MONITORING_NODE_IDS}
    events = simulate_cascade("Connaught Place", 0.9, states, MONITORING_NODE_IDS, ROUTE_CACHE, time_horizon=60)
    assert events[0].location == "Connaught Place"
    assert events[0].arrival_time == 0
    assert {event.cause for event in events}.intersection({"diverted_load", "upstream_wave"})
    assert all(event.arrival_time <= 60 for event in events)
    assert events == sorted(events, key=lambda event: event.arrival_time)


def test_cascade_engine_rejects_unknown_source():
    with pytest.raises(KeyError):
        simulate_cascade("Atlantis", 0.9, {}, MONITORING_NODE_IDS, ROUTE_CACHE)


def test_wardrop_routing_splits_users_and_bpr_penalizes_flow():
    routes = wardrop_route(GRAPH, "Connaught Place", "Cyber Hub Gurgaon", 10000)
    assert len(routes) >= 2
    assert all(route["eta_minutes"] > 0 for route in routes)
    assert all(route["percentage"] > 0 for route in routes)
    assert route_name(["A", "B", "C", "D"]) == "A -> B -> ... -> D"
    path = routes[0]["route_nodes"]
    assert bpr_travel_time(GRAPH, path, 10000) > bpr_travel_time(GRAPH, path, 100)


def test_wardrop_unknown_nodes_return_empty_routes():
    assert wardrop_route(GRAPH, "Atlantis", "Cyber Hub Gurgaon", 1000) == []


def test_signal_optimizer_adaptive_and_emergency_modes():
    adaptive = optimize_signal("India Gate", {"N": 1200, "S": 800, "E": 1000, "W": 700}, {"N": 0.8})
    assert adaptive["mode"] == "adaptive_webster"
    assert all(10 <= value <= 60 for value in adaptive["green_seconds"].values())
    emergency = optimize_signal("India Gate", {"N": 1, "S": 1, "E": 1, "W": 1}, {}, {"direction": "E"})
    assert emergency["mode"] == "emergency_preemption"
    assert emergency["green_seconds"] == {"N": 0, "S": 0, "E": 60, "W": 0}


def test_network_criticality_ranks_connaught_place_highest():
    ranked = network_criticality()
    assert ranked[0]["location"] == "Connaught Place"
    assert ranked[0]["risk_label"] == "Critical"


def test_phase_transition_stable_pretransition_and_jammed_paths():
    assert compute_instability([40]) == 0
    assert check_phase_transition("DND Flyway", [42, 43, 41], 0.2).phase == "stable"
    assert check_phase_transition("DND Flyway", [90, 10, 90, 10, 90], 0.4).phase == "pre_transition"
    assert check_phase_transition("DND Flyway", [12, 14, 13], 0.2).phase == "jammed"
    assert check_phase_transition("DND Flyway", [40, 42, 41], 0.8).phase == "jammed"


def test_hysteresis_recovery_paths():
    none = recovery_eta("DND Flyway", None, 0, 50)
    assert none.in_recovery is False
    active = recovery_eta("DND Flyway", datetime.now() - timedelta(minutes=5), 2.7, 22)
    assert active.in_recovery is True
    assert active.recovery_eta_minutes > 0
    completed = recovery_eta("DND Flyway", datetime.now() - timedelta(minutes=90), 2.7, 48)
    assert completed.in_recovery is False


def test_phantom_jam_positive_and_negative_paths():
    detected = detect_phantom_jam("Akshardham Route", [60, 40, 55, 35, 42, 24], False, False)
    assert detected.detected is True
    assert detected.confidence > 0
    assert detect_phantom_jam("Akshardham Route", [60, 40, 55, 35, 42, 24], True, False).detected is False
    assert detect_phantom_jam("Akshardham Route", [60, 59, 58], False, False).detected is False
    assert detect_phantom_jam("Akshardham Route", [60, 58, 56, 54, 52], False, False).detected is False


def test_feature_engineering_builds_all_required_features():
    normalized = normalize_columns(sample_dataframe().rename(columns={"Traffic Volume": "TrafficVolume"}))
    assert "Traffic Volume" in normalized.columns
    features, encoder = build_features(sample_dataframe())
    assert len(features) > 0
    assert set(FEATURE_COLS).issubset(features.columns)
    assert features[FEATURE_COLS].isna().sum().sum() == 0
    assert len(encoder.classes_) == 2


def test_feature_engineering_missing_required_columns_raises():
    with pytest.raises(ValueError):
        build_features(pd.DataFrame({"Timestamp": ["2026-05-01"], "Location": ["India Gate"]}))


def test_predict_heuristic_and_batch_prediction_paths():
    high = heuristic_prediction({"Avg Speed (km/h)": 12, "Traffic Volume": 2500, "instability_index": 0.8, "Accident": "Yes"})
    assert high["label"] == "Very High"
    low = heuristic_prediction({"Avg Speed (km/h)": 65, "Traffic Volume": 300, "instability_index": 0.1})
    assert low["label"] == "Low"
    batch = predict_congestion(sample_dataframe().head(3).to_dict(orient="records"))
    assert len(batch) == 3
    assert all(item["model"] in {"heuristic", "xgboost"} for item in batch)


def test_train_model_path_with_small_dataset(tmp_path, monkeypatch):
    dataset = tmp_path / "traffic.xlsx"
    model_path = tmp_path / "model.json"
    train_path = tmp_path / "features_train.csv"
    test_path = tmp_path / "features_test.csv"
    sample_dataframe().to_excel(dataset, index=False)
    monkeypatch.setattr(train_module, "DATASET", dataset)
    monkeypatch.setattr(train_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(train_module, "TRAIN_PATH", train_path)
    monkeypatch.setattr(train_module, "TEST_PATH", test_path)
    result = train_module.train_model(n_estimators=5)
    assert result["rows"] > 0
    assert 0 <= result["accuracy"] <= 1
    assert model_path.exists()
    assert train_path.exists()
    assert test_path.exists()


def test_synthetic_state_contains_required_demo_signals():
    assert level_from_load(0.9) == "Very High"
    state = generate_live_state()
    assert len(state) == 16
    assert state["DND Flyway"]["phase"]["phase"] == "pre_transition"
    assert state["Akshardham Route"]["phantom"]["detected"] is True


def test_api_state_injection_and_demo_scenarios():
    incident = inject_incident("Connaught Place", 0.9)
    assert incident["cascade_events"]
    full_state = get_full_state()
    assert full_state["incidents"]["Connaught Place"]["severity"] == 0.9
    assert cascade_demo()["cascade_events"]
    demo = five_insight_demo()
    assert set(demo).issuperset({"cascade", "phase", "phantom", "criticality", "emergency_signal", "recovery"})
    assert inject_phantom()["location"] == "Akshardham Route"

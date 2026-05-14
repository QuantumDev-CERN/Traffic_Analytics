from __future__ import annotations


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "service": "HackZilla Traffic AI"}


def test_state_endpoint_covers_dashboard_requirements(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert len(data["locations"]) == 16
    assert len(data["location_points"]) == 16
    assert set(data).issuperset({"timestamp", "locations", "incidents", "recoveries", "cascade_events", "alerts"})
    assert data["locations"]["DND Flyway"]["phase"]["phase"] == "pre_transition"
    assert data["locations"]["Akshardham Route"]["phantom"]["detected"] is True
    alert_types = {alert["type"] for alert in data["alerts"]}
    assert {"pre_transition", "phantom"}.issubset(alert_types)


def test_predict_valid_location_has_forecast_and_insights(client):
    response = client.get("/api/predict/Connaught Place")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Connaught Place"
    assert data["prediction"]["label"] in ["Low", "Medium", "High", "Very High"]
    assert set(data["prediction"]["probabilities"]) == {"Low", "Medium", "High", "Very High"}
    assert len(data["forecast_60_min"]) == 4
    assert data["forecast_60_min"][-1]["minute"] == 60
    assert set(data).issuperset({"phase", "phantom"})


def test_predict_unknown_location_returns_404(client):
    response = client.get("/api/predict/Atlantis")
    assert response.status_code == 404
    assert "Unknown location" in response.json()["detail"]


def test_cascade_simulate_injects_incident_and_ordered_events(client):
    response = client.post("/api/cascade/simulate", json={"location": "Connaught Place", "severity": 0.92})
    assert response.status_code == 200
    data = response.json()
    events = data["cascade_events"]
    assert data["incident"]["location"] == "Connaught Place"
    assert events[0] == {"arrival_time": 0.0, "location": "Connaught Place", "severity": 0.92, "cause": "direct"}
    assert len(events) >= 4
    assert events == sorted(events, key=lambda item: item["arrival_time"])
    assert all(0 <= event["severity"] <= 1 for event in events)
    assert all(event["arrival_time"] <= 60 for event in events)


def test_cascade_events_endpoint_reflects_latest_simulation(client):
    client.post("/api/cascade/simulate", json={"location": "Connaught Place", "severity": 0.9})
    response = client.get("/api/cascade/events")
    assert response.status_code == 200
    events = response.json()["cascade_events"]
    assert events[0]["location"] == "Connaught Place"


def test_cascade_clear_moves_incident_into_recovery_alert(client):
    client.post("/api/cascade/simulate", json={"location": "DND Flyway", "severity": 0.95})
    clear_response = client.post("/api/cascade/clear", json={"location": "DND Flyway"})
    assert clear_response.status_code == 200
    assert clear_response.json()["cleared"] is True

    state = client.get("/api/state").json()
    assert "DND Flyway" in state["recoveries"]
    assert state["locations"]["DND Flyway"]["recovery"]["in_recovery"] is True
    assert "recovery" in {alert["type"] for alert in state["alerts"]}


def test_cascade_clear_without_active_incident_is_safe(client):
    response = client.post("/api/cascade/clear", json={"location": "DND Flyway"})
    assert response.status_code == 200
    assert response.json() == {"cleared": False, "incident": None}


def test_cascade_bad_location_and_bad_severity_are_rejected(client):
    unknown = client.post("/api/cascade/simulate", json={"location": "Atlantis", "severity": 0.9})
    assert unknown.status_code == 404
    invalid = client.post("/api/cascade/simulate", json={"location": "Connaught Place", "severity": 1.5})
    assert invalid.status_code == 422


def test_route_equilibrium_returns_naive_and_wardrop_distribution(client):
    response = client.post(
        "/api/route/equilibrium",
        json={"origin": "Connaught Place", "destination": "Cyber Hub Gurgaon", "users": 10000},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["naive"]["percentage"] == 100
    assert data["naive"]["secondary_jam_minutes"] == 18
    assert len(data["wardrop"]) >= 2
    assert sum(route["users"] for route in data["wardrop"]) <= 10000
    assert all(route["percentage"] > 0 for route in data["wardrop"])
    assert "14 minutes" in data["summary"]


def test_route_rejects_unknown_origin_destination_and_bad_users(client):
    assert client.post("/api/route/equilibrium", json={"origin": "Atlantis", "destination": "India Gate"}).status_code == 404
    assert client.post("/api/route/equilibrium", json={"origin": "India Gate", "destination": "Atlantis"}).status_code == 404
    assert client.post("/api/route/equilibrium", json={"origin": "India Gate", "destination": "IGI Airport T3", "users": 0}).status_code == 422


def test_alerts_live_includes_five_alert_families_after_actions(client):
    client.post("/api/cascade/simulate", json={"location": "Connaught Place", "severity": 0.92})
    client.post("/api/cascade/clear", json={"location": "Connaught Place"})
    client.post("/api/emergency/route", json={"origin": "India Gate", "destination": "IGI Airport T3", "vehicle": "ambulance"})
    response = client.get("/api/alerts/live")
    assert response.status_code == 200
    alert_types = {alert["type"] for alert in response.json()["alerts"]}
    assert {"pre_transition", "phantom", "cascade", "recovery", "emergency"}.issubset(alert_types)


def test_emergency_route_creates_green_corridor_and_preempts_signal(client):
    response = client.post(
        "/api/emergency/route",
        json={"origin": "India Gate", "destination": "IGI Airport T3", "vehicle": "ambulance"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle"] == "ambulance"
    assert data["green_corridor"]
    assert data["signal_plan"]["mode"] == "emergency_preemption"
    assert data["signal_plan"]["green_seconds"]["N"] == 60
    assert data["alert"]["type"] == "emergency"


def test_emergency_route_rejects_unknown_locations(client):
    assert client.post("/api/emergency/route", json={"origin": "Atlantis", "destination": "IGI Airport T3"}).status_code == 404
    assert client.post("/api/emergency/route", json={"origin": "India Gate", "destination": "Atlantis"}).status_code == 404


def test_signal_endpoint_returns_adaptive_webster_timings(client):
    response = client.get("/api/signals/India Gate")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "India Gate"
    assert data["mode"] == "adaptive_webster"
    assert data["cycle_seconds"] == 90
    assert set(data["green_seconds"]) == {"N", "S", "E", "W"}
    assert all(10 <= seconds <= 60 for seconds in data["green_seconds"].values())


def test_signal_endpoint_rejects_unknown_intersection(client):
    response = client.get("/api/signals/Atlantis")
    assert response.status_code == 404


def test_chatbot_offline_mode_uses_live_context(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post("/api/chat/", json={"text": "Fastest way from India Gate to IGI Airport?"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "offline-demo"
    assert "Current hotspots" in data["response"]
    assert "India Gate to IGI Airport" in data["response"]


def test_websocket_live_stream_sends_full_state(client):
    with client.websocket_connect("/ws/live") as websocket:
        data = websocket.receive_json()
    assert len(data["locations"]) == 16
    assert "alerts" in data

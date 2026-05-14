# Backend Test Plan And Current Results

Scope: backend only. Frontend responsiveness work is blocked until this suite stays green.

Sources covered:
- `HACKZILLA_MASTER.md`: five insights, objective coverage, API layer, simulator, ML, graph, websocket.
- `Hackzilla_Winners.docx`: cascade propagation, Wardrop/Nash routing, phase transition, hysteresis memory, phantom jams, alerts, emergency route, chatbot, mobile/web dashboard backend feed.

Last verified command:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests -q
```

Current result:

```text
39 passed
```

Compile verification:

```bash
PYTHONPATH=backend .venv/bin/python -m py_compile $(rg --files backend -g '*.py')
```

Current result: pass.

## API Contract Matrix

| Area | API path | Test cases | Expected output | Current verified output |
|---|---|---|---|---|
| Health | `GET /health` | Service probe | `200`, `{"ok": true, "service": "HackZilla Traffic AI"}` | Pass, exact response matched |
| State | `GET /api/state` | Full live state | `200`, 16 locations, 16 map points, incidents, recoveries, cascade events, alerts | Pass, 16 locations returned; DND has `pre_transition`; Akshardham has phantom jam |
| Prediction | `GET /api/predict/{location}` | Valid location | `200`, location, congestion label/probabilities, phase, phantom, 15/30/45/60 min forecast | Pass, Connaught Place returns prediction and `forecast_60_min` with 4 points |
| Prediction | `GET /api/predict/{bad_location}` | Unknown location | `404` with unknown location detail | Pass, `Atlantis` returns `404` |
| Cascade | `POST /api/cascade/simulate` | Valid incident | `200`, incident object plus ordered cascade events within 60 min | Pass, CP direct event at T+0 and multiple downstream impacts |
| Cascade | `POST /api/cascade/simulate` | Bad location | `404` | Pass |
| Cascade | `POST /api/cascade/simulate` | Severity outside `0..1` | `422` validation error | Pass |
| Cascade | `GET /api/cascade/events` | After simulation | `200`, latest `cascade_events` list | Pass |
| Cascade | `POST /api/cascade/clear` | Active incident | `200`, `cleared: true`, incident gains `cleared_at`, recovery state created | Pass |
| Cascade | `POST /api/cascade/clear` | No active incident | `200`, `{"cleared": false, "incident": null}` | Pass |
| Routing | `POST /api/route/equilibrium` | Valid OD/users | `200`, naive route at 100 percent, secondary jam in 18 min, Wardrop split across routes, 14 min summary | Pass, multiple Wardrop routes returned |
| Routing | `POST /api/route/equilibrium` | Unknown origin | `404` | Pass |
| Routing | `POST /api/route/equilibrium` | Unknown destination | `404` | Pass |
| Routing | `POST /api/route/equilibrium` | `users <= 0` | `422` | Pass |
| Alerts | `GET /api/alerts/live` | Baseline and after actions | `200`, alert feed includes pre-transition, phantom, cascade, recovery, emergency families when triggered | Pass, all 5 alert families asserted |
| Emergency | `POST /api/emergency/route` | Valid emergency request | `200`, green corridor route, emergency signal preemption, emergency alert | Pass, N approach gets 60 seconds and other approaches 0 |
| Emergency | `POST /api/emergency/route` | Unknown origin/destination | `404` | Pass |
| Signals | `GET /api/signals/{intersection}` | Valid intersection | `200`, Webster adaptive timings with cycle 90 and N/S/E/W green seconds bounded 10 to 60 | Pass |
| Signals | `GET /api/signals/{bad_intersection}` | Unknown intersection | `404` | Pass |
| Chatbot | `POST /api/chat/` | No Anthropic key | `200`, offline demo response using live hotspot context | Pass |
| WebSocket | `WS /ws/live` | Connect and receive first message | JSON state with 16 locations and alerts | Pass |

## Engine And Feature Matrix

| Module | Paths tested | Expected behavior | Current result |
|---|---|---|---|
| `graph.locations` | `LOCATIONS`, `as_geojson_points()` | Exactly 16 NCR monitoring points with coordinates and criticality | Pass |
| `graph.network` | `build_demo_graph()`, `monitoring_node_ids()`, `precompute_route_cache()`, `haversine_km()` | Graph contains 16 nodes, route cache has pairwise travel times, distances positive | Pass |
| `graph.cascade` | `simulate_cascade()` | Direct source event at T+0, ordered propagated events, severities in `0..1`, respects horizon | Pass |
| `graph.routing` | `wardrop_route()`, `bpr_travel_time()`, `route_name()` | Splits users across candidate routes, higher flow increases BPR travel time, unknown nodes return empty list | Pass |
| `graph.signal_optimizer` | `optimize_signal()` | Adaptive Webster mode and emergency preemption mode | Pass |
| `graph.criticality` | `network_criticality()` | Connaught Place ranks as top critical node | Pass |
| `insights.phase_transition` | `compute_instability()`, `check_phase_transition()` | Stable, pre-transition, low-speed jammed, high-probability jammed paths | Pass |
| `insights.hysteresis` | `recovery_eta()` | No incident, active recovery, completed recovery paths | Pass |
| `insights.phantom_jams` | `detect_phantom_jam()` | Positive oscillation/no-cause detection and negative accident/short/stable paths | Pass |
| `ml.feature_engineering` | `normalize_columns()`, `build_features()` | Alias columns normalized, all feature columns produced, required-column errors raised | Pass |
| `ml.predict` | `heuristic_prediction()`, `predict_congestion()` | Low and very-high heuristic paths plus batch prediction path | Pass |
| `ml.train` | `train_model(n_estimators=5)` on small Excel fixture | Reads Excel, builds features, trains XGBoost, writes model and temporal split CSVs | Pass |
| `simulator.synthetic_state` | `level_from_load()`, `generate_live_state()` | 16 live nodes, DND phase warning, Akshardham phantom jam | Pass |
| `simulator.injector` | `inject_phantom()` | Returns Akshardham phantom speed history | Pass |
| `simulator.demo_scenarios` | `cascade_demo()`, `five_insight_demo()` | Scripted five-insight payload available for demo | Pass |
| `api.state` | `get_full_state()`, `inject_incident()`, `clear_incident()`, `register_emergency_alert()` via APIs and direct tests | State mutates correctly for incident, recovery, cascade, emergency alerts | Pass |

## Objective Coverage Checks

| Objective or feature | Backend proof |
|---|---|
| Predict congestion 30 to 60 min ahead | `/api/predict/{location}` returns `forecast_60_min`; ML feature and train paths pass |
| Identify high-risk zones | `network_criticality()` ranks monitored nodes; state exposes criticality per location |
| Suggest alternative routes | `/api/route/equilibrium` returns Wardrop split and naive comparison |
| Optimize signal timing | `/api/signals/{intersection}` and emergency route signal preemption pass |
| Real-time alerts | `/api/alerts/live` and `/ws/live` pass, including five alert families after triggers |
| Traffic heatmap feed | `/api/state` exposes 16 nodes with coordinates, congestion, speed, volume, load |
| AI prediction dashboard feed | `/api/state` and `/api/predict/{location}` expose phase, phantom, forecast, probabilities |
| Emergency vehicle priority route | `/api/emergency/route` returns route, green corridor, signal preemption |
| AI chatbot | `/api/chat/` passes offline live-context mode; Anthropic import is top-level and available |

## Current Known Backend Boundaries

- The local machine is Python 3.14, so `.venv` uses current compatible package versions. `requirements.txt` still reflects the Python 3.11 hackathon stack from the master plan.
- OSMnx is installed, but the tested graph is the deterministic 16-node Delhi-NCR demo graph so backend tests do not depend on live OpenStreetMap network availability.
- Anthropic live mode requires `ANTHROPIC_API_KEY`; offline demo mode is tested and stable.

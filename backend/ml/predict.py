from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

from .feature_engineering import CONG_LABELS, FEATURE_COLS, build_features


MODEL_PATH = Path(__file__).resolve().parent / "models" / "xgb_traffic.json"


def heuristic_prediction(row: dict) -> dict:
    speed = float(row.get("Avg Speed (km/h)", row.get("speed", 35)))
    volume = float(row.get("Traffic Volume", row.get("volume", 1100)))
    instability = float(row.get("instability_index", 0.25))
    accident = str(row.get("Accident", row.get("accident", "No"))).lower() in {"yes", "true", "1"}
    score = (volume / 2200) + max(0, (45 - speed) / 45) + instability * 0.7 + (0.25 if accident else 0)
    if score > 1.45:
        label = "Very High"
    elif score > 1.05:
        label = "High"
    elif score > 0.62:
        label = "Medium"
    else:
        label = "Low"
    idx = CONG_LABELS.index(label)
    probs = np.full(4, 0.08)
    probs[idx] = 0.76
    probs = probs / probs.sum()
    return {"label": label, "probabilities": dict(zip(CONG_LABELS, probs.round(3).tolist())), "model": "heuristic"}


def predict_congestion(records: list[dict]) -> list[dict]:
    df = pd.DataFrame(records)
    if not MODEL_PATH.exists() or len(df) < 4:
        return [heuristic_prediction(row) for row in df.to_dict(orient="records")]

    featured, _ = build_features(df)
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    probs = model.predict_proba(featured[FEATURE_COLS])
    results = []
    for prob in probs:
        label = CONG_LABELS[int(np.argmax(prob))]
        results.append({"label": label, "probabilities": dict(zip(CONG_LABELS, prob.round(3).tolist())), "model": "xgboost"})
    return results

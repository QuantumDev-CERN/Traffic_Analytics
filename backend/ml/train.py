from __future__ import annotations

from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report

from .feature_engineering import CONG_LABELS, FEATURE_COLS, build_features

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "raw" / "TrafficCongestion_MultiLocation_7000Rows.xlsx"
MODEL_PATH = ROOT / "ml" / "models" / "xgb_traffic.json"
TRAIN_PATH = ROOT / "data" / "processed" / "features_train.csv"
TEST_PATH = ROOT / "data" / "processed" / "features_test.csv"


def train_model(n_estimators: int = 300) -> dict:
    df_raw = pd.read_excel(DATASET)
    df, _ = build_features(df_raw)
    split_at = df["Timestamp"].quantile(0.75)
    train = df[df["Timestamp"] < split_at]
    test = df[df["Timestamp"] >= split_at]

    x_train, y_train = train[FEATURE_COLS], train["target"]
    x_test, y_test = test[FEATURE_COLS], test["target"]

    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob",
        num_class=4,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=False)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(MODEL_PATH)
    TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(TRAIN_PATH, index=False)
    test.to_csv(TEST_PATH, index=False)

    preds = model.predict(x_test)
    report = classification_report(
        y_test,
        preds,
        labels=[0, 1, 2, 3],
        target_names=CONG_LABELS,
        output_dict=True,
        zero_division=0,
    )
    return {"split_at": str(split_at), "rows": len(df), "accuracy": report["accuracy"], "report": report}


if __name__ == "__main__":
    print(train_model())

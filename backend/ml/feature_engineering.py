from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

FEATURE_COLS = [
    "Traffic Volume",
    "Avg Speed (km/h)",
    "Rain(mm)",
    "Public Transport Density",
    "speed_roll_std",
    "speed_roll_mean",
    "vol_roll_mean",
    "instability_index",
    "speed_delta",
    "speed_accel",
    "cong_lag_1",
    "cong_lag_2",
    "cong_lag_3",
    "congestion_memory",
    "was_high_recently",
    "periods_since_high",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "is_rush_hour",
    "is_weekend",
    "is_night",
    "weather_severity",
    "accident_flag",
    "event_flag",
    "location_enc",
]

CONG_MAP = {"Low": 0, "Medium": 1, "High": 2, "Very High": 3}
CONG_LABELS = ["Low", "Medium", "High", "Very High"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "DateTime": "Timestamp",
        "Time": "Timestamp",
        "TrafficVolume": "Traffic Volume",
        "Vehicle Count": "Traffic Volume",
        "Average Speed": "Avg Speed (km/h)",
        "Avg Speed": "Avg Speed (km/h)",
        "Rain": "Rain(mm)",
        "PublicTransportDensity": "Public Transport Density",
        "Congestion": "Congestion Level",
    }
    df = df.rename(columns={col: aliases.get(col, col) for col in df.columns})
    defaults = {
        "Rain(mm)": 0.0,
        "Public Transport Density": 0.5,
        "Weather": "Clear",
        "Accident": "No",
        "Event": "No",
    }
    for col, value in defaults.items():
        if col not in df:
            df[col] = value
    return df


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, LabelEncoder]:
    df = normalize_columns(df.copy())
    required = {"Timestamp", "Location", "Traffic Volume", "Avg Speed (km/h)", "Congestion Level"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values(["Location", "Timestamp"]).reset_index(drop=True)
    df["target"] = df["Congestion Level"].map(CONG_MAP)

    for loc in df["Location"].unique():
        mask = df["Location"] == loc
        sub = df.loc[mask].copy()
        df.loc[mask, "speed_roll_std"] = sub["Avg Speed (km/h)"].rolling(3, min_periods=2).std()
        df.loc[mask, "speed_roll_mean"] = sub["Avg Speed (km/h)"].rolling(3, min_periods=1).mean()
        df.loc[mask, "vol_roll_mean"] = sub["Traffic Volume"].rolling(3, min_periods=1).mean()
        df.loc[mask, "instability_index"] = (
            df.loc[mask, "speed_roll_std"] / (df.loc[mask, "speed_roll_mean"] + 1e-6)
        )
        df.loc[mask, "speed_delta"] = sub["Avg Speed (km/h)"].diff()
        df.loc[mask, "speed_accel"] = sub["Avg Speed (km/h)"].diff().diff()
        df.loc[mask, "cong_lag_1"] = sub["target"].shift(1)
        df.loc[mask, "cong_lag_2"] = sub["target"].shift(2)
        df.loc[mask, "cong_lag_3"] = sub["target"].shift(3)

        targets = sub["target"].fillna(0).to_numpy()
        memory = np.zeros(len(targets))
        for i in range(1, len(targets)):
            memory[i] = 0.6 * targets[i - 1] + 0.4 * memory[i - 1]
        df.loc[mask, "congestion_memory"] = memory
        df.loc[mask, "was_high_recently"] = sub["target"].shift(1).ge(2).astype(int)
        high_flags = sub["target"].ge(2).astype(int).to_numpy()
        periods = []
        count = 99
        for flag in high_flags:
            count = 0 if flag else count + 1
            periods.append(count)
        df.loc[mask, "periods_since_high"] = periods

    hour = df["Timestamp"].dt.hour
    dow = df["Timestamp"].dt.dayofweek
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    df["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    df["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    df["is_rush_hour"] = hour.isin([7, 8, 9, 17, 18, 19, 20]).astype(int)
    df["is_weekend"] = dow.isin([5, 6]).astype(int)
    df["is_night"] = hour.isin([22, 23, 0, 1, 2, 3, 4]).astype(int)

    weather_map = {"Clear": 0, "Cloudy": 1, "Fog": 2, "Rain": 3, "Heavy Rain": 4}
    df["weather_severity"] = df["Weather"].map(weather_map).fillna(0)
    df["accident_flag"] = df["Accident"].astype(str).str.lower().isin(["yes", "true", "1"]).astype(int)
    df["event_flag"] = df["Event"].astype(str).str.lower().isin(["yes", "true", "1"]).astype(int)

    le = LabelEncoder()
    df["location_enc"] = le.fit_transform(df["Location"])
    df = df.dropna(subset=["speed_roll_std", "speed_delta", "cong_lag_1", "cong_lag_2", "cong_lag_3"])
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(0)
    return df, le

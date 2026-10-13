import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.db.models import SessionLocal
from src.db.water_models import WaterFlow

MODEL_PATH = Path("models/water_flow.pkl")
MODEL_PATH.parent.mkdir(exist_ok=True)


def load_data(station_id: int = 1) -> pd.DataFrame:
    session = SessionLocal()
    rows = (
        session.query(WaterFlow)
        .filter(WaterFlow.station_id == station_id)
        .order_by(WaterFlow.timestamp)
        .all()
    )
    session.close()
    df = pd.DataFrame([
        {
            "timestamp": m.timestamp,
            "flow_m3s": m.flow_m3s,
            "level_m": m.level_m,
            "precipitation": m.precipitation,
            "temperature": m.temperature,
        }
        for m in rows
    ])
    return df


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    df["lag_1"] = df["flow_m3s"].shift(1)
    df["lag_2"] = df["flow_m3s"].shift(2)
    df["lag_4"] = df["flow_m3s"].shift(4)
    df = df.dropna()
    return df


def train(station_id: int = 1):
    df = load_data(station_id)
    df = make_features(df)

    features = ["hour", "day_of_year", "lag_1", "lag_2", "lag_4",
                "precipitation", "temperature"]
    target = "flow_m3s"

    split = int(len(df) * 0.8)
    X_train, X_test = df[features][:split], df[features][split:]
    y_train, y_test = df[target][:split], df[target][split:]

    model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Сохранено: {MODEL_PATH}")


def predict(station_id: int = 1, days: int = 7) -> list:
    model = joblib.load(MODEL_PATH)
    df = load_data(station_id)
    df = make_features(df)

    features = ["hour", "day_of_year", "lag_1", "lag_2", "lag_4",
                "precipitation", "temperature"]

    last = df[features].iloc[-1:].copy()
    predictions = []
    for d in range(days):
        p = float(model.predict(last)[0])
        predictions.append(round(p, 2))
        last["lag_4"] = last["lag_2"]
        last["lag_2"] = last["lag_1"]
        last["lag_1"] = p
        last["hour"] = (last["hour"].values[0] + 24) % 24
        last["day_of_year"] = (last["day_of_year"].values[0] + 1) % 365

    return predictions


if __name__ == "__main__":
    train(station_id=1)
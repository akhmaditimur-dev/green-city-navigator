import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.db.models import SessionLocal, Measurement

MODEL_PATH = Path("models/air_quality.pkl")
MODEL_PATH.parent.mkdir(exist_ok=True)


def load_data(station_id: int = 1) -> pd.DataFrame:
    session = SessionLocal()
    rows = (
        session.query(Measurement)
        .filter(Measurement.station_id == station_id)
        .order_by(Measurement.timestamp)
        .all()
    )
    session.close()

    df = pd.DataFrame([
        {
            "timestamp": m.timestamp,
            "pm25": m.pm25,
            "pm10": m.pm10,
            "temperature": m.temperature,
            "humidity": m.humidity,
            "wind_speed": m.wind_speed,
        }
        for m in rows
    ])
    return df


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    df["lag_1"] = df["pm25"].shift(1)
    df["lag_3"] = df["pm25"].shift(3)
    df["lag_8"] = df["pm25"].shift(8)
    df["lag_24"] = df["pm25"].shift(24)
    df = df.dropna()
    return df


def train(station_id: int = 1):
    df = load_data(station_id)
    df = make_features(df)

    features = [
        "hour", "day_of_year",
        "lag_1", "lag_3", "lag_8", "lag_24",
        "temperature", "humidity", "wind_speed",
    ]
    target = "pm25"

    split = int(len(df) * 0.8)
    X_train, X_test = df[features][:split], df[features][split:]
    y_train, y_test = df[target][:split], df[target][split:]

    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        objective="reg:squarederror",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Модель сохранена: {MODEL_PATH}")

    return model


def predict(station_id: int = 1, hours: int = 24):
    model = joblib.load(MODEL_PATH)
    df = load_data(station_id)
    df = make_features(df)

    features = [
        "hour", "day_of_year",
        "lag_1", "lag_3", "lag_8", "lag_24",
        "temperature", "humidity", "wind_speed",
    ]

    last = df[features].iloc[-1:].copy()
    predictions = []
    for h in range(hours):
        p = float(model.predict(last)[0])
        predictions.append(round(p, 2))
        last["lag_24"] = last["lag_8"]
        last["lag_8"] = last["lag_3"]
        last["lag_3"] = last["lag_1"]
        last["lag_1"] = p
        last["hour"] = (last["hour"].values[0] + 1) % 24

    return predictions


if __name__ == "__main__":
    train(station_id=1)
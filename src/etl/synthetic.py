import random
import math
from datetime import datetime, timedelta
from src.db.models import SessionLocal, Station, Measurement, init_db


HUJAND_STATIONS = [
    {"name": "Худжанд-Центр",  "lat": 40.2833, "lon": 69.6333},
    {"name": "Худжанд-Север",  "lat": 40.3000, "lon": 69.6400},
    {"name": "Худжанд-Юг",     "lat": 40.2650, "lon": 69.6200},
    {"name": "Худжанд-Восток", "lat": 40.2850, "lon": 69.6600},
    {"name": "Худжанд-Запад",  "lat": 40.2800, "lon": 69.6100},
]


def generate_pm25(day_of_year: int, hour: int, station_idx: int) -> float:
    """Синтетический PM2.5 с сезонностью (зима выше) и суточным ходом."""
    # сезонность: максимум зимой (декабрь-январь)
    seasonal = 60 + 60 * math.cos(2 * math.pi * (day_of_year - 15) / 365)
    # суточный ход: утро и вечер выше
    daily = 20 * math.sin(2 * math.pi * (hour - 6) / 24)
    # разброс по станциям
    station_offset = station_idx * 5
    # шум
    noise = random.uniform(-10, 10)
    return max(5, seasonal + daily + station_offset + noise)


def load_synthetic_data(days: int = 365):
    init_db()
    session = SessionLocal()

    # станции
    for s in HUJAND_STATIONS:
        exists = session.query(Station).filter_by(name=s["name"]).first()
        if not exists:
            session.add(Station(**s))
    session.commit()

    stations = session.query(Station).all()
    print(f"Станций: {len(stations)}")

    # измерения
    start = datetime.utcnow() - timedelta(days=days)
    total = 0

    for day in range(days):
        for hour in range(0, 24, 3):  # каждые 3 часа
            ts = start + timedelta(days=day, hours=hour)
            for idx, st in enumerate(stations):
                pm25 = generate_pm25(ts.timetuple().tm_yday, hour, idx)
                m = Measurement(
                    station_id=st.id,
                    timestamp=ts,
                    pm25=round(pm25, 2),
                    pm10=round(pm25 * 1.5, 2),
                    temperature=round(random.uniform(-5, 35), 1),
                    humidity=round(random.uniform(30, 90), 1),
                    wind_speed=round(random.uniform(0, 8), 1),
                )
                session.add(m)
                total += 1

    session.commit()
    session.close()
    print(f"Загружено измерений: {total}")


if __name__ == "__main__":
    load_synthetic_data()
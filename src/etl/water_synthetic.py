import random
import math
from datetime import datetime, timedelta
from src.db.models import SessionLocal, init_db
from src.db.water_models import RiverStation, WaterFlow, FloodRisk


HUJAND_RIVERS = [
    {"name": "Сырдарья-Худжанд", "river": "Сырдарья", "lat": 40.2833, "lon": 69.6333},
    {"name": "Сырдарья-Кайраккум", "river": "Сырдарья", "lat": 40.3200, "lon": 69.7000},
]

ISFARA_RIVERS = [
    {"name": "Исфара-Центр", "river": "Исфара", "lat": 40.1250, "lon": 70.6250},
    {"name": "Исфара-Верхний", "river": "Исфара", "lat": 40.1500, "lon": 70.6000},
    {"name": "Сохи-Исфара", "river": "Исфара", "lat": 40.1000, "lon": 70.6500},
]

DISTRICTS = [
    {"name": "Исфара-Центр", "lat": 40.1250, "lon": 70.6250},
    {"name": "Нау", "lat": 40.1500, "lon": 70.6500},
    {"name": "Ворух", "lat": 40.1000, "lon": 70.6000},
    {"name": "Худжанд-Центр", "lat": 40.2833, "lon": 69.6333},
]


def generate_flow(day_of_year: int, station_idx: int) -> float:
    # максимум — весной и летом (таяние ледников)
    seasonal = 50 + 40 * math.sin(2 * math.pi * (day_of_year - 90) / 365)
    noise = random.uniform(-10, 10)
    return max(5, seasonal + noise + station_idx * 5)


def generate_risk(district_idx: int) -> float:
    base = 30 + district_idx * 15
    noise = random.uniform(-15, 15)
    return max(0, min(100, base + noise))


def load_water_data(days: int = 365):
    init_db()

    from src.db.models import engine
    from src.db.water_models import Base as WaterBase
    WaterBase.metadata.create_all(engine)

    session = SessionLocal()

    # станции
    all_rivers = HUJAND_RIVERS + ISFARA_RIVERS
    for s in all_rivers:
        if not session.query(RiverStation).filter_by(name=s["name"]).first():
            session.add(RiverStation(**s))
    session.commit()

    stations = session.query(RiverStation).all()
    print(f"Речных станций: {len(stations)}")

    # расход воды
    start = datetime.utcnow() - timedelta(days=days)
    total = 0
    for day in range(days):
        for hour in [0, 6, 12, 18]:
            ts = start + timedelta(days=day, hours=hour)
            for idx, st in enumerate(stations):
                flow = generate_flow(ts.timetuple().tm_yday, idx)
                wf = WaterFlow(
                    station_id=st.id,
                    timestamp=ts,
                    flow_m3s=round(flow, 2),
                    level_m=round(flow / 20, 2),
                    precipitation=round(random.uniform(0, 15), 1),
                    temperature=round(random.uniform(-5, 35), 1),
                )
                session.add(wf)
                total += 1

    session.commit()
    print(f"Записей о расходе: {total}")

    # риск паводков
    for day in range(days):
        ts = start + timedelta(days=day)
        for idx, d in enumerate(DISTRICTS):
            risk = generate_risk(idx)
            cat = "low"
            if risk > 75: cat = "critical"
            elif risk > 50: cat = "high"
            elif risk > 30: cat = "medium"
            fr = FloodRisk(
                district=d["name"],
                timestamp=ts,
                risk_score=round(risk, 1),
                category=cat,
                lat=d["lat"],
                lon=d["lon"],
            )
            session.add(fr)

    session.commit()
    session.close()
    print("Данные по воде загружены")


if __name__ == "__main__":
    load_water_data()
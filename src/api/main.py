from fastapi import FastAPI, HTTPException
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from src.db.models import SessionLocal, Station, Measurement

from src.auth.init_admins import init_superadmins
from src.auth.routes import router as auth_router

app = FastAPI(title="Green City Navigator")

# При старте — инициализация супер-админов
@app.on_event("startup")
def startup_event():
    init_superadmins()

app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "ok", "city": "Худжанд"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/stations")
def get_stations():
    session = SessionLocal()
    stations = session.query(Station).all()
    result = [
        {"id": s.id, "name": s.name, "lat": s.lat, "lon": s.lon}
        for s in stations
    ]
    session.close()
    return result


@app.get("/measurements/{station_id}")
def get_measurements(station_id: int, days: int = 7):
    session = SessionLocal()
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        session.query(Measurement)
        .filter(Measurement.station_id == station_id)
        .filter(Measurement.timestamp >= since)
        .order_by(Measurement.timestamp)
        .all()
    )
    result = [
        {
            "timestamp": m.timestamp.isoformat(),
            "pm25": m.pm25,
            "pm10": m.pm10,
            "temperature": m.temperature,
            "humidity": m.humidity,
            "wind_speed": m.wind_speed,
        }
        for m in rows
    ]
    session.close()
    return result


@app.get("/current/{station_id}")
def get_current(station_id: int):
    session = SessionLocal()
    m = (
        session.query(Measurement)
        .filter(Measurement.station_id == station_id)
        .order_by(Measurement.timestamp.desc())
        .first()
    )
    session.close()
    if not m:
        raise HTTPException(404, "Нет данных")
    return {
        "station_id": station_id,
        "timestamp": m.timestamp.isoformat(),
        "pm25": m.pm25,
        "aqi": int(m.pm25 * 2) if m.pm25 else None,
    }

from src.models.air_quality import predict as predict_pm25


@app.get("/forecast/{station_id}")
def get_forecast(station_id: int, hours: int = 24):
    try:
        values = predict_pm25(station_id=station_id, hours=hours)
        return {
            "station_id": station_id,
            "hours": hours,
            "forecast": [
                {"hour": i + 1, "pm25": v}
                for i, v in enumerate(values)
            ],
        }
    except FileNotFoundError:
        raise HTTPException(503, "Модель не обучена")

    
from src.db.water_models import RiverStation, WaterFlow, FloodRisk


@app.get("/water/stations")
def get_water_stations():
    session = SessionLocal()
    rows = session.query(RiverStation).all()
    result = [
        {"id": s.id, "name": s.name, "river": s.river, "lat": s.lat, "lon": s.lon}
        for s in rows
    ]
    session.close()
    return result


@app.get("/water/flow/{station_id}")
def get_water_flow(station_id: int, days: int = 7):
    session = SessionLocal()
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        session.query(WaterFlow)
        .filter(WaterFlow.station_id == station_id)
        .filter(WaterFlow.timestamp >= since)
        .order_by(WaterFlow.timestamp)
        .all()
    )
    result = [
        {
            "timestamp": m.timestamp.isoformat(),
            "flow_m3s": m.flow_m3s,
            "level_m": m.level_m,
            "precipitation": m.precipitation,
            "temperature": m.temperature,
        }
        for m in rows
    ]
    session.close()
    return result


@app.get("/water/current/{station_id}")
def get_water_current(station_id: int):
    session = SessionLocal()
    m = (
        session.query(WaterFlow)
        .filter(WaterFlow.station_id == station_id)
        .order_by(WaterFlow.timestamp.desc())
        .first()
    )
    session.close()
    if not m:
        raise HTTPException(404, "Нет данных")
    return {
        "station_id": station_id,
        "timestamp": m.timestamp.isoformat(),
        "flow_m3s": m.flow_m3s,
        "level_m": m.level_m,
    }


@app.get("/flood/risk")
def get_flood_risk():
    session = SessionLocal()
    # последняя дата
    latest = session.query(FloodRisk).order_by(FloodRisk.timestamp.desc()).first()
    if not latest:
        session.close()
        return []

    day_start = latest.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = (
        session.query(FloodRisk)
        .filter(FloodRisk.timestamp >= day_start)
        .all()
    )
    result = [
        {
            "district": r.district,
            "risk_score": r.risk_score,
            "category": r.category,
            "lat": r.lat,
            "lon": r.lon,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]
    session.close()
    return result


from src.db.water_models import Report
from pydantic import BaseModel


class ReportCreate(BaseModel):
    name: str | None = None
    category: str
    description: str
    photo_url: str | None = None
    lat: float | None = None
    lon: float | None = None


@app.post("/reports")
def create_report(report: ReportCreate):
    session = SessionLocal()
    r = Report(
        name=report.name,
        category=report.category,
        description=report.description,
        photo_url=report.photo_url,
        lat=report.lat,
        lon=report.lon,
        status="new",
    )
    session.add(r)
    session.commit()
    result = {"id": r.id, "status": r.status}
    session.close()
    return result


@app.get("/reports")
def list_reports():
    session = SessionLocal()
    rows = session.query(Report).order_by(Report.created_at.desc()).all()
    result = [
        {
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "description": r.description,
            "photo_url": r.photo_url,
            "lat": r.lat,
            "lon": r.lon,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
    session.close()
    return result
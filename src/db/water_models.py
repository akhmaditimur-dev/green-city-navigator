from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from src.db.models import Base


class RiverStation(Base):
    __tablename__ = "river_stations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    river = Column(String(100))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)


class WaterFlow(Base):
    __tablename__ = "water_flows"

    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    flow_m3s = Column(Float)        # расход, м³/с
    level_m = Column(Float)         # уровень, м
    precipitation = Column(Float)   # осадки, мм
    temperature = Column(Float)     # температура


class FloodRisk(Base):
    __tablename__ = "flood_risk"

    id = Column(Integer, primary_key=True)
    district = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    risk_score = Column(Float)      # 0-100
    category = Column(String(20))   # low/medium/high/critical
    lat = Column(Float)
    lon = Column(Float)
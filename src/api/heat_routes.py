from fastapi import APIRouter, HTTPException
from pathlib import Path
import numpy as np
import rioxarray

router = APIRouter(prefix="/heat", tags=["heat"])

HEAT_DIR = Path("data/raw/heat")


@router.get("/map")
def heat_map():
    """Возвращает карту температур в формате для Plotly."""
    files = sorted(HEAT_DIR.glob("landsat_thermal_*.tif"))
    if not files:
        raise HTTPException(404, "Нет данных о температуре")

    latest = files[-1]
    da = rioxarray.open_rasterio(latest, masked=True).squeeze()

    # Получаем координаты
    lons = da.x.values
    lats = da.y.values
    temps = da.values

    # Понижаем разрешение для передачи (каждая 4-я точка)
    step = 4
    lons_s = lons[::step]
    lats_s = lats[::step]
    temps_s = temps[::step, ::step]

    # Преобразуем в список точек
    points = []
    for i, lat in enumerate(lats_s):
        for j, lon in enumerate(lons_s):
            t = temps_s[i, j]
            if not np.isnan(t):
                points.append({
                    "lat": float(lat),
                    "lon": float(lon),
                    "temp": round(float(t), 1),
                })

    return {
        "date": latest.stem.split("_")[-1],
        "min": float(np.nanmin(temps)),
        "max": float(np.nanmax(temps)),
        "mean": float(np.nanmean(temps)),
        "points": points,
    }


@router.get("/stats")
def heat_stats():
    """Статистика по последнему снимку."""
    files = sorted(HEAT_DIR.glob("landsat_thermal_*.tif"))
    if not files:
        raise HTTPException(404, "Нет данных")

    latest = files[-1]
    da = rioxarray.open_rasterio(latest, masked=True).squeeze()

    temps = da.values
    return {
        "date": latest.stem.split("_")[-1],
        "min": round(float(np.nanmin(temps)), 1),
        "max": round(float(np.nanmax(temps)), 1),
        "mean": round(float(np.nanmean(temps)), 1),
        "std": round(float(np.nanstd(temps)), 1),
        "shape": [int(da.sizes["y"]), int(da.sizes["x"])],
    }
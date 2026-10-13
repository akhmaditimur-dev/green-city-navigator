import cdsapi
from pathlib import Path

OUTPUT_DIR = Path("data/raw/era5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Худжанд: 40.2-40.4 N, 69.5-69.8 E
AREA = [40.4, 69.5, 40.2, 69.8]  # N, W, S, E
YEAR = "2024"
MONTHS = [f"{m:02d}" for m in range(1, 13)]
DAYS = [f"{d:02d}" for d in range(1, 32)]
HOURS = ["00:00", "06:00", "12:00", "18:00"]


def download_era5():
    client = cdsapi.Client()
    output = OUTPUT_DIR / f"era5_hujand_{YEAR}.nc"

    print(f"Скачиваем ERA5 за {YEAR}...")
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "2m_temperature",
                "2m_dewpoint_temperature",
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "surface_pressure",
                "total_precipitation",
            ],
            "year": YEAR,
            "month": MONTHS,
            "day": DAYS,
            "time": HOURS,
            "area": AREA,
            "format": "netcdf",
        },
        str(output),
    )
    print(f"Сохранено: {output}")


if __name__ == "__main__":
    download_era5()
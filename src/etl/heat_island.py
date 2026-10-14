"""Скачивание Landsat thermal для острова тепла."""
from pathlib import Path
from datetime import datetime, timedelta

import rioxarray
import planetary_computer
import pystac_client

OUTPUT_DIR = Path("data/raw/heat")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HUJAND_BBOX = [69.5, 40.2, 69.8, 40.4]
END_DATE = datetime.utcnow()
START_DATE = END_DATE - timedelta(days=180)


def search_landsat(bbox, start, end):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    search = catalog.search(
        collections=["landsat-c2-l2"],
        bbox=bbox,
        datetime=f"{start.isoformat()}/{end.isoformat()}",
        query={"eo:cloud_cover": {"lt": 10}},
    )
    items = list(search.items())
    print(f"Найдено снимков Landsat: {len(items)}")
    return items


def load_landsat_thermal(item):
    asset = item.assets.get("lwir11")
    if not asset:
        return None
    da = rioxarray.open_rasterio(
        asset.href,
        masked=True,
        chunks={"x": 512, "y": 512},
    )
    temp_c = da * 0.00341802 + 149.0 - 273.15
    temp_c.name = "temperature"
    return temp_c.squeeze()


def main():
    print("=== Landsat (температура) ===")
    items = search_landsat(HUJAND_BBOX, START_DATE, END_DATE)

    if not items:
        print("Нет снимков")
        return

    latest = sorted(items, key=lambda x: x.datetime, reverse=True)[0]
    print(f"Самый свежий: {latest.id} ({latest.datetime})")

    temp = load_landsat_thermal(latest)
    if temp is None:
        print("Не удалось загрузить тепловой канал")
        return

    # Уменьшаем разрешение (усредняем 10x10 пикселей)
    temp_small = temp.coarsen(x=10, y=10, boundary="trim").mean()

    # Перепроецируем в WGS84 (градусы)
    temp_wgs = temp_small.rio.reproject("EPSG:4326")

    output = OUTPUT_DIR / f"landsat_thermal_{latest.datetime.date()}.tif"
    temp_wgs.rio.to_raster(output)

    # Статистика
    t_min = float(temp_wgs.min())
    t_max = float(temp_wgs.max())
    t_mean = float(temp_wgs.mean())

    print(f"Сохранено: {output}")
    print(f"Температура: min={t_min:.1f}°C, max={t_max:.1f}°C, mean={t_mean:.1f}°C")
    print(f"Размер файла: {output.stat().st_size / 1024 / 1024:.1f} МБ")
    print("\n✓ Готово")


if __name__ == "__main__":
    main()
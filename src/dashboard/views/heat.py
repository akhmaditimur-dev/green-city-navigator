import streamlit as st
import requests
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import header, footer, COLORS, recommendation
from i18n import get_lang

API = "http://api:8000"

header(lang=get_lang())

st.markdown("# Остров тепла")
st.caption("Температура поверхности города по спутниковым данным Landsat")

# --- Данные ---
try:
    stats = requests.get(f"{API}/heat/stats", timeout=10).json()
    map_data = requests.get(f"{API}/heat/map", timeout=30).json()
except Exception as e:
    st.error(f"Ошибка загрузки: {e}")
    st.stop()

st.caption(f"Снимок от **{stats['date']}**")

# --- Метрики ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Мин.", f"{stats['min']}°C")
with col2:
    st.metric("Макс.", f"{stats['max']}°C")
with col3:
    st.metric("Среднее", f"{stats['mean']}°C")
with col4:
    st.metric("Разброс", f"{stats['std']}°C")

# --- Рекомендация ---
delta = stats["max"] - stats["min"]
if delta > 30:
    recommendation(
        f"Разница температур {delta:.0f}°C — сильный остров тепла. "
        "Рекомендуется озеленение горячих точек.",
        "danger",
    )
elif delta > 20:
    recommendation(f"Разница {delta:.0f}°C. Умеренный остров тепла.", "warning")
else:
    recommendation(f"Разница {delta:.0f}°C. Ситуация стабильная.", "info")

# --- Карта ---
st.markdown("## Карта температур")

df = pd.DataFrame(map_data["points"])

# Обрезаем только Худжандом
df = df[
    (df["lat"] >= 40.25) & (df["lat"] <= 40.33) &
    (df["lon"] >= 69.55) & (df["lon"] <= 69.72)
].copy()

st.caption(f"Точек в границах Худжанда: {len(df)}")

if not df.empty:
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="temp",
        color_continuous_scale="RdYlBu_r",
        range_color=[stats["min"], stats["max"]],
        size_max=18,
        zoom=13,
        height=650,
        center={"lat": 40.2833, "lon": 69.6333},
        opacity=0.8,
    )
    fig.update_traces(marker=dict(size=14))
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="°C"),
        mapbox=dict(
            center=dict(lat=40.2833, lon=69.6333),
            zoom=13,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Топ горячих ---
st.markdown("## Самые горячие точки")
hot = df.nlargest(10, "temp")[["lat", "lon", "temp"]].copy()
hot.columns = ["Широта", "Долгота", "Температура (°C)"]
st.dataframe(hot, use_container_width=True, hide_index=True)

# --- Топ холодных ---
st.markdown("## Самые холодные точки")
cold = df.nsmallest(10, "temp")[["lat", "lon", "temp"]].copy()
cold.columns = ["Широта", "Долгота", "Температура (°C)"]
st.dataframe(cold, use_container_width=True, hide_index=True)

footer(lang=get_lang())
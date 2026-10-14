import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer, recommendation, AQI_COLORS
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

st.set_page_config(page_title="Воздух — Green City Navigator", page_icon="💨", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

st.title(f"💨 {t('air_title')}")

# --- Данные ---
try:
    stations = requests.get(f"{API}/stations", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка подключения к API: {e}")
    st.stop()

if not stations:
    st.warning("Нет станций")
    st.stop()

# --- Карта ---
st.subheader(t("air_map"))

map_df = pd.DataFrame([
    {
        "name": s["name"],
        "lat": s["lat"],
        "lon": s["lon"],
        "pm25": requests.get(f"{API}/current/{s['id']}", timeout=3).json()["pm25"],
    }
    for s in stations
])

fig_map = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    size="pm25",
    color="pm25",
    hover_name="name",
    color_continuous_scale="RdYlGn_r",
    zoom=12,
    height=450,
)
fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_map, use_container_width=True)

# --- Текущие значения ---
st.subheader(t("air_current"))

cols = st.columns(len(stations))
for i, s in enumerate(stations):
    cur = requests.get(f"{API}/current/{s['id']}", timeout=3).json()
    with cols[i]:
        st.metric(s["name"], f"{cur['pm25']:.1f}", f"AQI {cur['aqi']}")

# --- Рекомендация ---
avg_pm = map_df["pm25"].mean()
if avg_pm < 35:
    recommendation(t("rec_air_good"), "info")
elif avg_pm < 75:
    recommendation(t("rec_air_moderate"), "warning")
else:
    recommendation(t("rec_air_bad"), "danger")

# --- История ---
st.subheader(t("air_history"))

col1, col2 = st.columns([3, 1])
with col2:
    days = st.selectbox(t("air_select_period"), [7, 30], format_func=lambda x: t(f"days_{x}"))

station_id = st.selectbox(
    t("air_station"),
    options=[s["id"] for s in stations],
    format_func=lambda x: next(s["name"] for s in stations if s["id"] == x),
)

data = requests.get(f"{API}/measurements/{station_id}?days={days}", timeout=5).json()
if data:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    fig = px.line(df, x="timestamp", y="pm25", labels={"pm25": "PM2.5, мкг/м³", "timestamp": ""})
    st.plotly_chart(fig, use_container_width=True)

# --- Прогноз ---
st.subheader(t("air_forecast"))

forecast = requests.get(f"{API}/forecast/{station_id}?hours=24", timeout=5).json()
fdf = pd.DataFrame(forecast["forecast"])

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=fdf["hour"], y=fdf["pm25"], mode="lines+markers", name="Прогноз"))
fig2.add_hline(y=35, line_dash="dash", line_color="orange", annotation_text="35")
fig2.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="75")
fig2.update_layout(xaxis_title="Часы", yaxis_title="PM2.5, мкг/м³")
st.plotly_chart(fig2, use_container_width=True)

footer(lang=get_lang())
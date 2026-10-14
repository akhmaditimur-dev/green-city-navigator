import streamlit as st
import requests
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer, recommendation
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

st.set_page_config(page_title="Вода — Green City Navigator", page_icon="💧", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

st.title(f"💧 {t('water_title')}")

# --- Данные ---
stations = requests.get(f"{API}/water/stations", timeout=5).json()
flood = requests.get(f"{API}/flood/risk", timeout=5).json()

if not stations:
    st.warning("Нет речных станций")
    st.stop()

# --- Карта: реки + риск паводков ---
st.subheader(t("water_map"))

if flood:
    flood_df = pd.DataFrame(flood)
    fig_map = px.scatter_mapbox(
        flood_df,
        lat="lat",
        lon="lon",
        size="risk_score",
        color="risk_score",
        hover_name="district",
        color_continuous_scale="RdYlGn_r",
        zoom=11,
        height=450,
        range_color=[0, 100],
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

# --- Текущие значения ---
st.subheader(t("water_current"))

cols = st.columns(len(stations))
for i, ws in enumerate(stations):
    cur = requests.get(f"{API}/water/current/{ws['id']}", timeout=3).json()
    with cols[i]:
        st.metric(ws["name"], f"{cur['flow_m3s']}", f"{cur['level_m']} м")

# --- Рекомендация по риску ---
if flood:
    max_risk = max(r["risk_score"] for r in flood)
    if max_risk > 75:
        recommendation(t("rec_water_critical"), "danger")
    elif max_risk > 50:
        recommendation(t("rec_water_high"), "warning")
    elif max_risk > 30:
        recommendation(t("rec_water_medium"), "info")
    else:
        recommendation(t("rec_water_low"), "info")

# --- История расхода ---
st.subheader(t("water_history"))

river_id = st.selectbox(
    t("water_station"),
    options=[ws["id"] for ws in stations],
    format_func=lambda x: next(ws["name"] for ws in stations if ws["id"] == x),
)

flow_data = requests.get(f"{API}/water/flow/{river_id}?days=7", timeout=5).json()
if flow_data:
    fdf = pd.DataFrame(flow_data)
    fdf["timestamp"] = pd.to_datetime(fdf["timestamp"])
    fig = px.line(fdf, x="timestamp", y="flow_m3s",
                  labels={"flow_m3s": "Расход, м³/с", "timestamp": ""})
    st.plotly_chart(fig, use_container_width=True)

# --- Таблица риска паводков ---
st.subheader(t("water_risk"))

if flood:
    risk_df = pd.DataFrame(flood)[["district", "risk_score", "category"]]
    risk_df.columns = [t("water_district"), "Риск", t("water_category")]
    st.dataframe(risk_df, use_container_width=True, hide_index=True)

footer(lang=get_lang())
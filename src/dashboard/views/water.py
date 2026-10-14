import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer, recommendation, COLORS
from styles_dark import inject_dark_css
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

# st.set_page_config(page_title="Вода — Green City Navigator", page_icon="🌿", layout="wide")

inject_css()
if st.session_state.get("theme") == "dark":
    inject_dark_css()

header(lang=get_lang())

st.markdown("# Водные ресурсы")
st.caption("Реки Сырдарья и Исфара · расход воды и риск паводков")

# --- Данные ---
try:
    stations = requests.get(f"{API}/water/stations", timeout=5).json()
    flood = requests.get(f"{API}/flood/risk", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка API: {e}")
    st.stop()

if not stations:
    st.warning("Нет речных станций")
    st.stop()

# --- Карта риска ---
st.markdown("## Карта риска паводков")

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
    zoom=10,
    height=450,
    range_color=[0, 100],
    size_max=35,
    center={"lat": 40.2833, "lon": 69.6333},  # Худжанд
)
fig_map.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Риск"),
    mapbox=dict(
        center=dict(lat=40.2833, lon=69.6333),
        zoom=9,
    ),
)
st.plotly_chart(fig_map, use_container_width=True)

# --- Функция цвета риска ---
def risk_color(score):
    if score < 30:
        return COLORS["green_dark"], "Низкий"
    elif score < 50:
        return COLORS["warm_dark"], "Средний"
    elif score < 75:
        return COLORS["warning"], "Высокий"
    else:
        return COLORS["danger"], "Критический"

# --- Текущее состояние рек ---
st.markdown("## Расход воды на станциях")

current_water = []
for s in stations:
    try:
        cur = requests.get(f"{API}/water/current/{s['id']}", timeout=3).json()
        current_water.append({
            "id": s["id"],
            "name": s["name"],
            "river": s.get("river", ""),
            "flow": cur["flow_m3s"],
            "level": cur["level_m"],
        })
    except Exception:
        pass

if current_water:
    cols = st.columns(len(current_water))
    for i, w in enumerate(current_water):
        with cols[i]:
            html = (
                f'<div class="card" style="border-left: 4px solid {COLORS["water_dark"]};">'
                f'<p style="color:{COLORS["text_muted"]};font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">'
                f'{w["name"]}</p>'
                f'<p style="color:{COLORS["water_dark"]};font-size:1.75rem;font-weight:700;margin:0;line-height:1.1;">'
                f'{w["flow"]:.1f}</p>'
                f'<p style="color:{COLORS["text_muted"]};font-size:0.85rem;margin-top:0.25rem;">'
                f'м³/с · уровень {w["level"]:.2f} м</p>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

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
st.markdown("## История расхода воды")

river_id = st.selectbox(
    "Речная станция",
    options=[s["id"] for s in stations],
    format_func=lambda x: next(s["name"] for s in stations if s["id"] == x),
)

try:
    flow_data = requests.get(f"{API}/water/flow/{river_id}?days=7", timeout=5).json()
    if flow_data:
        fdf = pd.DataFrame(flow_data)
        fdf["timestamp"] = pd.to_datetime(fdf["timestamp"])
        fig = px.line(fdf, x="timestamp", y="flow_m3s",
                      labels={"flow_m3s": "Расход, м³/с", "timestamp": ""})
        fig.update_traces(line_color=COLORS["water_dark"], line_width=2)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Ошибка истории: {e}")

# --- Таблица риска ---
st.markdown("## Риск паводков по районам")

if flood:
    risk_rows = []
    for r in flood:
        color, label = risk_color(r["risk_score"])
        risk_rows.append({
            "Район": r["district"],
            "Риск": r["risk_score"],
            "Уровень": label,
        })
    rdf = pd.DataFrame(risk_rows)
    st.dataframe(rdf, use_container_width=True, hide_index=True)

footer(lang=get_lang())

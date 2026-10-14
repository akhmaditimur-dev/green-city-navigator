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
from auth_utils import is_logged_in, get_user

API = "http://api:8000"

inject_css()
if st.session_state.get("theme") == "dark":
    inject_dark_css()

header(lang=get_lang())

# --- Заголовок ---
st.markdown("# Качество воздуха")
st.caption("Данные о PM2.5 с 5 станций в Худжанде")

# --- Данные ---
try:
    stations = requests.get(f"{API}/stations", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка API: {e}")
    st.stop()

if not stations:
    st.warning("Нет станций")
    st.stop()

# --- Собираем текущие данные ---
current_data = []
for s in stations:
    try:
        cur = requests.get(f"{API}/current/{s['id']}", timeout=3).json()
        current_data.append({
            "id": s["id"],
            "name": s["name"],
            "lat": s["lat"],
            "lon": s["lon"],
            "pm25": cur["pm25"],
            "aqi": cur["aqi"],
        })
    except Exception:
        pass

df = pd.DataFrame(current_data)

# --- Функция цвета AQI ---
def aqi_color(pm25):
    if pm25 < 35:
        return COLORS["green_dark"], "Хорошо"
    elif pm25 < 75:
        return COLORS["warm_dark"], "Умеренно"
    elif pm25 < 150:
        return COLORS["danger"], "Вредно"
    else:
        return "#7f1d1d", "Опасно"

# --- Текущие значения (карточки) ---
st.markdown("## Текущие значения")

cols = st.columns(len(df))
for i, row in df.iterrows():
    color, label = aqi_color(row["pm25"])
    with cols[i]:
        html = (
            f'<div class="card" style="border-left: 4px solid {color};">'
            f'<p style="color:{COLORS["text_muted"]};font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">'
            f'{row["name"]}</p>'
            f'<p style="color:{color};font-size:1.75rem;font-weight:700;margin:0;line-height:1.1;">'
            f'{row["pm25"]:.1f}</p>'
            f'<p style="color:{COLORS["text_muted"]};font-size:0.85rem;margin-top:0.25rem;">'
            f'мкг/м³ · AQI {row["aqi"]}</p>'
            f'<p style="color:{color};font-size:0.8rem;font-weight:500;margin-top:0.5rem;">{label}</p>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

# --- Рекомендация ---
avg_pm = df["pm25"].mean()
if avg_pm < 35:
    recommendation(t("rec_air_good"), "info")
elif avg_pm < 75:
    recommendation(t("rec_air_moderate"), "warning")
else:
    recommendation(t("rec_air_bad"), "danger")

# --- Карта ---
st.markdown("## Карта станций")

fig_map = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="pm25",
    color="pm25",
    hover_name="name",
    color_continuous_scale="RdYlGn_r",
    zoom=12,
    height=450,
    size_max=30,
)
fig_map.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="PM2.5"),
)
st.plotly_chart(fig_map, use_container_width=True)

# --- История ---
st.markdown("## История PM2.5")

col1, col2 = st.columns([1, 3])
with col1:
    days = st.selectbox("Период", [7, 30], format_func=lambda x: f"{x} дней")
    station_id = st.selectbox(
        "Станция",
        options=[s["id"] for s in stations],
        format_func=lambda x: next(s["name"] for s in stations if s["id"] == x),
    )

try:
    data = requests.get(f"{API}/measurements/{station_id}?days={days}", timeout=5).json()
    if data:
        hdf = pd.DataFrame(data)
        hdf["timestamp"] = pd.to_datetime(hdf["timestamp"])
        fig = px.line(hdf, x="timestamp", y="pm25", labels={"pm25": "PM2.5, мкг/м³", "timestamp": ""})
        fig.update_traces(line_color=COLORS["air_dark"], line_width=2)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Ошибка истории: {e}")

# --- Прогноз ---
st.markdown("## Прогноз на 24 часа")

try:
    forecast = requests.get(f"{API}/forecast/{station_id}?hours=24", timeout=5).json()
    fdf = pd.DataFrame(forecast["forecast"])

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=fdf["hour"], y=fdf["pm25"],
        mode="lines+markers",
        line=dict(color=COLORS["air_dark"], width=2),
        marker=dict(size=6, color=COLORS["air_dark"]),
        name="Прогноз",
    ))
    fig2.add_hline(y=35, line_dash="dash", line_color=COLORS["green_dark"],
                   annotation_text="35 (хорошо)", annotation_position="right")
    fig2.add_hline(y=75, line_dash="dash", line_color=COLORS["warm_dark"],
                   annotation_text="75 (умеренно)", annotation_position="right")
    fig2.update_layout(
        xaxis_title="Часы",
        yaxis_title="PM2.5, мкг/м³",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=100, t=20, b=0),
    )
    st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error(f"Ошибка прогноза: {e}")

footer(lang=get_lang())

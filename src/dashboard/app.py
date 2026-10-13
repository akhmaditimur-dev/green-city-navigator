import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API = "http://api:8000"

st.set_page_config(page_title="Green City Navigator", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 13px;
    }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    .stMetric label { font-size: 0.8rem !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    .stMetric [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }
    .stDataFrame { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🌿 Green City Navigator — Худжанд")

# --- Станции ---
stations = requests.get(f"{API}/stations").json()

# --- Карта ---
st.header("Карта станций")

map_df = pd.DataFrame([
    {
        "name": s["name"],
        "lat": s["lat"],
        "lon": s["lon"],
        "pm25": requests.get(f"{API}/current/{s['id']}").json()["pm25"],
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
    height=500,
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# --- Текущие значения ---
st.header("Текущее состояние")

cols = st.columns(len(stations))
for i, s in enumerate(stations):
    current = requests.get(f"{API}/current/{s['id']}").json()
    with cols[i]:
        st.metric(s["name"], f"{current['pm25']:.1f} мкг/м³", f"AQI {current['aqi']}")

# --- История PM2.5 ---
st.header("История PM2.5 (7 дней)")

station_id = st.selectbox(
    "Станция",
    options=[s["id"] for s in stations],
    format_func=lambda x: next(s["name"] for s in stations if s["id"] == x),
)

data = requests.get(f"{API}/measurements/{station_id}?days=7").json()
df = pd.DataFrame(data)
df["timestamp"] = pd.to_datetime(df["timestamp"])

fig = px.line(df, x="timestamp", y="pm25", title="PM2.5")
st.plotly_chart(fig, use_container_width=True)

# --- Прогноз ---
st.header("Прогноз на 24 часа")

forecast = requests.get(f"{API}/forecast/{station_id}?hours=24").json()
fdf = pd.DataFrame(forecast["forecast"])

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=fdf["hour"], y=fdf["pm25"], mode="lines+markers", name="Прогноз"))
fig2.add_hline(y=35, line_dash="dash", line_color="orange", annotation_text="Средний порог")
fig2.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="Высокий порог")
fig2.update_layout(xaxis_title="Часы", yaxis_title="PM2.5, мкг/м³")
st.plotly_chart(fig2, use_container_width=True)


# --- МОДУЛЬ ВОДА ---
st.header("💧 Водные ресурсы")

water_stations = requests.get(f"{API}/water/stations").json()

# Карта рек и риска паводков
flood_data = requests.get(f"{API}/flood/risk").json()

if flood_data:
    flood_df = pd.DataFrame(flood_data)
    fig_flood = px.scatter_mapbox(
        flood_df,
        lat="lat",
        lon="lon",
        size="risk_score",
        color="risk_score",
        hover_name="district",
        color_continuous_scale="RdYlGn_r",
        zoom=11,
        height=500,
        range_color=[0, 100],
    )
    fig_flood.update_layout(mapbox_style="open-street-map", title="Риск паводков по районам")
    st.plotly_chart(fig_flood, use_container_width=True)

# Текущее состояние рек
st.subheader("Расход воды на станциях")
cols_w = st.columns(len(water_stations))
for i, ws in enumerate(water_stations):
    current = requests.get(f"{API}/water/current/{ws['id']}").json()
    with cols_w[i]:
        st.metric(
            ws["name"],
            f"{current['flow_m3s']} м³/с",
            f"уровень {current['level_m']} м"
        )

# График расхода
st.subheader("Расход воды (7 дней)")
river_id = st.selectbox(
    "Речная станция",
    options=[ws["id"] for ws in water_stations],
    format_func=lambda x: next(ws["name"] for ws in water_stations if ws["id"] == x),
)

flow_data = requests.get(f"{API}/water/flow/{river_id}?days=7").json()
if flow_data:
    fdf = pd.DataFrame(flow_data)
    fdf["timestamp"] = pd.to_datetime(fdf["timestamp"])
    fig_flow = px.line(fdf, x="timestamp", y="flow_m3s", title="Расход воды, м³/с")
    st.plotly_chart(fig_flow, use_container_width=True)

# Таблица риска
st.subheader("Риск паводков")
if flood_data:
    risk_df = pd.DataFrame(flood_data)[["district", "risk_score", "category"]]
    risk_df.columns = ["Район", "Риск", "Категория"]
    st.dataframe(risk_df, use_container_width=True)
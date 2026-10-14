import streamlit as st
import requests
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import header, footer, COLORS
from i18n import get_lang
from auth_utils import is_logged_in, get_user

API = "http://api:8000"

header(lang=get_lang())

# --- HERO ---
hero_html = (
    '<div class="hero">'
    '<h1>Худжанд — состояние города<br>в реальном времени</h1>'
    '<p class="lead">Воздух, вода, климат и участие жителей. '
    'Данные обновляются автоматически, прогнозы на 24 часа и 7 дней.</p>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# --- Данные ---
try:
    stations_air = requests.get(f"{API}/stations", timeout=5).json()
    stations_water = requests.get(f"{API}/water/stations", timeout=5).json()
    flood = requests.get(f"{API}/flood/risk", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка подключения к API: {e}")
    st.stop()

# --- Метрики ---
col1, col2, col3, col4 = st.columns(4)

if stations_air:
    pm_values = []
    for s in stations_air:
        try:
            cur = requests.get(f"{API}/current/{s['id']}", timeout=3).json()
            pm_values.append(cur["pm25"])
        except Exception:
            pass
    avg_pm25 = sum(pm_values) / len(pm_values) if pm_values else 0
    aqi = int(avg_pm25 * 2)
    with col1:
        st.metric("Качество воздуха", f"{avg_pm25:.0f} мкг/м³", f"AQI {aqi}")

if stations_water:
    flow_values = []
    for s in stations_water:
        try:
            cur = requests.get(f"{API}/water/current/{s['id']}", timeout=3).json()
            flow_values.append(cur["flow_m3s"])
        except Exception:
            pass
    avg_flow = sum(flow_values) / len(flow_values) if flow_values else 0
    with col2:
        st.metric("Расход воды", f"{avg_flow:.0f} м³/с")

if flood:
    max_risk = max(r["risk_score"] for r in flood)
    max_district = next(r["district"] for r in flood if r["risk_score"] == max_risk)
    with col3:
        st.metric("Риск паводков", f"{max_risk:.0f}", max_district)

with col4:
    st.metric("Температура", "—", "в разработке")

# --- Разделы ---
st.markdown("## Разделы")

col_a, col_b, col_c = st.columns(3)

with col_a:
    html = (
        f'<div class="card card-air">'
        f'<h3 style="color:{COLORS["air_dark"]};">Воздух</h3>'
        f'<p style="color:{COLORS["text_muted"]};">PM2.5, карта станций, прогноз на 24 часа</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if st.button("Открыть →", key="go_air_home", use_container_width=True):
        st.switch_page("views/air.py")

with col_b:
    html = (
        f'<div class="card card-water">'
        f'<h3 style="color:{COLORS["water_dark"]};">Вода</h3>'
        f'<p style="color:{COLORS["text_muted"]};">Расход воды, риск паводков, прогноз</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if st.button("Открыть →", key="go_water_home", use_container_width=True):
        st.switch_page("views/water.py")

with col_c:
    html = (
        f'<div class="card card-green">'
        f'<h3 style="color:{COLORS["green_dark"]};">Участие</h3>'
        f'<p style="color:{COLORS["text_muted"]};">Сообщить о проблеме, карта обращений</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if st.button("Открыть →", key="go_participate_home", use_container_width=True):
        st.switch_page("views/participate.py")

# --- Курсы ---
st.markdown("## Обучение")
st.caption("Курсы по экологии, воде и климату для специалистов и жителей")

try:
    r = requests.get(f"{API}/courses", timeout=5)
    courses = r.json() if r.status_code == 200 else []
except Exception:
    courses = []

if courses:
    cols = st.columns(min(3, len(courses)))
    for i, c in enumerate(courses[:3]):
        with cols[i % 3]:
            html = (
                f'<div class="card">'
                f'<p style="color:{COLORS["text_light"]};font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">'
                f'{c["category"]} · {c["level"]}</p>'
                f'<h3>{c["title_ru"]}</h3>'
                f'<p style="color:{COLORS["text_muted"]};font-size:0.9rem;">'
                f'{(c.get("description_ru") or "")[:100]}...</p>'
                f'<p style="color:{COLORS["text_light"]};font-size:0.85rem;">'
                f'{c["lessons_count"]} уроков · {c["students_count"]} студентов</p>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
            if st.button("Открыть", key=f"open_course_home_{c['id']}", use_container_width=True):
                st.session_state.selected_course = c["id"]
                st.switch_page("views/course.py")
else:
    st.info("Курсы скоро появятся")

footer(lang=get_lang())

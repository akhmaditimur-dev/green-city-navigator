import streamlit as st
import requests
import pandas as pd

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

# --- Настройка ---
st.set_page_config(
    page_title="Green City Navigator",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# --- Сайдбар ---
lang_switch()

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t('menu_home')}")
st.sidebar.markdown(f"### {t('menu_air')}")
st.sidebar.markdown(f"### {t('menu_water')}")
st.sidebar.markdown(f"### {t('menu_participate')}")
st.sidebar.markdown(f"### {t('menu_about')}")

# --- Хедер ---
header(lang=get_lang())

# --- Заголовок ---
st.title(f"🌿 {t('home_title')} — {t('city')}")
st.markdown(f"*{t('home_subtitle')}*")

# --- Данные ---
try:
    stations_air = requests.get(f"{API}/stations", timeout=5).json()
    stations_water = requests.get(f"{API}/water/stations", timeout=5).json()
    flood = requests.get(f"{API}/flood/risk", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка подключения к API: {e}")
    st.stop()

# --- Текущие метрики ---
col1, col2, col3, col4 = st.columns(4)

# Воздух — среднее по станциям
if stations_air:
    pm_values = []
    for s in stations_air:
        try:
            cur = requests.get(f"{API}/current/{s['id']}", timeout=3).json()
            pm_values.append(cur["pm25"])
        except:
            pass
    avg_pm25 = sum(pm_values) / len(pm_values) if pm_values else 0
    aqi = int(avg_pm25 * 2)

    with col1:
        st.metric(
            label=t("current_air"),
            value=f"{avg_pm25:.0f} мкг/м³",
            delta=f"AQI {aqi}",
        )

# Вода — среднее по станциям
if stations_water:
    flow_values = []
    for s in stations_water:
        try:
            cur = requests.get(f"{API}/water/current/{s['id']}", timeout=3).json()
            flow_values.append(cur["flow_m3s"])
        except:
            pass
    avg_flow = sum(flow_values) / len(flow_values) if flow_values else 0

    with col2:
        st.metric(
            label=t("current_water"),
            value=f"{avg_flow:.0f} м³/с",
        )

# Риск паводков — максимальный
if flood:
    max_risk = max(r["risk_score"] for r in flood)
    max_district = next(r["district"] for r in flood if r["risk_score"] == max_risk)

    with col3:
        st.metric(
            label=t("current_risk"),
            value=f"{max_risk:.0f}",
            delta=max_district,
        )

# Температура — с первой станции воздуха
if stations_air:
    try:
        first = stations_air[0]
        cur = requests.get(f"{API}/current/{first['id']}", timeout=3).json()
        # Температура не в /current, добавим позже
        with col4:
            st.metric(
                label=t("current_temp"),
                value="—",
            )
    except:
        pass

st.markdown("---")

# --- Быстрые ссылки ---
st.subheader(t("quick_links"))

link_col1, link_col2, link_col3 = st.columns(3)

with link_col1:
    st.markdown(f"""
    <div class="card">
        <h3>💨 {t('menu_air')}</h3>
        <p>PM2.5, карта станций, прогноз на 24 часа</p>
    </div>
    """, unsafe_allow_html=True)

with link_col2:
    st.markdown(f"""
    <div class="card">
        <h3>💧 {t('menu_water')}</h3>
        <p>Расход воды, риск паводков, прогноз</p>
    </div>
    """, unsafe_allow_html=True)

with link_col3:
    st.markdown(f"""
    <div class="card">
        <h3>📢 {t('menu_participate')}</h3>
        <p>Сообщить о проблеме, карта обращений</p>
    </div>
    """, unsafe_allow_html=True)

# --- Последнее обновление ---
st.markdown("---")
last_update = pd.Timestamp.now().strftime("%d.%m.%Y %H:%M")
st.caption(f"{t('last_update')}: {last_update}")

# --- Футер ---
footer(lang=get_lang())
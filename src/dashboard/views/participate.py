import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer, COLORS
from styles_dark import inject_dark_css
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

# st.set_page_config(page_title="Участие — Green City Navigator", page_icon="🌿", layout="wide")

inject_css()
if st.session_state.get("theme") == "dark":
    inject_dark_css()

header(lang=get_lang())

st.markdown("# Сообщить о проблеме")
st.caption("Помогите улучшить город — ваше обращение увидит мэрия")

# --- Геокодер ---
@st.cache_resource
def get_geolocator():
    return Nominatim(user_agent="green-city-navigator")

geolocator = get_geolocator()

# --- Session state для координат ---
if "report_lat" not in st.session_state:
    st.session_state.report_lat = 40.2833
if "report_lon" not in st.session_state:
    st.session_state.report_lon = 69.6333
if "report_address" not in st.session_state:
    st.session_state.report_address = ""

# --- Данные ---
try:
    reports = requests.get(f"{API}/reports", timeout=5).json()
except Exception:
    reports = []

# --- Две колонки ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("## Форма обращения")

    # Адрес
    address_input = st.text_input(
        "Адрес (необязательно)",
        value=st.session_state.report_address,
        placeholder="ул. Ленина, 15, Худжанд",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Найти на карте", use_container_width=True):
            if address_input:
                try:
                    loc = geolocator.geocode(f"{address_input}, Худжанд, Таджикистан", timeout=10)
                    if loc:
                        st.session_state.report_lat = loc.latitude
                        st.session_state.report_lon = loc.longitude
                        st.session_state.report_address = loc.address
                        st.success(f"Найдено: {loc.address[:80]}...")
                        st.rerun()
                    else:
                        st.warning("Адрес не найден")
                except Exception as e:
                    st.error(f"Ошибка геокодирования: {e}")
            else:
                st.warning("Введите адрес")

    with col_btn2:
        if st.button("Сбросить", use_container_width=True):
            st.session_state.report_lat = 40.2833
            st.session_state.report_lon = 69.6333
            st.session_state.report_address = ""
            st.rerun()

    # Текущие координаты
    st.caption(f"Координаты: {st.session_state.report_lat:.4f}, {st.session_state.report_lon:.4f}")

    # Форма
    with st.form("report_form", clear_on_submit=True):
        name = st.text_input("Ваше имя")
        category = st.selectbox(
            "Категория",
            ["air", "water", "trash", "other"],
            format_func=lambda x: {"air": "Воздух", "water": "Вода",
                                    "trash": "Мусор", "other": "Другое"}[x],
        )
        description = st.text_area("Описание проблемы", height=120)

        submitted = st.form_submit_button("Отправить", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Заполните описание")
            else:
                try:
                    r = requests.post(
                        f"{API}/reports",
                        json={
                            "name": name or None,
                            "category": category,
                            "description": description,
                            "lat": st.session_state.report_lat,
                            "lon": st.session_state.report_lon,
                        },
                        timeout=5,
                    )
                    if r.status_code == 200:
                        st.success("Спасибо! Обращение принято.")
                        st.rerun()
                    else:
                        st.error(f"Ошибка: {r.status_code}")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with col2:
    st.markdown("## Кликните на карту для координат")

    import plotly.graph_objects as go

    # Карта с Plotly — работает стабильнее folium
    fig = go.Figure()

    # Маркер текущей точки
    fig.add_trace(go.Scattermapbox(
        lat=[st.session_state.report_lat],
        lon=[st.session_state.report_lon],
        mode="markers",
        marker=dict(size=18, color="red"),
        text=["Ваша точка"],
        hoverinfo="text",
    ))

    # Существующие обращения
    if reports:
        rdf = pd.DataFrame(reports).dropna(subset=["lat", "lon"])
        if not rdf.empty:
            fig.add_trace(go.Scattermapbox(
                lat=rdf["lat"],
                lon=rdf["lon"],
                mode="markers",
                marker=dict(size=10, color=COLORS["text_muted"]),
                text=rdf["description"].str[:50],
                hoverinfo="text",
                name="Обращения",
            ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=st.session_state.report_lat, lon=st.session_state.report_lon),
            zoom=12,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Кликните по карте для уточнения координат вручную (ниже)")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        new_lat = st.number_input("Широта", value=st.session_state.report_lat, format="%.4f", key="manual_lat")
    with col_lon:
        new_lon = st.number_input("Долгота", value=st.session_state.report_lon, format="%.4f", key="manual_lon")

    if new_lat != st.session_state.report_lat or new_lon != st.session_state.report_lon:
        st.session_state.report_lat = new_lat
        st.session_state.report_lon = new_lon
        st.rerun()

# --- Таблица ---
st.markdown("## Список проблем")

if reports:
    df = pd.DataFrame(reports)
    cat_labels = {"air": "Воздух", "water": "Вода", "trash": "Мусор", "other": "Другое"}
    status_labels = {"new": "Новое", "in_progress": "В работе", "resolved": "Решено"}

    df["category_label"] = df["category"].map(cat_labels).fillna(df["category"])
    df["status_label"] = df["status"].map(status_labels).fillna(df["status"])
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d.%m.%Y %H:%M")

    show = df[["created_at", "name", "category_label", "description", "status_label"]].copy()
    show.columns = ["Дата", "Имя", "Категория", "Описание", "Статус"]
    show["Имя"] = show["Имя"].fillna("Аноним")
    st.dataframe(show, use_container_width=True, hide_index=True)
else:
    st.info("Пока нет обращений")

footer(lang=get_lang())

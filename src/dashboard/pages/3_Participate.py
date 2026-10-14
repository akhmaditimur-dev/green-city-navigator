import streamlit as st
import requests
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang

API = "http://api:8000"

st.set_page_config(page_title="Участие — Green City Navigator", page_icon="📢", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

st.title(f"📢 {t('participate_title')}")
st.markdown(f"*{t('participate_subtitle')}*")

# --- Данные ---
try:
    reports = requests.get(f"{API}/reports", timeout=5).json()
except Exception as e:
    st.error(f"Ошибка API: {e}")
    reports = []

# --- Две колонки: форма + карта ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(t("participate_form"))

    with st.form("report_form", clear_on_submit=True):
        name = st.text_input(t("form_name"))
        category = st.selectbox(
            t("form_category"),
            ["air", "water", "trash", "other"],
            format_func=lambda x: t(f"cat_{x}"),
        )
        description = st.text_area(t("form_description"), height=100)
        photo_url = st.text_input(t("form_photo"))
        lat = st.number_input(t("form_lat"), value=40.2833, format="%.4f")
        lon = st.number_input(t("form_lon"), value=69.6333, format="%.4f")

        submitted = st.form_submit_button(t("form_submit"))

        if submitted:
            if not description.strip():
                st.error(t("form_error"))
            else:
                payload = {
                    "name": name or None,
                    "category": category,
                    "description": description,
                    "photo_url": photo_url or None,
                    "lat": lat,
                    "lon": lon,
                }
                try:
                    r = requests.post(f"{API}/reports", json=payload, timeout=5)
                    if r.status_code == 200:
                        st.success(t("form_success"))
                        st.rerun()
                    else:
                        st.error(f"Ошибка: {r.status_code}")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with col2:
    st.subheader(t("participate_map"))

    if reports:
        df = pd.DataFrame(reports)
        df_filtered = df.dropna(subset=["lat", "lon"])

        if not df_filtered.empty:
            fig = px.scatter_mapbox(
                df_filtered,
                lat="lat",
                lon="lon",
                color="category",
                hover_name="description",
                zoom=11,
                height=450,
                color_discrete_map={
                    "air": "#1e6091",
                    "water": "#4a90c2",
                    "trash": "#e09f3e",
                    "other": "#5c6b73",
                },
            )
            fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет обращений с координатами")
    else:
        st.info("Пока нет обращений")

# --- Список ---
st.subheader(t("participate_list"))

if reports:
    df = pd.DataFrame(reports)
    df["category_label"] = df["category"].apply(lambda x: t(f"cat_{x}"))
    df["status_label"] = df["status"].apply(lambda x: t(f"status_{x}"))
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d.%m.%Y %H:%M")

    show = df[["created_at", "name", "category_label", "description", "status_label"]].copy()
    show.columns = ["Дата", "Имя", "Категория", "Описание", "Статус"]
    st.dataframe(show, use_container_width=True, hide_index=True)
else:
    st.info("Пока нет обращений")

footer(lang=get_lang())
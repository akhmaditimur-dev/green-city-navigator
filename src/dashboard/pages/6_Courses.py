import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang
from auth_utils import is_logged_in

API = "http://api:8000"

st.set_page_config(page_title="Курсы — Green City Navigator", page_icon="📚", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

st.title("📚 Курсы")
st.markdown("Обучающие курсы по экологии, воде и климату")

# Фильтры
col1, col2 = st.columns(2)
with col1:
    category = st.selectbox("Категория", ["all", "air", "water", "climate", "general"],
                            format_func=lambda x: {"all": "Все", "air": "Воздух", "water": "Вода",
                                                    "climate": "Климат", "general": "Общее"}.get(x, x))
with col2:
    level = st.selectbox("Уровень", ["all", "beginner", "intermediate", "advanced"],
                         format_func=lambda x: {"all": "Все", "beginner": "Начальный",
                                                "intermediate": "Средний", "advanced": "Продвинутый"}.get(x, x))

# Данные
params = {}
if category != "all":
    params["category"] = category
if level != "all":
    params["level"] = level

try:
    r = requests.get(f"{API}/courses", params=params, timeout=5)
    courses = r.json()
except Exception as e:
    st.error(f"Ошибка: {e}")
    st.stop()

if not courses:
    st.info("Пока нет курсов")
    st.stop()

# Сетка курсов
cols = st.columns(3)
for i, c in enumerate(courses):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="card" style="min-height: 220px;">
            <h3>{c['title_ru']}</h3>
            <p style="color: #5c6b73; font-size: 0.85rem;">{c['category']} · {c['level']}</p>
            <p>{c['description_ru'][:120] if c['description_ru'] else ''}...</p>
            <p style="color: #5c6b73; font-size: 0.85rem;">
                📖 {c['lessons_count']} уроков · 👥 {c['students_count']} студентов
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Открыть курс", key=f"course_{c['id']}"):
            st.session_state.selected_course = c["id"]
            st.switch_page("pages/7_Course.py")

footer(lang=get_lang())
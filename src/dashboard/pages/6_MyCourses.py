import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang
from auth_utils import require_login, auth_headers

API = "http://api:8000"

st.set_page_config(page_title="Мои курсы — Green City Navigator", page_icon="📚", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

require_login()

st.title("📚 Мои курсы")

try:
    r = requests.get(f"{API}/my/courses", headers=auth_headers(), timeout=5)
    courses = r.json()
except Exception as e:
    st.error(f"Ошибка: {e}")
    st.stop()

if not courses:
    st.info("Вы ещё не записаны ни на один курс")
    if st.button("← Перейти в каталог"):
        st.switch_page("pages/6_Courses.py")
    st.stop()

for c in courses:
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {c['title_ru']}")
            st.caption(f"{c['category']} · {c['lessons_count']} уроков")
            st.progress(c["progress"] / 100, text=f"Прогресс: {c['progress']}%")
        with col2:
            if st.button("Открыть", key=f"my_course_{c['course_id']}"):
                st.session_state.selected_course = c["course_id"]
                st.switch_page("pages/7_Course.py")
        st.markdown("---")

if st.button("← Перейти в каталог"):
    st.switch_page("pages/6_Courses.py")

footer(lang=get_lang())
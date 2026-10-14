import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang
from auth_utils import is_logged_in, get_token, auth_headers

API = "http://api:8000"

st.set_page_config(page_title="Курс — Green City Navigator", page_icon="📖", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

course_id = st.session_state.get("selected_course")
if not course_id:
    st.warning("Курс не выбран")
    if st.button("← К каталогу"):
        st.switch_page("pages/6_Courses.py")
    st.stop()

# Данные курса
try:
    r = requests.get(f"{API}/courses/{course_id}", timeout=5)
    if r.status_code != 200:
        st.error("Курс не найден")
        st.stop()
    course = r.json()
except Exception as e:
    st.error(f"Ошибка: {e}")
    st.stop()

st.title(course["title_ru"])
st.caption(f"{course['category']} · {course['level']} · Автор: {course.get('author', '—')}")

st.markdown(f"**{course['description_ru']}**")

st.markdown("---")

# Кнопка записи
if is_logged_in():
    try:
        r = requests.post(f"{API}/courses/{course_id}/enroll",
                          headers=auth_headers(), timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "already_enrolled":
                st.success("Вы уже записаны на этот курс")
            else:
                st.success("Вы записаны на курс")
    except Exception as e:
        st.warning(f"Не удалось записаться: {e}")
else:
    st.info("Войдите, чтобы записаться на курс")
    if st.button("Войти"):
        st.switch_page("pages/0_Login.py")

st.markdown("---")
st.subheader("Уроки")

lessons = course.get("lessons", [])
if not lessons:
    st.info("Уроки ещё не добавлены")
else:
    for lesson in lessons:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{lesson['order_num']}. {lesson['title_ru']}**")
            st.caption(f"{lesson['lesson_type']} · {lesson['duration_min']} мин")
        with col2:
            if st.button("Открыть", key=f"lesson_{lesson['id']}"):
                st.session_state.selected_lesson = lesson["id"]
                st.switch_page("pages/8_Lesson.py")

st.markdown("---")
if st.button("← К каталогу"):
    st.switch_page("pages/6_Courses.py")

footer(lang=get_lang())
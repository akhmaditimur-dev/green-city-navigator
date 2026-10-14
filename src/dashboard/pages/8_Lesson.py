import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang
from auth_utils import is_logged_in, auth_headers

API = "http://api:8000"

st.set_page_config(page_title="Урок — Green City Navigator", page_icon="📖", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

lesson_id = st.session_state.get("selected_lesson")
if not lesson_id:
    st.warning("Урок не выбран")
    st.stop()

if not is_logged_in():
    st.warning("Войдите, чтобы смотреть уроки")
    if st.button("Войти"):
        st.switch_page("pages/0_Login.py")
    st.stop()

try:
    r = requests.get(f"{API}/lessons/{lesson_id}", headers=auth_headers(), timeout=5)
    if r.status_code != 200:
        st.error("Урок не найден")
        st.stop()
    lesson = r.json()
except Exception as e:
    st.error(f"Ошибка: {e}")
    st.stop()

st.title(lesson["title_ru"])
st.caption(f"{lesson['lesson_type']} · {lesson['duration_min']} мин")

st.markdown("---")

if lesson["lesson_type"] == "text":
    st.markdown(lesson.get("content_ru") or "Содержимое не добавлено")
elif lesson["lesson_type"] == "video":
    if lesson.get("video_url"):
        st.video(lesson["video_url"])
    else:
        st.warning("Видео не добавлено")
elif lesson["lesson_type"] == "material":
    if lesson.get("material_url"):
        st.markdown(f"[📄 Скачать материал]({lesson['material_url']})")
    else:
        st.warning("Материал не добавлен")

st.markdown("---")

if lesson.get("is_completed"):
    st.success("✅ Урок пройден")
else:
    if st.button("Отметить как пройденный"):
        r = requests.post(f"{API}/lessons/{lesson_id}/complete",
                          headers=auth_headers(), timeout=5)
        if r.status_code == 200:
            data = r.json()
            st.success(f"Прогресс: {data['progress']}%")
            st.rerun()

if st.button("← К курсу"):
    st.switch_page("pages/7_Course.py")

footer(lang=get_lang())
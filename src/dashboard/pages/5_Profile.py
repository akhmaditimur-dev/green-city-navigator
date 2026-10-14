import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang
from auth_utils import require_login, get_user, get_token, logout, auth_headers

API = "http://api:8000"

st.set_page_config(page_title="Профиль — Green City Navigator", page_icon="👤", layout="wide")

inject_css()
lang_switch()

require_login()

user = get_user()

# --- Хедер ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title(f"👤 {user.get('full_name') or user.get('username')}")
with col2:
    if st.button("Выйти"):
        logout()
        st.switch_page("pages/0_Login.py")

st.caption(f"Логин: **{user['username']}** · Роль: **{user['role']}**")

st.markdown("---")

# --- Данные с сервера ---
try:
    r = requests.get(f"{API}/auth/me", headers=auth_headers(), timeout=5)
    if r.status_code == 200:
        me = r.json()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ID", me["id"])
        with col2:
            st.metric("Роль", me["role"])
        with col3:
            st.metric("Создан", me["created_at"][:10] if me.get("created_at") else "—")
    elif r.status_code == 401:
        st.error("Сессия истекла. Войдите заново.")
        logout()
        st.switch_page("pages/0_Login.py")
except Exception as e:
    st.error(f"Ошибка: {e}")

st.markdown("---")

# --- Разделы ---
st.subheader("Разделы")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📚 Мои курсы</h3>
        <p>Курсы, на которые вы записаны</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Перейти → Мои курсы", key="my_courses"):
        st.info("Раздел в разработке")

with col2:
    st.markdown("""
    <div class="card">
        <h3>🎓 Сертификаты</h3>
        <p>Ваши сертификаты об обучении</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Перейти → Сертификаты", key="certs"):
        st.info("Раздел в разработке")

with col3:
    st.markdown("""
    <div class="card">
        <h3>💬 Форум</h3>
        <p>Общение с другими участниками</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Перейти → Форум", key="forum"):
        st.info("Раздел в разработке")

# --- Админ-панель для админов ---
if user["role"] in ("admin", "superadmin"):
    st.markdown("---")
    st.subheader("🔧 Админ-панель")
    st.markdown("Управление пользователями и приглашениями")
    if st.button("Открыть админ-панель", key="admin"):
        st.switch_page("pages/9_Admin.py")

footer(lang=get_lang())
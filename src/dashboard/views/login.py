import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css
from i18n import t, lang_switch, get_lang
from auth_utils import set_token, is_logged_in

API = "http://api:8000"

# st.set_page_config(page_title="Вход — Green City Navigator", page_icon="🔐", layout="centered")

inject_css()

if is_logged_in():
    st.success("Вы уже вошли")
    if st.button("Перейти в профиль"):
        st.switch_page("views/profile.py")
    st.stop()

st.title("🔐 Вход")
st.markdown("Войдите, чтобы получить доступ к личному кабинету")

with st.form("login_form"):
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    submitted = st.form_submit_button("Войти")

    if submitted:
        if not username or not password:
            st.error("Заполните все поля")
        else:
            try:
                r = requests.post(
                    f"{API}/auth/login",
                    json={"username": username, "password": password},
                    timeout=5,
                )
                if r.status_code == 200:
                    data = r.json()
                    set_token(data["access_token"], data["user"])
                    st.success("Вход выполнен")
                    st.switch_page("views/profile.py")
                elif r.status_code == 401:
                    st.error("Неверный логин или пароль")
                elif r.status_code == 423:
                    st.error("Аккаунт заблокирован. Попробуйте позже.")
                else:
                    st.error(f"Ошибка: {r.status_code} {r.text}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

st.markdown("---")
st.caption("Нет доступа? Обратитесь к администратору YGPE за приглашением.")

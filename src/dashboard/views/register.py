import streamlit as st
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css
from i18n import lang_switch
from auth_utils import set_token, is_logged_in

API = "http://api:8000"

# st.set_page_config(page_title="Регистрация — Green City Navigator", page_icon="📝", layout="centered")

inject_css()

if is_logged_in():
    st.success("Вы уже вошли")
    st.stop()

# Код из URL
code_from_url = st.query_params.get("code", "")

st.title("📝 Регистрация")
st.markdown("Создайте аккаунт по коду приглашения")

with st.form("register_form"):
    code = st.text_input("Код приглашения", value=code_from_url)
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    full_name = st.text_input("ФИО")

    submitted = st.form_submit_button("Зарегистрироваться")

    if submitted:
        if not code or not username or not password:
            st.error("Заполните обязательные поля")
        else:
            try:
                r = requests.post(
                    f"{API}/auth/register",
                    json={
                        "code": code.strip().upper(),
                        "username": username.strip(),
                        "password": password,
                        "full_name": full_name or None,
                    },
                    timeout=5,
                )
                if r.status_code == 200:
                    data = r.json()
                    set_token(data["access_token"], data["user"])
                    st.success("Аккаунт создан")
                    st.switch_page("pages/5_Profile.py")
                else:
                    try:
                        detail = r.json().get("detail", r.text)
                    except Exception:
                        detail = r.text
                    st.error(f"Ошибка: {detail}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

st.markdown("---")
st.markdown("**Требования к паролю:**")
st.markdown("- Минимум 8 символов\n- Заглавная и строчная буквы\n- Цифра\n- Спецсимвол (`!@#$%^&*`)")

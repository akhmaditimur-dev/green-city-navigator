import streamlit as st
import requests
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, footer
from i18n import t, lang_switch, get_lang
from auth_utils import require_login, get_user, auth_headers

API = "http://api:8000"

st.set_page_config(page_title="Админ-панель — Green City Navigator", page_icon="🔧", layout="wide")

inject_css()
lang_switch()

require_login()

user = get_user()
if user["role"] not in ("admin", "superadmin"):
    st.error("Доступ запрещён")
    st.stop()

st.title("🔧 Админ-панель")
st.caption(f"Вы вошли как **{user['username']}** ({user['role']})")

tab1, tab2, tab3 = st.tabs(["👥 Пользователи", "🎫 Приглашения", "📜 История входов"])

# --- Пользователи ---
with tab1:
    st.subheader("Пользователи")

    try:
        r = requests.get(f"{API}/admin/users", headers=auth_headers(), timeout=5)
        if r.status_code == 200:
            users = r.json()
            df = pd.DataFrame(users)
            if not df.empty:
                show = df[["id", "username", "full_name", "role", "is_active", "last_login"]].copy()
                show.columns = ["ID", "Логин", "ФИО", "Роль", "Активен", "Последний вход"]
                st.dataframe(show, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("Изменить роль")

                col1, col2, col3 = st.columns(3)
                with col1:
                    uid = st.selectbox("Пользователь", options=[u["id"] for u in users],
                                       format_func=lambda x: next(f"{u['username']} ({u['role']})" for u in users if u["id"] == x))
                with col2:
                    new_role = st.selectbox("Новая роль", ["student", "teacher", "admin", "superadmin"])
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("Сменить роль"):
                        r = requests.post(f"{API}/admin/users/{uid}/role",
                                          json={"role": new_role},
                                          headers=auth_headers(), timeout=5)
                        if r.status_code == 200:
                            st.success("Роль изменена")
                            st.rerun()
                        else:
                            st.error(r.text)
            else:
                st.info("Нет пользователей")
        else:
            st.error(f"Ошибка загрузки: {r.status_code}")
    except Exception as e:
        st.error(f"Ошибка: {e}")

# --- Приглашения ---
with tab2:
    st.subheader("Приглашения")

    with st.expander("➕ Создать приглашение"):
        col1, col2 = st.columns(2)
        with col1:
            inv_role = st.selectbox("Роль", ["student", "teacher", "admin", "superadmin"], key="inv_role")
        with col2:
            inv_days = st.number_input("Дней действия", min_value=1, max_value=365, value=30)

        if st.button("Создать"):
            r = requests.post(f"{API}/admin/invitations",
                              json={"role": inv_role, "days": inv_days},
                              headers=auth_headers(), timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.success(f"Код: **{data['code']}**")
                st.code(data["link"], language=None)
                st.rerun()
            else:
                st.error(r.text)

    try:
        r = requests.get(f"{API}/admin/invitations", headers=auth_headers(), timeout=5)
        if r.status_code == 200:
            invs = r.json()
            if invs:
                df = pd.DataFrame(invs)
                show = df[["id", "code", "role", "is_used", "is_expired", "expires_at"]].copy()
                show.columns = ["ID", "Код", "Роль", "Использован", "Истёк", "Истекает"]
                st.dataframe(show, use_container_width=True, hide_index=True)

                st.markdown("---")
                del_id = st.selectbox("Удалить приглашение", options=[i["id"] for i in invs])
                if st.button("Удалить"):
                    r = requests.delete(f"{API}/admin/invitations/{del_id}",
                                        headers=auth_headers(), timeout=5)
                    if r.status_code == 200:
                        st.success("Удалено")
                        st.rerun()
                    else:
                        st.error(r.text)
            else:
                st.info("Нет приглашений")
    except Exception as e:
        st.error(f"Ошибка: {e}")

# --- История входов ---
with tab3:
    st.subheader("История входов")

    try:
        r = requests.get(f"{API}/admin/login-history?limit=100", headers=auth_headers(), timeout=5)
        if r.status_code == 200:
            history = r.json()
            if history:
                df = pd.DataFrame(history)
                show = df[["created_at", "username", "ip_address", "success"]].copy()
                show.columns = ["Дата", "Логин", "IP", "Успех"]
                st.dataframe(show, use_container_width=True, hide_index=True)
            else:
                st.info("История пуста")
    except Exception as e:
        st.error(f"Ошибка: {e}")

footer(lang=get_lang())
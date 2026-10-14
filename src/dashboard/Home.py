import streamlit as st

from styles import inject_css
from styles_dark import inject_dark_css
from i18n import lang_switch, get_lang
from auth_utils import is_logged_in, get_user


# --- Конфиг ---
st.set_page_config(
    page_title="Green City Navigator — Худжанд",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
if st.session_state.get("theme") == "dark":
    inject_dark_css()


# --- Определяем страницы ---
def build_navigation():
    user = get_user() or {}
    role = user.get("role", "guest")
    logged = is_logged_in()

    # Публичные страницы
    public_pages = [
        st.Page("views/home_content.py", title="Обзор", icon=":material/home:", default=True),
        st.Page("views/air.py", title="Воздух", icon=":material/air:"),
        st.Page("views/water.py", title="Вода", icon=":material/water_drop:"),
        st.Page("views/heat.py", title="Тепло", icon=":material/thermostat:"),
        st.Page("views/participate.py", title="Участие", icon=":material/campaign:"),
    ]

    learning_pages = [
        st.Page("views/courses.py", title="Курсы", icon=":material/school:"),
    ]
    if logged:
        learning_pages.append(st.Page("views/my_courses.py", title="Мои курсы", icon=":material/menu_book:"))

    info_pages = [
        st.Page("views/about.py", title="О проекте", icon=":material/info:"),
    ]

    # Аккаунт
    if logged:
        account_pages = [
            st.Page("views/profile.py", title="Профиль", icon=":material/person:"),
        ]
        if role in ("admin", "superadmin"):
            account_pages.append(st.Page("views/admin.py", title="Админ-панель", icon=":material/settings:"))
    else:
        account_pages = [
            st.Page("views/login.py", title="Войти", icon=":material/login:"),
            st.Page("views/register.py", title="Регистрация", icon=":material/person_add:"),
        ]

    # Собираем всё
    sections = {
        "Навигация": public_pages,
        "Обучение": learning_pages,
        "О проекте": info_pages,
        "Аккаунт": account_pages,
    }

    return st.navigation(sections)


# --- Меню в сайдбаре ---
lang_switch()
st.sidebar.markdown("---")

theme_label = "Светлая" if st.session_state.get("theme") == "dark" else "Тёмная"
if st.sidebar.button(theme_label, key="theme_switch", use_container_width=True):
    st.session_state.theme = "light" if st.session_state.get("theme") == "dark" else "dark"
    st.rerun()


# --- Запуск выбранной страницы ---
pg = build_navigation()
pg.run()
import streamlit as st


def set_token(token: str, user: dict):
    st.session_state.token = token
    st.session_state.user = user


def get_token():
    return st.session_state.get("token")


def get_user():
    return st.session_state.get("user")


def is_logged_in() -> bool:
    return bool(st.session_state.get("token"))


def logout():
    for key in ["token", "user"]:
        if key in st.session_state:
            del st.session_state[key]


def auth_headers():
    token = get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def require_login():
    """Если не залогинен — редирект на /login."""
    if not is_logged_in():
        st.warning("Требуется вход")
        st.switch_page("pages/0_Login.py")
        st.stop()
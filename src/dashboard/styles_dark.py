"""Тёмная тема. Активируется через st.session_state.theme = 'dark'."""
import streamlit as st


DARK_COLORS = {
    "bg": "#0f172a",
    "bg_soft": "#1e293b",
    "bg_muted": "#334155",
    "card": "#1e293b",
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "text_light": "#64748b",
    "border": "#334155",
    "border_strong": "#475569",
    "green_dark": "#4ade80",
    "green_light": "#14532d",
    "sidebar_bg": "#1e293b",
    "sidebar_border": "#334155",
    "sidebar_hover": "#334155",
    "sidebar_active": "#475569",
}


def inject_dark_css():
    """Переопределяет светлую тему на тёмную (включая сайдбар)."""
    st.markdown(f"""
    <style>
        /* Основной фон */
        .stApp, [data-testid="stAppViewContainer"] {{
            background: {DARK_COLORS['bg']} !important;
        }}
        html, body, [class*="css"] {{
            color: {DARK_COLORS['text']} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, li, span, div {{
            color: {DARK_COLORS['text']} !important;
        }}
        .block-container {{
            background: {DARK_COLORS['bg']} !important;
        }}

        /* Сайдбар — тёмный */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarNav"] {{
            background: {DARK_COLORS['sidebar_bg']} !important;
            background-color: {DARK_COLORS['sidebar_bg']} !important;
            border-color: {DARK_COLORS['sidebar_border']} !important;
        }}

        /* Текст сайдбара — светлый */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] *,
        [data-testid="stSidebarNav"] * {{
            color: {DARK_COLORS['text']} !important;
        }}

        /* Ссылки меню — фон сайдбара */
        [data-testid="stSidebar"] a,
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNavLink"] {{
            background: {DARK_COLORS['sidebar_bg']} !important;
            background-color: {DARK_COLORS['sidebar_bg']} !important;
            color: {DARK_COLORS['text']} !important;
        }}

        /* Hover */
        [data-testid="stSidebar"] a:hover,
        [data-testid="stSidebarNav"] a:hover {{
            background: {DARK_COLORS['sidebar_hover']} !important;
            background-color: {DARK_COLORS['sidebar_hover']} !important;
            color: white !important;
        }}

        /* Активная */
        [data-testid="stSidebar"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: {DARK_COLORS['sidebar_active']} !important;
            background-color: {DARK_COLORS['sidebar_active']} !important;
            color: white !important;
            font-weight: 700 !important;
        }}
        [data-testid="stSidebar"] a[aria-current="page"] *,
        [data-testid="stSidebarNav"] a[aria-current="page"] * {{
            color: white !important;
        }}

        /* Кнопки в сайдбаре */
        [data-testid="stSidebar"] button,
        [data-testid="stSidebar"] .stButton > button {{
            background: {DARK_COLORS['sidebar_bg']} !important;
            color: {DARK_COLORS['text']} !important;
            border: 1px solid {DARK_COLORS['sidebar_border']} !important;
        }}
        [data-testid="stSidebar"] button:hover {{
            background: {DARK_COLORS['sidebar_hover']} !important;
            color: white !important;
        }}

        /* Стрелка свернуть */
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebar"] [data-testid="stBaseButton-header"] {{
            background: {DARK_COLORS['sidebar_active']} !important;
            color: white !important;
            border: none !important;
        }}
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: white !important;
        }}

        /* Карточки и метрики */
        .card, .stMetric {{
            background: {DARK_COLORS['card']} !important;
            border-color: {DARK_COLORS['border']} !important;
        }}

        /* Формы */
        .stTextInput input, .stTextArea textarea,
        .stSelectbox > div > div, .stNumberInput input {{
            background: {DARK_COLORS['bg_muted']} !important;
            color: {DARK_COLORS['text']} !important;
            border-color: {DARK_COLORS['border']} !important;
        }}

        /* Хедер Streamlit */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        header[data-testid="stHeader"] {{
            background: {DARK_COLORS['bg']} !important;
            color: {DARK_COLORS['text']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)
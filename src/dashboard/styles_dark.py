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
}


def inject_dark_css():
    """Переопределяет светлую тему на тёмную."""
    st.markdown(f"""
    <style>
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
        [data-testid="stSidebar"] {{
            background: {DARK_COLORS['bg_soft']} !important;
            border-color: {DARK_COLORS['border']} !important;
        }}
        .card, .stMetric {{
            background: {DARK_COLORS['card']} !important;
            border-color: {DARK_COLORS['border']} !important;
        }}
        .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {{
            background: {DARK_COLORS['bg_muted']} !important;
            color: {DARK_COLORS['text']} !important;
            border-color: {DARK_COLORS['border']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)
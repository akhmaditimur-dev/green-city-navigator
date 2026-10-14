import streamlit as st


# --- Цвета (матовые, серьёзные) ---
COLORS = {
    "primary_green": "#2d6a4f",      # тёмно-зелёный
    "light_green": "#52b788",        # светло-зелёный
    "primary_blue": "#1e6091",       # тёмно-синий
    "light_blue": "#4a90c2",         # светло-синий
    "bg": "#f8f9fa",                 # фон
    "card_bg": "#ffffff",            # карточки
    "text": "#1b263b",               # текст
    "text_muted": "#5c6b73",         # второстепенный текст
    "border": "#dee2e6",             # границы
    # Статусы
    "success": "#2d6a4f",
    "warning": "#e09f3e",
    "danger": "#bc4749",
    "info": "#1e6091",
}

# --- AQI категории ---
AQI_COLORS = {
    "good": "#2d6a4f",                # 0-50
    "moderate": "#e09f3e",            # 51-100
    "unhealthy_sensitive": "#d97706", # 101-150
    "unhealthy": "#bc4749",           # 151-200
    "very_unhealthy": "#7f1d1d",      # 201+
}

# --- Риск паводков ---
RISK_COLORS = {
    "low": "#2d6a4f",
    "medium": "#e09f3e",
    "high": "#d97706",
    "critical": "#bc4749",
}


def inject_css():
    """Подключает единый CSS. Вызывать в начале каждой страницы."""
    st.markdown(f"""
    <style>
        /* Шрифты и общий фон */
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            color: {COLORS['text']};
        }}
        .stApp {{
            background: {COLORS['bg']};
        }}

        /* Заголовки */
        h1 {{ font-size: 1.8rem !important; color: {COLORS['primary_green']} !important; font-weight: 600 !important; }}
        h2 {{ font-size: 1.4rem !important; color: {COLORS['primary_green']} !important; font-weight: 600 !important; margin-top: 1.5rem !important; }}
        h3 {{ font-size: 1.1rem !important; color: {COLORS['primary_blue']} !important; font-weight: 600 !important; }}

        /* Метрики */
        .stMetric {{
            background: {COLORS['card_bg']};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {COLORS['primary_green']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .stMetric label {{ font-size: 0.8rem !important; color: {COLORS['text_muted']} !important; }}
        .stMetric [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; color: {COLORS['text']} !important; }}

        /* Карточки */
        .card {{
            background: {COLORS['card_bg']};
            padding: 1.2rem;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 1rem;
        }}

        /* Рекомендации */
        .recommendation {{
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid {COLORS['info']};
            background: #eef4f8;
            color: {COLORS['text']};
        }}
        .recommendation.warning {{
            border-left-color: {COLORS['warning']};
            background: #fdf6e8;
        }}
        .recommendation.danger {{
            border-left-color: {COLORS['danger']};
            background: #fbeae9;
        }}

        /* Таблицы */
        .stDataFrame {{ font-size: 13px; }}

        /* Кнопки */
        .stButton > button {{
            background: {COLORS['primary_green']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
        }}
        .stButton > button:hover {{
            background: {COLORS['light_green']};
        }}

        /* Сайдбар */
        [data-testid="stSidebar"] {{
            background: {COLORS['card_bg']};
            border-right: 1px solid {COLORS['border']};
        }}
        [data-testid="stSidebar"] a {{
            color: {COLORS['text']} !important;
            font-size: 0.95rem;
        }}
        [data-testid="stSidebar"] a:hover {{
            color: {COLORS['primary_green']} !important;
        }}

        /* Убираем лишние отступы */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px !important;
        }}

        /* Хедер */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1rem 0;
            border-bottom: 1px solid {COLORS['border']};
            margin-bottom: 1.5rem;
        }}
        .header .logo {{
            font-size: 1.3rem;
            font-weight: 600;
            color: {COLORS['primary_green']};
        }}

        /* Футер */
        .footer {{
            margin-top: 3rem;
            padding: 1.5rem 0;
            border-top: 1px solid {COLORS['border']};
            color: {COLORS['text_muted']};
            font-size: 0.85rem;
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)


def header(lang: str = "ru"):
    """Верхний хедер с логотипом и кнопкой входа."""
    login_text = "Войти" if lang == "ru" else "Sign in"
    status_text = "в разработке" if lang == "ru" else "coming soon"

    st.markdown(f"""
    <div class="header">
        <div class="logo">🌿 Green City Navigator</div>
        <div style="color: {COLORS['text_muted']}; font-size: 0.9rem;">
            {login_text} <span style="font-size: 0.75rem;">({status_text})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def footer(lang: str = "ru"):
    """Футер с партнёрами."""
    text = "Партнёры: YGPE · GIZ · EU4Sustainable Central Asia" if lang == "ru" \
        else "Partners: YGPE · GIZ · EU4Sustainable Central Asia"

    st.markdown(f"""
    <div class="footer">{text}</div>
    """, unsafe_allow_html=True)


def recommendation(text: str, level: str = "info"):
    """Блок рекомендации. level: info / warning / danger."""
    st.markdown(f"""
    <div class="recommendation {level}">{text}</div>
    """, unsafe_allow_html=True)
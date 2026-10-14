import streamlit as st


# ============= ЦВЕТА =============
COLORS = {
    # Нейтральные
    "bg": "#ffffff",
    "bg_soft": "#f8fafc",
    "bg_muted": "#f1f5f9",
    "card": "#ffffff",
    "text": "#0f172a",
    "text_muted": "#64748b",
    "text_light": "#94a3b8",
    "border": "#e2e8f0",
    "border_strong": "#cbd5e1",

    # Сайдбар — оливковый
    "sidebar_bg": "#e8eeda",
    "sidebar_border": "#d1dcb5",
    "sidebar_text": "#4a5e2a",
    "sidebar_hover": "#d6e0bc",
    "sidebar_active_bg": "#c6d3a2",      # активная — на 2 тона темнее
    "sidebar_active_text": "#2d3f18",

    # Акценты модулей
    "air_light": "#e0f2fe",
    "air": "#7dd3fc",
    "air_dark": "#0369a1",

    "water_light": "#dbeafe",
    "water": "#3b82f6",
    "water_dark": "#1e40af",

    "green_light": "#dcfce7",
    "green": "#86efac",
    "green_dark": "#16a34a",

    "warm_light": "#ffedd5",
    "warm": "#fdba74",
    "warm_dark": "#ea580c",

    "climate_light": "#ede9fe",
    "climate": "#c4b5fd",
    "climate_dark": "#7c3aed",

    "success": "#16a34a",
    "warning": "#ea580c",
    "danger": "#dc2626",
    "info": "#0ea5e9",
}


# ============= CSS =============
def inject_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 15px;
            color: {COLORS['text']};
            -webkit-font-smoothing: antialiased;
        }}

        .stApp {{ background: {COLORS['bg']}; }}

        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1280px !important;
        }}

        h1 {{
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: {COLORS['text']} !important;
            letter-spacing: -0.02em !important;
            line-height: 1.15 !important;
            margin-bottom: 0.5rem !important;
        }}
        h2 {{
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            color: {COLORS['text']} !important;
            letter-spacing: -0.01em !important;
            margin-top: 2.5rem !important;
            margin-bottom: 1rem !important;
        }}
        h3 {{
            font-size: 1.125rem !important;
            font-weight: 600 !important;
            color: {COLORS['text']} !important;
            margin-bottom: 0.5rem !important;
        }}
        h4 {{
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: {COLORS['text_muted']} !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        p, li {{ color: {COLORS['text']}; line-height: 1.6; }}

        /* ============ САЙДБАР (СВЕТЛАЯ) ============ */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarNav"] {{
            background: {COLORS['sidebar_bg']} !important;
            background-color: {COLORS['sidebar_bg']} !important;
            border-color: {COLORS['sidebar_border']} !important;
        }}

        /* Текст — болотный */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] *,
        [data-testid="stSidebarNav"] * {{
            color: {COLORS['sidebar_text']} !important;
        }}

        /* Ссылки меню — фон = фон сайдбара */
        [data-testid="stSidebar"] a,
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNavLink"] {{
            background: {COLORS['sidebar_bg']} !important;
            background-color: {COLORS['sidebar_bg']} !important;
            color: {COLORS['sidebar_text']} !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 0.5rem 0.75rem !important;
            border-radius: 8px !important;
            margin-bottom: 4px !important;
            border: none !important;
            box-shadow: none !important;
            transition: all 0.15s ease;
        }}

        /* Hover */
        [data-testid="stSidebar"] a:hover,
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNavLink"]:hover {{
            background: {COLORS['sidebar_hover']} !important;
            background-color: {COLORS['sidebar_hover']} !important;
            color: {COLORS['sidebar_active_text']} !important;
        }}

        /* Активная ссылка — на 2 тона темнее */
        [data-testid="stSidebar"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebar"] [aria-current="page"],
        [data-testid="stSidebarNav"] [aria-current="page"],
        section[data-testid="stSidebar"] a[aria-current="page"],
        [data-testid="stSidebarNavLink"][aria-current="page"],
        [data-testid="stSidebar"] li[aria-selected="true"] > a,
        [data-testid="stSidebarNav"] li[aria-selected="true"] > a,
        [data-testid="stSidebar"] a.nav-active {{
            background: #c6d3a2 !important;
            background-color: #c6d3a2 !important;
            color: #2d3f18 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
        }}
        /* Активная ссылка — при любом состоянии (hover, focus, active) */
        [data-testid="stSidebar"] a[aria-current="page"],
        [data-testid="stSidebar"] a[aria-current="page"]:hover,
        [data-testid="stSidebar"] a[aria-current="page"]:focus,
        [data-testid="stSidebar"] a[aria-current="page"]:active,
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"]:hover,
        [data-testid="stSidebarNav"] a[aria-current="page"]:focus,
        [data-testid="stSidebarNav"] a[aria-current="page"]:active {{
            background: #c6d3a2 !important;
            background-color: #c6d3a2 !important;
            color: #2d3f18 !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }}

        /* Текст */
        [data-testid="stSidebar"] a[aria-current="page"] *,
        [data-testid="stSidebarNav"] a[aria-current="page"] *,
        [data-testid="stSidebar"] a.nav-active * {{
            color: #2d3f18 !important;
            font-weight: 700 !important;
        }}

        /* Hover НЕ перебивает активную */
        [data-testid="stSidebar"] a.nav-active:hover,
        [data-testid="stSidebar"] a[aria-current="page"]:hover {{
            background: #c6d3a2 !important;
            background-color: #c6d3a2 !important;
            color: #2d3f18 !important;
        }}

        /* Заголовки секций */
        [data-testid="stSidebarNav"] > div > span,
        [data-testid="stSidebar"] h4 {{
            color: {COLORS['sidebar_text']} !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.75rem !important;
            background: transparent !important;
        }}

        /* Кнопки в сайдбаре (EN, Тёмная) — как фон сайдбара */
        [data-testid="stSidebar"] button,
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] button[kind="secondary"] {{
            background: {COLORS['sidebar_bg']} !important;
            background-color: {COLORS['sidebar_bg']} !important;
            color: {COLORS['sidebar_text']} !important;
            border: 1px solid {COLORS['sidebar_border']} !important;
            box-shadow: none !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSidebar"] button:hover {{
            background: {COLORS['sidebar_hover']} !important;
            color: {COLORS['sidebar_active_text']} !important;
            border-color: {COLORS['sidebar_active_text']} !important;
            transform: none !important;
        }}

        /* Стрелка свернуть — фон как у активной ссылки */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebar"] [data-testid="stBaseButton-header"],
        [data-testid="stSidebar"] [data-testid="baseButton-header"] {{
            background: {COLORS['sidebar_active_bg']} !important;
            background-color: {COLORS['sidebar_active_bg']} !important;
            color: {COLORS['sidebar_active_text']} !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover {{
            background: {COLORS['sidebar_hover']} !important;
            color: {COLORS['sidebar_active_text']} !important;
        }}
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: {COLORS['sidebar_active_text']} !important;
            color: {COLORS['sidebar_active_text']} !important;
        }}

        /* ============ КАРТОЧКИ ============ */
        .card {{
            background: {COLORS['card']};
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            transition: all 0.2s ease;
        }}
        .card:hover {{
            border-color: {COLORS['border_strong']};
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        }}
        .card-air {{ background: {COLORS['air_light']}; border-color: {COLORS['air']}; }}
        .card-water {{ background: {COLORS['water_light']}; border-color: {COLORS['water']}; }}
        .card-green {{ background: {COLORS['green_light']}; border-color: {COLORS['green']}; }}
        .card-warm {{ background: {COLORS['warm_light']}; border-color: {COLORS['warm']}; }}
        .card-climate {{ background: {COLORS['climate_light']}; border-color: {COLORS['climate']}; }}

        /* ============ МЕТРИКИ ============ */
        .stMetric {{
            background: {COLORS['card']};
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
        }}
        .stMetric label {{
            font-size: 0.75rem !important;
            color: {COLORS['text_muted']} !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .stMetric [data-testid="stMetricValue"] {{
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            color: {COLORS['text']} !important;
        }}
        .stMetric [data-testid="stMetricDelta"] {{ font-size: 0.85rem !important; }}

        /* ============ КНОПКИ (вне сайдбара) ============ */
        .stButton > button {{
            background: {COLORS['text']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.25rem;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.15s ease;
        }}
        .stButton > button:hover {{
            background: {COLORS['green_dark']};
            transform: translateY(-1px);
        }}
        .stButton > button:focus {{
            box-shadow: 0 0 0 3px {COLORS['green_light']} !important;
        }}

        /* ============ ФОРМЫ ============ */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox > div > div,
        .stNumberInput input {{
            border-radius: 8px !important;
            border-color: {COLORS['border']} !important;
            font-size: 0.9rem !important;
        }}
        .stTextInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {COLORS['green_dark']} !important;
            box-shadow: 0 0 0 3px {COLORS['green_light']} !important;
        }}

        /* ============ ТАБЫ ============ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 6px 6px 0 0;
            padding: 0.6rem 1rem;
            font-weight: 500;
            font-size: 0.9rem;
            color: {COLORS['text_muted']};
        }}
        .stTabs [aria-selected="true"] {{
            background: {COLORS['green_light']};
            color: {COLORS['green_dark']} !important;
        }}

        /* ============ ТАБЛИЦЫ ============ */
        .stDataFrame {{
            font-size: 13px;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            overflow: hidden;
        }}

        /* ============ РЕКОМЕНДАЦИИ ============ */
        .recommendation {{
            padding: 1rem 1.25rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid {COLORS['info']};
            background: {COLORS['air_light']};
            font-size: 0.9rem;
        }}
        .recommendation.warning {{
            border-left-color: {COLORS['warning']};
            background: {COLORS['warm_light']};
        }}
        .recommendation.danger {{
            border-left-color: {COLORS['danger']};
            background: #fee2e2;
        }}

        /* ============ ХЕДЕР ============ */
        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0 1.5rem 0;
            border-bottom: 1px solid {COLORS['border']};
            margin-bottom: 2rem;
        }}
        .app-logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.15rem;
            font-weight: 700;
            color: {COLORS['text']};
            letter-spacing: -0.01em;
        }}
        .app-logo svg {{ width: 28px; height: 28px; }}

        /* ============ HERO ============ */
        .hero {{ padding: 3rem 0 2rem 0; }}
        .hero h1 {{ font-size: 3rem !important; line-height: 1.1 !important; }}
        .hero .lead {{
            font-size: 1.15rem;
            color: {COLORS['text_muted']};
            margin-top: 0.75rem;
            max-width: 640px;
        }}

        /* ============ ФУТЕР ============ */
        .app-footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid {COLORS['border']};
            color: {COLORS['text_muted']};
            font-size: 0.85rem;
            text-align: center;
        }}

        /* Кнопка свернуть — всегда видна */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebar"] [data-testid="stBaseButton-header"],
        [data-testid="stSidebar"] [data-testid="baseButton-header"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            background: #c6d3a2 !important;
            color: #2d3f18 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: #2d3f18 !important;
        }}
    </style>
    """, unsafe_allow_html=True)


# ============= КОМПОНЕНТЫ =============

def logo_svg(color: str = None) -> str:
    c = color or COLORS["green_dark"]
    return f'''
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" fill="none">
        <path d="M16 4 C16 4, 26 10, 26 18 C26 24, 22 28, 16 28 C10 28, 6 24, 6 18 C6 10, 16 4, 16 4 Z"
              fill="{c}" opacity="0.15"/>
        <path d="M16 6 C16 6, 24 11, 24 18 C24 22.5, 20.5 26, 16 26 C11.5 26, 8 22.5, 8 18 C8 11, 16 6, 16 6 Z"
              fill="{c}" opacity="0.4"/>
        <path d="M16 10 L16 24 M16 14 L20 12 M16 17 L12 15"
              stroke="{c}" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="16" cy="24" r="1.5" fill="{c}"/>
    </svg>
    '''


def header(lang: str = "ru"):
    from auth_utils import is_logged_in, get_user

    if is_logged_in():
        user = get_user() or {}
        name = user.get("full_name") or user.get("username") or "Пользователь"
        right_html = (
            f'<a href="/Profile" target="_self" style="display:flex;align-items:center;gap:8px;'
            f'color:{COLORS["text"]};text-decoration:none;font-size:0.9rem;font-weight:500;'
            f'padding:0.5rem 1rem;border-radius:8px;background:{COLORS["bg_muted"]};">'
            f'<span style="width:28px;height:28px;border-radius:50%;background:{COLORS["green_dark"]};'
            f'color:white;display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:0.75rem;font-weight:600;">{name[0].upper()}</span>{name}</a>'
        )
    else:
        login_text = "Войти" if lang == "ru" else "Sign in"
        right_html = (
            f'<a href="/Login" target="_self" style="color:white;text-decoration:none;'
            f'font-size:0.9rem;font-weight:500;padding:0.55rem 1.25rem;border-radius:8px;'
            f'background:{COLORS["text"]};">{login_text}</a>'
        )

    html = (
        f'<div class="app-header">'
        f'<div class="app-logo">{logo_svg()}<span>Green City Navigator</span></div>'
        f'<div>{right_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def footer(lang: str = "ru"):
    text = "Партнёры: YGPE · GIZ · EU4Sustainable Central Asia" if lang == "ru" \
        else "Partners: YGPE · GIZ · EU4Sustainable Central Asia"

    html = (
        f'<div class="app-footer">{text}<br>'
        f'<span style="color:{COLORS["text_light"]};font-size:0.75rem;margin-top:8px;display:inline-block;">'
        f'© 2026 Green City Navigator · Худжанд</span></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def recommendation(text: str, level: str = "info"):
    st.markdown(f'<div class="recommendation {level}">{text}</div>', unsafe_allow_html=True)


def card(title: str, body: str, variant: str = "default"):
    cls = "card" if variant == "default" else f"card card-{variant}"
    html = (
        f'<div class="{cls}">'
        f'<h3>{title}</h3>'
        f'<p style="color:{COLORS["text_muted"]};font-size:0.9rem;">{body}</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
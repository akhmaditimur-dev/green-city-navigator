import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from styles import inject_css, header, footer
from i18n import t, lang_switch, get_lang

st.set_page_config(page_title="О проекте — Green City Navigator", page_icon="ℹ️", layout="wide")

inject_css()
lang_switch()
header(lang=get_lang())

st.title(f"ℹ️ {t('about_title')}")

# --- Что это ---
st.subheader(t("about_what"))
st.markdown(f"""
<div class="card">
    {t('about_what_text')}
</div>
""", unsafe_allow_html=True)

# --- Методология ---
st.subheader(t("about_method"))
st.markdown(f"""
<div class="card">
    {t('about_method_text')}
</div>
""", unsafe_allow_html=True)

# --- Партнёры ---
st.subheader(t("about_partners"))

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h3>YGPE</h3>
        <p>Молодёжная группа<br>по защите окружающей среды</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h3>GIZ</h3>
        <p>EU4Sustainable<br>Central Asia</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h3>Мэрия Худжанда</h3>
        <p>Пилотный город<br>проекта</p>
    </div>
    """, unsafe_allow_html=True)

# --- Контакты ---
st.subheader(t("about_contacts"))

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="card">
        <h3>📧 {t('about_email')}</h3>
        <p>info@ygpe.tj</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="card">
        <h3>📞 {t('about_phone')}</h3>
        <p>+992 XX XXX XX XX</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="card">
        <h3>📍 {t('about_address')}</h3>
        <p>г. Худжанд,<br>Согдийская область</p>
    </div>
    """, unsafe_allow_html=True)

footer(lang=get_lang())
import streamlit as st


TRANSLATIONS = {
    "ru": {
        # Header / nav
        "app_name": "Green City Navigator",
        "city": "Худжанд",
        "login": "Войти",
        "login_soon": "в разработке",

        # Menu
        "menu_home": "Главная",
        "menu_air": "Воздух",
        "menu_water": "Вода",
        "menu_participate": "Участие",
        "menu_about": "О проекте",

        # Home
        "home_title": "Обзор города",
        "home_subtitle": "Состояние воздуха и воды в реальном времени",
        "current_air": "Качество воздуха",
        "current_water": "Расход воды",
        "current_risk": "Риск паводков",
        "current_temp": "Температура",
        "quick_links": "Разделы",
        "last_update": "Последнее обновление",

        # Air
        "air_title": "Качество воздуха",
        "air_map": "Карта станций",
        "air_current": "Текущие значения",
        "air_history": "История PM2.5",
        "air_forecast": "Прогноз на 24 часа",
        "air_station": "Станция",
        "air_select_period": "Период",
        "days_7": "7 дней",
        "days_30": "30 дней",

        # Water
        "water_title": "Водные ресурсы",
        "water_map": "Карта рек и риск паводков",
        "water_current": "Расход воды на станциях",
        "water_history": "Расход воды",
        "water_risk": "Риск паводков",
        "water_station": "Речная станция",
        "water_district": "Район",
        "water_level": "Уровень",
        "water_flow": "Расход",
        "water_category": "Категория",

        # Participate
        "participate_title": "Сообщить о проблеме",
        "participate_subtitle": "Помогите улучшить город",
        "participate_map": "Карта проблем",
        "participate_form": "Форма обращения",
        "participate_list": "Список проблем",
        "form_name": "Ваше имя",
        "form_category": "Категория",
        "form_description": "Описание проблемы",
        "form_photo": "Ссылка на фото (необязательно)",
        "form_lat": "Широта",
        "form_lon": "Долгота",
        "form_submit": "Отправить",
        "form_success": "Спасибо! Обращение принято.",
        "form_error": "Заполните обязательные поля",
        "cat_air": "Воздух",
        "cat_water": "Вода",
        "cat_trash": "Мусор",
        "cat_other": "Другое",
        "status_new": "Новое",
        "status_in_progress": "В работе",
        "status_resolved": "Решено",

        # About
        "about_title": "О проекте",
        "about_what": "Что это",
        "about_what_text": "Green City Navigator — цифровая платформа для климат-устойчивого развития Худжанда. "
                          "Показывает состояние воздуха и воды, помогает жителям сообщать о проблемах.",
        "about_method": "Методология",
        "about_method_text": "Данные: спутники, метеостанции, локальные измерения. "
                             "ML-модели: XGBoost, LSTM. Прогноз PM2.5 на 24 часа, R²=0.89.",
        "about_partners": "Партнёры",
        "about_contacts": "Контакты",
        "about_email": "Почта",
        "about_phone": "Телефон",
        "about_address": "Адрес",

        # Recommendations
        "rec_air_good": "Воздух чистый. Можно гулять.",
        "rec_air_moderate": "Умеренное загрязнение. Чувствительным людям — ограничить время на улице.",
        "rec_air_bad": "Высокое загрязнение. Рекомендуется остаться дома.",
        "rec_water_low": "Ситуация спокойная. Риск паводков низкий.",
        "rec_water_medium": "Умеренный риск. Следите за новостями.",
        "rec_water_high": "Высокий риск паводков. Будьте осторожны у воды.",
        "rec_water_critical": "Критический риск. Не приближайтесь к рекам.",

        # Footer
        "partners": "Партнёры: YGPE · GIZ · EU4Sustainable Central Asia",
        "lang_switch": "EN",
    },

    "en": {
        "app_name": "Green City Navigator",
        "city": "Khujand",
        "login": "Sign in",
        "login_soon": "coming soon",

        "menu_home": "Home",
        "menu_air": "Air",
        "menu_water": "Water",
        "menu_participate": "Participate",
        "menu_about": "About",

        "home_title": "City Overview",
        "home_subtitle": "Real-time air and water conditions",
        "current_air": "Air Quality",
        "current_water": "Water Flow",
        "current_risk": "Flood Risk",
        "current_temp": "Temperature",
        "quick_links": "Sections",
        "last_update": "Last update",

        "air_title": "Air Quality",
        "air_map": "Station Map",
        "air_current": "Current Values",
        "air_history": "PM2.5 History",
        "air_forecast": "24-hour Forecast",
        "air_station": "Station",
        "air_select_period": "Period",
        "days_7": "7 days",
        "days_30": "30 days",

        "water_title": "Water Resources",
        "water_map": "Rivers and Flood Risk Map",
        "water_current": "Water Flow at Stations",
        "water_history": "Water Flow",
        "water_risk": "Flood Risk",
        "water_station": "River Station",
        "water_district": "District",
        "water_level": "Level",
        "water_flow": "Flow",
        "water_category": "Category",

        "participate_title": "Report a Problem",
        "participate_subtitle": "Help improve the city",
        "participate_map": "Problem Map",
        "participate_form": "Report Form",
        "participate_list": "Problem List",
        "form_name": "Your name",
        "form_category": "Category",
        "form_description": "Problem description",
        "form_photo": "Photo link (optional)",
        "form_lat": "Latitude",
        "form_lon": "Longitude",
        "form_submit": "Submit",
        "form_success": "Thank you! Report submitted.",
        "form_error": "Fill in required fields",
        "cat_air": "Air",
        "cat_water": "Water",
        "cat_trash": "Trash",
        "cat_other": "Other",
        "status_new": "New",
        "status_in_progress": "In progress",
        "status_resolved": "Resolved",

        "about_title": "About the Project",
        "about_what": "What it is",
        "about_what_text": "Green City Navigator is a digital platform for climate-resilient development of Khujand. "
                          "It shows air and water conditions and helps citizens report problems.",
        "about_method": "Methodology",
        "about_method_text": "Data: satellites, weather stations, local measurements. "
                             "ML models: XGBoost, LSTM. PM2.5 forecast for 24 hours, R²=0.89.",
        "about_partners": "Partners",
        "about_contacts": "Contacts",
        "about_email": "Email",
        "about_phone": "Phone",
        "about_address": "Address",

        "rec_air_good": "Air is clean. Enjoy your walk.",
        "rec_air_moderate": "Moderate pollution. Sensitive groups should limit outdoor time.",
        "rec_air_bad": "High pollution. Stay indoors if possible.",
        "rec_water_low": "Situation is calm. Flood risk is low.",
        "rec_water_medium": "Moderate risk. Follow the news.",
        "rec_water_high": "High flood risk. Be careful near rivers.",
        "rec_water_critical": "Critical risk. Avoid rivers.",

        "partners": "Partners: YGPE · GIZ · EU4Sustainable Central Asia",
        "lang_switch": "RU",
    },
}


def get_lang() -> str:
    """Возвращает текущий язык из сессии."""
    if "lang" not in st.session_state:
        st.session_state.lang = "ru"
    return st.session_state.lang


def set_lang(lang: str):
    st.session_state.lang = lang


def t(key: str) -> str:
    """Перевод по ключу."""
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["ru"]).get(key, key)


def lang_switch():
    """Кнопка переключения языка в сайдбаре."""
    lang = get_lang()
    label = t("lang_switch")
    if st.sidebar.button(label, key="lang_switch"):
        set_lang("en" if lang == "ru" else "ru")
        st.rerun()
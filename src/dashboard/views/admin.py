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

# st.set_page_config(page_title="Админ-панель — Green City Navigator", page_icon="🔧", layout="wide")

inject_css()

require_login()

user = get_user()
if user["role"] not in ("admin", "superadmin"):
    st.error("Доступ запрещён")
    st.stop()

st.title("🔧 Админ-панель")
st.caption(f"Вы вошли как **{user['username']}** ({user['role']})")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Пользователи",
    "🎫 Приглашения",
    "📚 Курсы",
    "📖 Уроки",
    "📜 История входов",
])

# ==================== ПОЛЬЗОВАТЕЛИ ====================
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
                    uid = st.selectbox("Пользователь",
                                       options=[u["id"] for u in users],
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
    except Exception as e:
        st.error(f"Ошибка: {e}")


# ==================== ПРИГЛАШЕНИЯ ====================
with tab2:
    st.subheader("Приглашения")

    with st.expander("➕ Создать приглашение"):
        col1, col2 = st.columns(2)
        with col1:
            inv_role = st.selectbox("Роль", ["student", "teacher", "admin", "superadmin"], key="inv_role")
        with col2:
            inv_days = st.number_input("Дней действия", min_value=1, max_value=365, value=30)

        if st.button("Создать приглашение"):
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
                if st.button("Удалить приглашение"):
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


# ==================== КУРСЫ ====================
with tab3:
    st.subheader("Курсы")

    # Загрузка списка курсов
    try:
        r = requests.get(f"{API}/admin/courses", headers=auth_headers(), timeout=5)
        courses = r.json() if r.status_code == 200 else []
    except Exception:
        courses = []

    # --- Создание ---
    with st.expander("➕ Создать курс", expanded=False):
        with st.form("create_course"):
            title_ru = st.text_input("Название (RU) *")
            title_en = st.text_input("Название (EN) *")
            desc_ru = st.text_area("Описание (RU)")
            desc_en = st.text_area("Описание (EN)")
            col1, col2 = st.columns(2)
            with col1:
                cat = st.selectbox("Категория", ["general", "air", "water", "climate"])
            with col2:
                lvl = st.selectbox("Уровень", ["beginner", "intermediate", "advanced"])
            cover = st.text_input("URL обложки")
            published = st.checkbox("Опубликовать сразу", value=False)

            if st.form_submit_button("Создать"):
                if not title_ru or not title_en:
                    st.error("Заполните название RU/EN")
                else:
                    r = requests.post(
                        f"{API}/admin/courses",
                        json={
                            "title_ru": title_ru,
                            "title_en": title_en,
                            "description_ru": desc_ru or None,
                            "description_en": desc_en or None,
                            "category": cat,
                            "level": lvl,
                            "cover_url": cover or None,
                            "is_published": published,
                        },
                        headers=auth_headers(), timeout=5,
                    )
                    if r.status_code == 200:
                        st.success(f"Курс создан: ID {r.json()['id']}")
                        st.rerun()
                    else:
                        st.error(r.text)

    # --- Таблица ---
    if courses:
        df = pd.DataFrame(courses)
        show = df[["id", "title_ru", "category", "level", "is_published", "lessons_count", "students_count"]].copy()
        show.columns = ["ID", "Название", "Категория", "Уровень", "Опубликован", "Уроков", "Студентов"]
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("✏️ Редактировать курс")

        # Выбор курса
        cid = st.selectbox(
            "Выберите курс",
            options=[c["id"] for c in courses],
            format_func=lambda x: next(f"[{c['id']}] {c['title_ru']}" for c in courses if c["id"] == x),
            key="edit_course_select",
        )

        # Данные курса
        try:
            r = requests.get(f"{API}/courses/{cid}", timeout=5)
            current = r.json() if r.status_code == 200 else None
        except Exception:
            current = None

        # Берём полные данные через админский эндпоинт
        current_admin = next((c for c in courses if c["id"] == cid), None)

        if current_admin:
            with st.form(f"edit_course_{cid}"):
                e_title_ru = st.text_input("Название (RU)", value=current_admin["title_ru"])
                e_title_en = st.text_input("Название (EN)", value=current_admin["title_en"])

                # Описания и обложка — подтягиваем из /courses/{id}
                desc_ru_val = ""
                desc_en_val = ""
                cover_val = ""
                if current:
                    desc_ru_val = current.get("description_ru") or ""
                    desc_en_val = current.get("description_en") or ""
                    cover_val = current.get("cover_url") or ""

                e_desc_ru = st.text_area("Описание (RU)", value=desc_ru_val)
                e_desc_en = st.text_area("Описание (EN)", value=desc_en_val)

                col1, col2 = st.columns(2)
                with col1:
                    cat_list = ["general", "air", "water", "climate"]
                    e_cat = st.selectbox(
                        "Категория",
                        cat_list,
                        index=cat_list.index(current_admin["category"]) if current_admin["category"] in cat_list else 0,
                    )
                with col2:
                    lvl_list = ["beginner", "intermediate", "advanced"]
                    e_lvl = st.selectbox(
                        "Уровень",
                        lvl_list,
                        index=lvl_list.index(current_admin["level"]) if current_admin["level"] in lvl_list else 0,
                    )

                e_cover = st.text_input("URL обложки", value=cover_val)
                e_pub = st.checkbox("Опубликован", value=current_admin["is_published"])

                if st.form_submit_button("💾 Сохранить"):
                    r = requests.put(
                        f"{API}/admin/courses/{cid}",
                        json={
                            "title_ru": e_title_ru,
                            "title_en": e_title_en,
                            "description_ru": e_desc_ru or None,
                            "description_en": e_desc_en or None,
                            "category": e_cat,
                            "level": e_lvl,
                            "cover_url": e_cover or None,
                            "is_published": e_pub,
                        },
                        headers=auth_headers(), timeout=5,
                    )
                    if r.status_code == 200:
                        st.success("Курс обновлён")
                        st.rerun()
                    else:
                        st.error(r.text)

            # --- Удаление с подтверждением ---
            st.markdown("---")
            st.subheader("⚠️ Удалить курс")
            st.warning(f"Удаление курса **[{cid}] {current_admin['title_ru']}** приведёт к удалению всех уроков и записей студентов. Отменить нельзя.")

            confirm = st.checkbox("Я понимаю последствия и хочу удалить курс", key=f"confirm_del_course_{cid}")

            if st.button("🗑 Удалить курс окончательно", disabled=not confirm, key=f"del_course_{cid}"):
                r = requests.delete(f"{API}/admin/courses/{cid}",
                                    headers=auth_headers(), timeout=5)
                if r.status_code == 200:
                    st.success("Курс удалён")
                    st.rerun()
                else:
                    st.error(r.text)
    else:
        st.info("Нет курсов. Создайте первый.")


# ==================== УРОКИ ====================
with tab4:
    st.subheader("Уроки")

    try:
        r = requests.get(f"{API}/admin/courses", headers=auth_headers(), timeout=5)
        courses = r.json() if r.status_code == 200 else []
    except Exception:
        courses = []

    if not courses:
        st.info("Сначала создайте курс")
    else:
        cid_lesson = st.selectbox(
            "Выберите курс",
            options=[c["id"] for c in courses],
            format_func=lambda x: next(f"[{c['id']}] {c['title_ru']}" for c in courses if c["id"] == x),
            key="lesson_course_select",
        )

        # Загрузка уроков
        try:
            r = requests.get(f"{API}/admin/courses/{cid_lesson}/lessons", headers=auth_headers(), timeout=5)
            lessons = r.json() if r.status_code == 200 else []
        except Exception:
            lessons = []

        # --- Список ---
        if lessons:
            df = pd.DataFrame(lessons)
            show = df[["id", "order_num", "title_ru", "lesson_type", "duration_min"]].copy()
            show.columns = ["ID", "Порядок", "Название", "Тип", "Длительность (мин)"]
            st.dataframe(show, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("✏️ Редактировать урок")

            lid = st.selectbox(
                "Выберите урок",
                options=[l["id"] for l in lessons],
                format_func=lambda x: next(f"[{l['id']}] {l['order_num']}. {l['title_ru']}" for l in lessons if l["id"] == x),
                key=f"edit_lesson_{cid_lesson}",
            )

            # Полные данные урока
            try:
                r = requests.get(f"{API}/lessons/{lid}", headers=auth_headers(), timeout=5)
                lesson_data = r.json() if r.status_code == 200 else None
            except Exception:
                lesson_data = None

            if lesson_data:
                with st.form(f"edit_lesson_form_{lid}"):
                    le_title_ru = st.text_input("Название (RU) *", value=lesson_data["title_ru"])
                    le_title_en = st.text_input("Название (EN) *", value=lesson_data["title_en"])

                    types = ["text", "video", "material", "assignment"]
                    le_type = st.selectbox(
                        "Тип урока",
                        types,
                        index=types.index(lesson_data["lesson_type"]) if lesson_data["lesson_type"] in types else 0,
                    )

                    le_content_ru = st.text_area("Содержимое (RU)", value=lesson_data.get("content_ru") or "", height=200)
                    le_content_en = st.text_area("Содержимое (EN)", value=lesson_data.get("content_en") or "", height=200)
                    le_video = st.text_input("URL видео", value=lesson_data.get("video_url") or "")
                    le_material = st.text_input("URL материала", value=lesson_data.get("material_url") or "")

                    col1, col2 = st.columns(2)
                    with col1:
                        le_order = st.number_input("Порядок", min_value=0, value=int(lesson_data["order_num"] or 0))
                    with col2:
                        le_duration = st.number_input("Длительность (мин)", min_value=0, value=int(lesson_data["duration_min"] or 0))

                    if st.form_submit_button("💾 Сохранить урок"):
                        # Используем PUT /admin/lessons/{id} — нужно добавить в API
                        r = requests.put(
                            f"{API}/admin/lessons/{lid}",
                            json={
                                "title_ru": le_title_ru,
                                "title_en": le_title_en,
                                "lesson_type": le_type,
                                "content_ru": le_content_ru or None,
                                "content_en": le_content_en or None,
                                "video_url": le_video or None,
                                "material_url": le_material or None,
                                "order_num": int(le_order),
                                "duration_min": int(le_duration),
                            },
                            headers=auth_headers(), timeout=5,
                        )
                        if r.status_code == 200:
                            st.success("Урок обновлён")
                            st.rerun()
                        else:
                            st.error(r.text)

                # --- Удаление с подтверждением ---
                st.markdown("---")
                st.subheader("⚠️ Удалить урок")
                st.warning(f"Удаление урока **{lesson_data['title_ru']}** необратимо. Прогресс студентов по этому уроку будет потерян.")

                confirm_l = st.checkbox("Я понимаю последствия", key=f"confirm_del_lesson_{lid}")

                if st.button("🗑 Удалить урок окончательно", disabled=not confirm_l, key=f"del_lesson_{lid}"):
                    r = requests.delete(f"{API}/admin/lessons/{lid}",
                                        headers=auth_headers(), timeout=5)
                    if r.status_code == 200:
                        st.success("Урок удалён")
                        st.rerun()
                    else:
                        st.error(r.text)
        else:
            st.info("В этом курсе ещё нет уроков")

        # --- Добавить урок ---
        st.markdown("---")
        st.subheader("➕ Добавить урок")

        with st.form(f"create_lesson_{cid_lesson}"):
            n_title_ru = st.text_input("Название (RU) *")
            n_title_en = st.text_input("Название (EN) *")
            n_type = st.selectbox("Тип", ["text", "video", "material", "assignment"])
            n_content_ru = st.text_area("Содержимое (RU)", height=150)
            n_content_en = st.text_area("Содержимое (EN)", height=150)
            n_video = st.text_input("URL видео")
            n_material = st.text_input("URL материала")
            col1, col2 = st.columns(2)
            with col1:
                n_order = st.number_input("Порядок", min_value=0, value=len(lessons) + 1)
            with col2:
                n_duration = st.number_input("Длительность (мин)", min_value=0, value=15)

            if st.form_submit_button("Добавить урок"):
                if not n_title_ru or not n_title_en:
                    st.error("Заполните название RU/EN")
                else:
                    r = requests.post(
                        f"{API}/admin/courses/{cid_lesson}/lessons",
                        json={
                            "title_ru": n_title_ru,
                            "title_en": n_title_en,
                            "lesson_type": n_type,
                            "content_ru": n_content_ru or None,
                            "content_en": n_content_en or None,
                            "video_url": n_video or None,
                            "material_url": n_material or None,
                            "order_num": int(n_order),
                            "duration_min": int(n_duration),
                        },
                        headers=auth_headers(), timeout=5,
                    )
                    if r.status_code == 200:
                        st.success(f"Урок добавлен: ID {r.json()['id']}")
                        st.rerun()
                    else:
                        st.error(r.text)


# ==================== ИСТОРИЯ ВХОДОВ ====================
with tab5:
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

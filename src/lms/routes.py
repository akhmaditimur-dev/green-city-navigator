from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.db.models import SessionLocal
from src.auth.models import User
from src.auth.deps import get_current_user, require_role
from src.lms.models import Course, Lesson, Enrollment, LessonProgress

router = APIRouter(tags=["lms"])


# --- Публичные: каталог ---
@router.get("/courses")
def list_courses(category: Optional[str] = None, level: Optional[str] = None):
    """Каталог опубликованных курсов."""
    session = SessionLocal()
    q = session.query(Course).filter_by(is_published=True)
    if category:
        q = q.filter_by(category=category)
    if level:
        q = q.filter_by(level=level)
    courses = q.order_by(Course.created_at.desc()).all()

    result = []
    for c in courses:
        lessons_count = session.query(Lesson).filter_by(course_id=c.id).count()
        students_count = session.query(Enrollment).filter_by(course_id=c.id).count()
        author = session.query(User).filter_by(id=c.author_id).first() if c.author_id else None
        result.append({
            "id": c.id,
            "title_ru": c.title_ru,
            "title_en": c.title_en,
            "description_ru": c.description_ru,
            "description_en": c.description_en,
            "category": c.category,
            "level": c.level,
            "cover_url": c.cover_url,
            "author": author.full_name if author else None,
            "lessons_count": lessons_count,
            "students_count": students_count,
        })
    session.close()
    return result


@router.get("/courses/{course_id}")
def get_course(course_id: int):
    """Детали курса."""
    session = SessionLocal()
    c = session.query(Course).filter_by(id=course_id, is_published=True).first()
    if not c:
        session.close()
        raise HTTPException(404, "Курс не найден")

    lessons = (
        session.query(Lesson)
        .filter_by(course_id=course_id)
        .order_by(Lesson.order_num)
        .all()
    )
    author = session.query(User).filter_by(id=c.author_id).first() if c.author_id else None

    result = {
        "id": c.id,
        "title_ru": c.title_ru,
        "title_en": c.title_en,
        "description_ru": c.description_ru,
        "description_en": c.description_en,
        "category": c.category,
        "level": c.level,
        "cover_url": c.cover_url,
        "author": author.full_name if author else None,
        "lessons": [
            {
                "id": l.id,
                "title_ru": l.title_ru,
                "title_en": l.title_en,
                "lesson_type": l.lesson_type,
                "order_num": l.order_num,
                "duration_min": l.duration_min,
            }
            for l in lessons
        ],
    }
    session.close()
    return result


# --- Запись на курс ---
@router.post("/courses/{course_id}/enroll")
def enroll(course_id: int, current: User = Depends(get_current_user)):
    session = SessionLocal()
    c = session.query(Course).filter_by(id=course_id, is_published=True).first()
    if not c:
        session.close()
        raise HTTPException(404, "Курс не найден")

    existing = session.query(Enrollment).filter_by(user_id=current.id, course_id=course_id).first()
    if existing:
        session.close()
        return {"status": "already_enrolled", "enrollment_id": existing.id}

    e = Enrollment(user_id=current.id, course_id=course_id, progress=0)
    session.add(e)
    session.commit()
    session.refresh(e)
    result = {"status": "ok", "enrollment_id": e.id}
    session.close()
    return result


# --- Мои курсы ---
@router.get("/my/courses")
def my_courses(current: User = Depends(get_current_user)):
    session = SessionLocal()
    enrollments = session.query(Enrollment).filter_by(user_id=current.id).all()
    result = []
    for e in enrollments:
        c = session.query(Course).filter_by(id=e.course_id).first()
        if not c:
            continue
        lessons_count = session.query(Lesson).filter_by(course_id=c.id).count()
        result.append({
            "enrollment_id": e.id,
            "course_id": c.id,
            "title_ru": c.title_ru,
            "title_en": c.title_en,
            "category": c.category,
            "progress": e.progress,
            "lessons_count": lessons_count,
            "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        })
    session.close()
    return result


# --- Урок ---
@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, current: User = Depends(get_current_user)):
    session = SessionLocal()
    l = session.query(Lesson).filter_by(id=lesson_id).first()
    if not l:
        session.close()
        raise HTTPException(404, "Урок не найден")

    # Проверка: записан ли пользователь на курс
    enrollment = session.query(Enrollment).filter_by(
        user_id=current.id, course_id=l.course_id
    ).first()

    completed = session.query(LessonProgress).filter_by(
        user_id=current.id, lesson_id=lesson_id
    ).first() is not None

    result = {
        "id": l.id,
        "course_id": l.course_id,
        "title_ru": l.title_ru,
        "title_en": l.title_en,
        "lesson_type": l.lesson_type,
        "content_ru": l.content_ru,
        "content_en": l.content_en,
        "video_url": l.video_url,
        "material_url": l.material_url,
        "order_num": l.order_num,
        "duration_min": l.duration_min,
        "is_enrolled": enrollment is not None,
        "is_completed": completed,
    }
    session.close()
    return result


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, current: User = Depends(get_current_user)):
    session = SessionLocal()
    l = session.query(Lesson).filter_by(id=lesson_id).first()
    if not l:
        session.close()
        raise HTTPException(404, "Урок не найден")

    enrollment = session.query(Enrollment).filter_by(
        user_id=current.id, course_id=l.course_id
    ).first()
    if not enrollment:
        session.close()
        raise HTTPException(403, "Сначала запишитесь на курс")

    existing = session.query(LessonProgress).filter_by(
        user_id=current.id, lesson_id=lesson_id
    ).first()
    if not existing:
        session.add(LessonProgress(user_id=current.id, lesson_id=lesson_id))
        session.commit()

    # Пересчёт прогресса
    total_lessons = session.query(Lesson).filter_by(course_id=l.course_id).count()
    completed_lessons = (
        session.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .filter(LessonProgress.user_id == current.id, Lesson.course_id == l.course_id)
        .count()
    )
    progress = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
    enrollment.progress = progress
    if progress >= 100:
        enrollment.completed_at = datetime.utcnow()
    session.commit()

    result = {
        "status": "ok",
        "progress": progress,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
    }
    session.close()
    return result

# --- Админские эндпоинты ---
class CourseCreate(BaseModel):
    title_ru: str
    title_en: str
    description_ru: Optional[str] = None
    description_en: Optional[str] = None
    category: str = "general"
    level: str = "beginner"
    cover_url: Optional[str] = None
    is_published: bool = False


class LessonCreate(BaseModel):
    title_ru: str
    title_en: str
    lesson_type: str = "text"
    content_ru: Optional[str] = None
    content_en: Optional[str] = None
    video_url: Optional[str] = None
    material_url: Optional[str] = None
    order_num: int = 0
    duration_min: int = 0


@router.post("/admin/courses")
def admin_create_course(
    data: CourseCreate,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    c = Course(
        title_ru=data.title_ru,
        title_en=data.title_en,
        description_ru=data.description_ru,
        description_en=data.description_en,
        category=data.category,
        level=data.level,
        cover_url=data.cover_url,
        is_published=data.is_published,
        author_id=current.id,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    result = {"id": c.id, "title_ru": c.title_ru}
    session.close()
    return result


@router.put("/admin/courses/{course_id}")
def admin_update_course(
    course_id: int,
    data: CourseCreate,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    c = session.query(Course).filter_by(id=course_id).first()
    if not c:
        session.close()
        raise HTTPException(404, "Курс не найден")

    for field, value in data.dict().items():
        setattr(c, field, value)
    c.updated_at = datetime.utcnow()
    session.commit()
    session.close()
    return {"status": "ok", "id": course_id}


@router.delete("/admin/courses/{course_id}")
def admin_delete_course(
    course_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    c = session.query(Course).filter_by(id=course_id).first()
    if not c:
        session.close()
        raise HTTPException(404, "Курс не найден")

    session.query(Lesson).filter_by(course_id=course_id).delete()
    session.query(Enrollment).filter_by(course_id=course_id).delete()
    session.delete(c)
    session.commit()
    session.close()
    return {"status": "ok", "deleted_id": course_id}


@router.get("/admin/courses")
def admin_list_courses(
    current: User = Depends(require_role("admin", "superadmin")),
):
    """Все курсы, включая неопубликованные."""
    session = SessionLocal()
    courses = session.query(Course).order_by(Course.created_at.desc()).all()
    result = []
    for c in courses:
        lessons_count = session.query(Lesson).filter_by(course_id=c.id).count()
        students_count = session.query(Enrollment).filter_by(course_id=c.id).count()
        result.append({
            "id": c.id,
            "title_ru": c.title_ru,
            "title_en": c.title_en,
            "category": c.category,
            "level": c.level,
            "is_published": c.is_published,
            "lessons_count": lessons_count,
            "students_count": students_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    session.close()
    return result


@router.post("/admin/courses/{course_id}/lessons")
def admin_create_lesson(
    course_id: int,
    data: LessonCreate,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    c = session.query(Course).filter_by(id=course_id).first()
    if not c:
        session.close()
        raise HTTPException(404, "Курс не найден")

    l = Lesson(
        course_id=course_id,
        title_ru=data.title_ru,
        title_en=data.title_en,
        lesson_type=data.lesson_type,
        content_ru=data.content_ru,
        content_en=data.content_en,
        video_url=data.video_url,
        material_url=data.material_url,
        order_num=data.order_num,
        duration_min=data.duration_min,
    )
    session.add(l)
    session.commit()
    session.refresh(l)
    result = {"id": l.id, "title_ru": l.title_ru}
    session.close()
    return result


@router.delete("/admin/lessons/{lesson_id}")
def admin_delete_lesson(
    lesson_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    l = session.query(Lesson).filter_by(id=lesson_id).first()
    if not l:
        session.close()
        raise HTTPException(404, "Урок не найден")

    session.query(LessonProgress).filter_by(lesson_id=lesson_id).delete()
    session.delete(l)
    session.commit()
    session.close()
    return {"status": "ok", "deleted_id": lesson_id}


@router.get("/admin/courses/{course_id}/lessons")
def admin_list_lessons(
    course_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    lessons = (
        session.query(Lesson)
        .filter_by(course_id=course_id)
        .order_by(Lesson.order_num)
        .all()
    )
    result = [
        {
            "id": l.id,
            "title_ru": l.title_ru,
            "title_en": l.title_en,
            "lesson_type": l.lesson_type,
            "order_num": l.order_num,
            "duration_min": l.duration_min,
        }
        for l in lessons
    ]
    session.close()
    return result
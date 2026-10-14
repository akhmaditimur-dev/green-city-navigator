from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from src.db.models import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title_ru = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=False)
    description_ru = Column(Text)
    description_en = Column(Text)
    category = Column(String(50), default="general")  # water / air / climate / general
    level = Column(String(20), default="beginner")    # beginner / intermediate / advanced
    cover_url = Column(String(500))
    author_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Course {self.title_ru}>"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title_ru = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=False)
    lesson_type = Column(String(20), default="text")  # text / video / material / assignment
    content_ru = Column(Text)
    content_en = Column(Text)
    video_url = Column(String(500))
    material_url = Column(String(500))
    order_num = Column(Integer, default=0)
    duration_min = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Lesson {self.title_ru}>"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    progress = Column(Integer, default=0)  # 0-100

    def __repr__(self):
        return f"<Enrollment user={self.user_id} course={self.course_id}>"


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LessonProgress user={self.user_id} lesson={self.lesson_id}>"
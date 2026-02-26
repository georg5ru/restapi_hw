import pytest
from django.core.exceptions import ValidationError
from lms.models import Course, Lesson


@pytest.mark.django_db
class TestCourseModel:
    def test_course_creation(self, user):
        """Тест создания курса"""
        course = Course.objects.create(
            owner=user,
            title="Test Course",
            description="This is a test course description"
        )
        assert course.title == "Test Course"
        assert course.owner == user
        assert str(course) == "Test Course"

    def test_course_title_min_length(self, user):
        """Тест минимальной длины названия"""
        with pytest.raises(ValidationError):
            course = Course(owner=user, title="ABC", description="Valid description" * 10)
            course.full_clean()

    def test_course_title_max_length(self, user):
        """Тест максимальной длины названия"""
        long_title = "A" * 201
        with pytest.raises(ValidationError):
            course = Course(owner=user, title=long_title, description="Valid description" * 10)
            course.full_clean()


@pytest.mark.django_db
class TestLessonModel:
    def test_lesson_creation(self, user, course):
        """Тест создания урока"""
        lesson = Lesson.objects.create(
            owner=user,
            course=course,
            title="Test Lesson",
            description="This is a test lesson",
            video_url="https://youtube.com/watch?v=test123"
        )
        assert lesson.title == "Test Lesson"
        assert lesson.course == course
        assert str(lesson) == f"Test Lesson ({course.title})"

    def test_lesson_video_url_validation(self, user, course):
        """Тест валидации URL видео"""
        with pytest.raises(ValidationError):
            lesson = Lesson(
                owner=user,
                course=course,
                title="Test Lesson",
                description="Valid description",
                video_url="invalid-url"
            )
            lesson.full_clean()
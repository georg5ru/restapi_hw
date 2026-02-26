import pytest
from lms.serializers import CourseSerializer, LessonSerializer


@pytest.mark.django_db
class TestCourseSerializer:
    def test_course_serializer_validation(self, user):
        """Тест валидации сериализатора курса"""
        data = {
            'title': 'Valid Course Title',
            'description': 'This is a valid course description with enough length'
        }
        serializer = CourseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_course_serializer_invalid_title(self, user):
        """Тест невалидного названия"""
        data = {
            'title': 'ABC',  # Слишком короткое
            'description': 'Valid description' * 10
        }
        serializer = CourseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors


@pytest.mark.django_db
class TestLessonSerializer:
    def test_lesson_serializer_validation(self, user, course):
        """Тест валидации сериализатора урока"""
        data = {
            'title': 'Valid Lesson',
            'description': 'This is a valid lesson description',
            'video_url': 'https://youtube.com/watch?v=test123'
        }
        serializer = LessonSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
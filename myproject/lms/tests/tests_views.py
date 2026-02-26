import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from lms.models import Course, Lesson


@pytest.mark.django_db
class TestCourseViewSet:
    def test_list_courses(self, api_client, user, course):
        """Тест получения списка курсов"""
        url = reverse('course-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_create_course(self, api_client, user):
        """Тест создания курса"""
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'This is a new course description'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Course.objects.filter(title='New Course').exists()

    def test_moderator_cannot_create_course(self, api_client, moderator):
        """Тест что модератор не может создавать курсы"""
        url = reverse('course-list')
        data = {
            'title': 'Moderator Course',
            'description': 'This should fail'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLessonViews:
    def test_list_lessons(self, api_client, user, lesson):
        """Тест получения списка уроков"""
        url = reverse('lesson-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_lesson(self, api_client, user, course):
        """Тест создания урока"""
        url = reverse('lesson-create')
        data = {
            'course': course.id,
            'title': 'New Lesson',
            'description': 'Valid description',
            'video_url': 'https://youtube.com/watch?v=test'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
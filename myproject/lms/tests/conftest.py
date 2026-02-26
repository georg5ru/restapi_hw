import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def moderator(db):
    from django.contrib.auth.models import Group
    group, _ = Group.objects.get_or_create(name='moderators')
    user = User.objects.create_user(
        email='moder@example.com',
        password='testpass123'
    )
    user.groups.add(group)
    return user


@pytest.fixture
def course(user):
    return Course.objects.create(
        owner=user,
        title='Test Course',
        description='This is a test course description'
    )


@pytest.fixture
def lesson(user, course):
    return Lesson.objects.create(
        owner=user,
        course=course,
        title='Test Lesson',
        description='This is a test lesson',
        video_url='https://youtube.com/watch?v=test123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
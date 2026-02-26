from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    """
    Тесты для CRUD уроков
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')

        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123',
            phone='123456789',
            city='Test City'
        )

        # Создаем модератора
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='test123'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user
        )

        # Настраиваем клиенты
        self.client = APIClient()
        self.moderator_client = APIClient()

        # Авторизуем клиенты
        self.client.force_authenticate(user=self.user)
        self.moderator_client.force_authenticate(user=self.moderator)

    def test_lesson_create(self):
        """Тест создания урока обычным пользователем"""
        url = reverse('lesson-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner, self.user)

    def test_lesson_create_with_invalid_url(self):
        """Тест создания урока с недопустимой ссылкой"""
        url = reverse('lesson-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://vimeo.com/12345',  # Недопустимая ссылка
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_list(self):
        """Тест получения списка уроков"""
        url = reverse('lesson-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # С пагинацией

    def test_lesson_retrieve(self):
        """Тест получения конкретного урока"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.lesson.title)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        url = reverse('lesson-update', args=[self.lesson.id])
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Description',
            'video_link': 'https://www.youtube.com/watch?v=updated',
            'course': self.course.id
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_update_moderator(self):
        """Тест обновления урока модератором"""
        url = reverse('lesson-update', args=[self.lesson.id])
        data = {
            'title': 'Updated by Moderator',
            'description': 'Updated Description',
            'video_link': 'https://www.youtube.com/watch?v=moderator',
            'course': self.course.id
        }
        response = self.moderator_client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_lesson_update_unauthorized(self):
        """Тест обновления урока неавторизованным пользователем"""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            email='other@test.com',
            password='test123'
        )
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        url = reverse('lesson-update', args=[self.lesson.id])
        data = {
            'title': 'Updated by Other',
            'description': 'Updated Description',
            'course': self.course.id
        }
        response = other_client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        url = reverse('lesson-delete', args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_moderator(self):
        """Тест удаления урока модератором (должен быть запрещен)"""
        url = reverse('lesson-delete', args=[self.lesson.id])
        response = self.moderator_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    """
    Тесты для подписки на курсы
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем пользователя
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Настраиваем клиент
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_subscription_create(self):
        """Тест создания подписки"""
        url = reverse('subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

    def test_subscription_delete(self):
        """Тест удаления подписки"""
        # Сначала создаем подписку
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )

        url = reverse('subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

    def test_subscription_without_course_id(self):
        """Тест подписки без указания ID курса"""
        url = reverse('subscription')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        url = reverse('subscription')
        data = {'course_id': 999}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_list_with_subscription_status(self):
        """Тест, что в списке курсов отображается статус подписки"""
        # Создаем подписку
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )

        url = reverse('course-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в данных курса есть поле is_subscribed
        self.assertIn('is_subscribed', response.data['results'][0])
        self.assertTrue(response.data['results'][0]['is_subscribed'])
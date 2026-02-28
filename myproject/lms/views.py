from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Lesson
from .serializers import LessonSerializer
from .permissions import IsModerator, IsOwner

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов с правами доступа"""
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            # Создание: только авторизованные (НЕ модераторы)
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Обновление: модераторы ИЛИ владельцы
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            # Удаление: только владельцы (НЕ модераторы)
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр списка и деталей: все авторизованные
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Привязываем курс к создавшему его пользователю"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Модераторы видят все, обычные пользователи только свои"""
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            return Course.objects.prefetch_related('lessons').all()

        return Course.objects.filter(owner=user).prefetch_related('lessons').all()


class LessonListView(generics.ListAPIView):
    """Получение списка всех уроков"""
    queryset = Lesson.objects.select_related('course').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.select_related('course').all()

        return Lesson.objects.filter(owner=user).select_related('course').all()


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление одного урока"""
    serializer_class = LessonSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        """
        В Generic views нет self.action, поэтому проверяем метод запроса
        """
        if self.request.method in ('PUT', 'PATCH'):
            # Update - модератор ИЛИ владелец
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.request.method == 'DELETE':
            # Destroy - только владелец (НЕ модератор)
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Retrieve (GET, HEAD, OPTIONS) - любой аутентифицированный
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.select_related('course').all()

        return Lesson.objects.filter(owner=user).select_related('course').all()


class LessonCreateView(generics.CreateAPIView):
    """Создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]  # НЕ модераторы

    def perform_create(self, serializer):
        """Привязываем урок к создавшему его пользователю"""
        serializer.save(owner=self.request.user)
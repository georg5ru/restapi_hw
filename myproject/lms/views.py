from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner


class StandardResultsSetPagination(PageNumberPagination):
    """Стандартная пагинация"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов с правами доступа"""
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

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
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.select_related('course').all()

        return Lesson.objects.filter(owner=user)
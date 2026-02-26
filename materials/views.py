from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModerator, IsOwner
from materials.paginators import CoursePagination, LessonPagination


class SubscriptionView(APIView):
    """
    APIView для управления подпиской на курс
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Если подписка есть - удаляем, если нет - создаем
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли подписка
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            # Подписка есть - удаляем
            subscription.delete()
            message = 'Подписка удалена'
            status_code = status.HTTP_200_OK
        else:
            # Подписки нет - создаем
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            status_code = status.HTTP_201_CREATED

        return Response(
            {"message": message},
            status=status_code
        )


# Остальные view остаются без изменений
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination  # Добавляем пагинацию

    # ... остальной код

    def get_serializer_context(self):
        """
        Передаем request в контекст сериализатора для is_subscribed
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not (IsModerator().has_permission(request, self) or
                IsOwner().has_object_permission(request, self, instance)):
            self.permission_denied(request, message="У вас нет прав для просмотра этого курса")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Lesson views остаются без изменений
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPagination  # Добавляем пагинацию


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not (IsModerator().has_permission(request, self) or
                IsOwner().has_object_permission(request, self, instance)):
            self.permission_denied(request, message="У вас нет прав для просмотра этого урока")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]
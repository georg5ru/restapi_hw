from rest_framework import viewsets
from rest_framework import generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


# CRUD для Course с использованием ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов"""
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer


# CRUD для Lesson с использованием Generic классов
class LessonListView(generics.ListAPIView):
    """Получение списка всех уроков"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'pk'


class LessonCreateView(generics.CreateAPIView):
    """Создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Простой сериализатор для Course"""

    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    """Простой сериализатор для Lesson"""

    class Meta:
        model = Lesson
        fields = '__all__'
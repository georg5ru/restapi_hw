from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для уроков"""

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курсов с уроками"""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons')

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

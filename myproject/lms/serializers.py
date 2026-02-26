from rest_framework import serializers
from .models import Course, Lesson
from .validators import (
    CourseTitleValidator,
    LessonTitleValidator,
    VideoURLValidator,
    DescriptionValidator
)


class LessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[LessonTitleValidator()])
    description = serializers.CharField(validators=[DescriptionValidator(min_length=10, max_length=1000)])
    video_url = serializers.URLField(validators=[VideoURLValidator()])

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        # Дополнительная валидация на уровне сериализатора
        if 'title' in data and 'description' in data:
            if data['title'].lower() == data['description'].lower():
                raise serializers.ValidationError({
                    'description': 'Описание не должно совпадать с названием'
                })
        return data


class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[CourseTitleValidator()])
    description = serializers.CharField(validators=[DescriptionValidator(min_length=20, max_length=2000)])
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons')

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']
        read_only_fields = ['created_at']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def validate(self, data):
        # Проверка что название уникально (case-insensitive)
        title = data.get('title')
        if title:
            if Course.objects.filter(title__iexact=title).exists():
                raise serializers.ValidationError({
                    'title': 'Курс с таким названием уже существует'
                })
        return data
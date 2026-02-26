from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url, YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для урока с валидацией ссылок
    """

    class Meta:
        model = Lesson
        fields = '__all__'
        # Вариант 1: валидация через Meta
        validators = [YouTubeValidator(field='video_link')]

    # Вариант 2: валидация на уровне поля
    # video_link = serializers.URLField(validators=[validate_youtube_url], required=False)


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курса с вложенными уроками
    """
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()  # для задания 2

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на курс
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import Subscription
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False



class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки
    """
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created_at']
        read_only_fields = ['created_at']
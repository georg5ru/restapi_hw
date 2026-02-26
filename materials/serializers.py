from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для урока
    """

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeValidator(field='video_link')]
        extra_kwargs = {
            'title': {'help_text': 'Название урока'},
            'description': {'help_text': 'Описание урока'},
            'video_link': {'help_text': 'Ссылка на видео (только YouTube)'},
            'course': {'help_text': 'ID курса, к которому относится урок'},
        }


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курса с вложенными уроками и информацией о подписке
    """
    lessons = LessonSerializer(many=True, read_only=True, help_text='Список уроков курса')
    lessons_count = serializers.SerializerMethodField(help_text='Количество уроков в курсе')
    is_subscribed = serializers.SerializerMethodField(help_text='Подписан ли текущий пользователь на курс')

    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'title': {'help_text': 'Название курса'},
            'description': {'help_text': 'Описание курса'},
            'preview': {'help_text': 'Превью изображение курса'},
        }

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки на курс
    """

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'user': {'help_text': 'ID пользователя'},
            'course': {'help_text': 'ID курса'},
        }
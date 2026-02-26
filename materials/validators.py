import re
from rest_framework import serializers
from django.core.exceptions import ValidationError


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com
    """
    # Регулярное выражение для проверки YouTube ссылок
    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

    if not re.match(youtube_regex, value):
        raise ValidationError('Разрешены только ссылки на YouTube')

    return value


class YouTubeValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Если валидатор применяется к полю, то value - это значение поля
        if isinstance(value, dict):
            # Если value - словарь (для валидации в Meta)
            field_value = value.get(self.field)
            if field_value:
                validate_youtube_url(field_value)
        else:
            # Если value - строка (для валидации поля)
            validate_youtube_url(value)
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class CourseTitleValidator:
    """Валидатор для названия курса"""

    def __call__(self, value):
        if len(value) < 5:
            raise ValidationError('Название курса должно содержать не менее 5 символов')

        if len(value) > 200:
            raise ValidationError('Название курса не должно превышать 200 символов')

        # Проверка на наличие только букв, цифр и базовых символов
        if not re.match(r'^[\w\s\-.,:!?()]+$', value):
            raise ValidationError('Название курса содержит недопустимые символы')


@deconstructible
class LessonTitleValidator:
    """Валидатор для названия урока"""

    def __call__(self, value):
        if len(value) < 3:
            raise ValidationError('Название урока должно содержать не менее 3 символов')

        if len(value) > 200:
            raise ValidationError('Название урока не должно превышать 200 символов')


@deconstructible
class VideoURLValidator:
    """Валидатор для URL видео"""

    def __call__(self, value):
        # Проверка на корректность URL
        url_pattern = re.compile(
            r'^https?://'  # http:// или https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(value):
            raise ValidationError('Введите корректный URL видео')

        # Проверка на YouTube или Vimeo
        if not any(domain in value for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
            raise ValidationError('Поддерживаются только видео с YouTube или Vimeo')


@deconstructible
class DescriptionValidator:
    """Валидатор для описания"""

    def __init__(self, min_length=10, max_length=5000):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(f'Описание должно содержать не менее {self.min_length} символов')

        if len(value) > self.max_length:
            raise ValidationError(f'Описание не должно превышать {self.max_length} символов')
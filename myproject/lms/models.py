from django.db import models


class Course(models.Model):
    """Модель курса"""

    title = models.CharField('Название', max_length=200)
    preview = models.ImageField('Превью', upload_to='courses/')
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока. Связан с курсом (один ко многим)"""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    preview = models.ImageField('Превью', upload_to='lessons/')
    video_url = models.URLField('Ссылка на видео')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['course', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.course.title})"
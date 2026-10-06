from django.conf import settings
from django.db import models


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Начальный'
        INTERMEDIATE = 'intermediate', 'Средний'
        ADVANCED = 'advanced', 'Продвинутый'

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    cover = models.ImageField('Обложка', upload_to='covers/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='authored_courses', verbose_name='Автор',
    )
    level = models.CharField('Уровень', max_length=20, choices=Level.choices, default=Level.BEGINNER)
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='Курс')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', verbose_name='Модуль')
    title = models.CharField('Название', max_length=200)
    content = models.TextField('Содержание', blank=True)
    video_url = models.URLField('Видео', blank=True)
    order = models.PositiveIntegerField('Порядок', default=1)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ('module', 'order')
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title

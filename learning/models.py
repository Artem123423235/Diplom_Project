from django.conf import settings
from django.db import models
from django.utils import timezone


class Enrollment(models.Model):
    """Запись студента на курс."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='enrollments', verbose_name='Студент',
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE,
        related_name='enrollments', verbose_name='Курс',
    )
    enrolled_at = models.DateTimeField('Дата записи', auto_now_add=True)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ('student', 'course')
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'

    def __str__(self):
        return f'{self.student} → {self.course}'

    @property
    def progress_percent(self):
        """Сколько процентов уроков курса пройдено студентом."""
        from courses.models import Lesson
        total = Lesson.objects.filter(module__course=self.course).count()
        if total == 0:
            return 0.0
        done = Progress.objects.filter(
            student=self.student,
            lesson__module__course=self.course,
            is_completed=True,
        ).count()
        return round(done * 100 / total, 1)


class Progress(models.Model):
    """Прогресс студента по конкретному уроку."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='progress_records', verbose_name='Студент',
    )
    lesson = models.ForeignKey(
        'courses.Lesson', on_delete=models.CASCADE,
        related_name='progress_records', verbose_name='Урок',
    )
    is_completed = models.BooleanField('Пройден', default=False)
    completed_at = models.DateTimeField('Дата прохождения', null=True, blank=True)

    class Meta:
        ordering = ['-completed_at']
        unique_together = ('student', 'lesson')
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогресс'

    def __str__(self):
        mark = '✔' if self.is_completed else '—'
        return f'{self.student} / {self.lesson} [{mark}]'

    def save(self, *args, **kwargs):
        if self.is_completed:
            if self.completed_at is None:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None
        super().save(*args, **kwargs)

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class Quiz(models.Model):
    lesson = models.OneToOneField(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="quiz",
        verbose_name="Урок",
    )
    title = models.CharField("Название теста", max_length=255)
    pass_score = models.PositiveIntegerField(
        "Проходной балл (%)",
        default=70,
        validators=[MaxValueValidator(100)],
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        constraints = [
            models.CheckConstraint(
                check=models.Q(pass_score__lte=100),
                name="quiz_pass_score_lte_100",
            ),
        ]

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Тест",
    )
    text = models.TextField("Текст вопроса")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    text = models.CharField("Текст ответа", max_length=255)
    is_correct = models.BooleanField("Правильный?", default=False)

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return self.text


class Attempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        verbose_name="Студент",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Тест",
    )
    score = models.PositiveIntegerField(
        "Результат (%)",
        default=0,
        validators=[MaxValueValidator(100)],
    )
    passed = models.BooleanField("Сдано?", default=False)
    created_at = models.DateTimeField("Дата попытки", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"
        constraints = [
            models.CheckConstraint(
                check=models.Q(score__lte=100),
                name="attempt_score_lte_100",
            ),
        ]

    def __str__(self):
        return f"{self.user} · {self.quiz} · {self.score}%"

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Course, Lesson, Module
from learning.models import Enrollment, Progress
from quizzes.models import Answer, Question, Quiz

User = get_user_model()

PASSWORD = 'Zx9!Qw2#Fp7'


def _has_field(model, name):
    return any(f.name == name for f in model._meta.get_fields())


def _create(model, **kwargs):
    """Создаёт объект, отбрасывая поля, которых нет в модели."""
    clean = {k: v for k, v in kwargs.items() if _has_field(model, k)}
    return model.objects.create(**clean)


class Command(BaseCommand):
    help = "Заполняет БД демо-данными: пользователи, курсы, модули, уроки, тесты, прогресс."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)   # детерминированный результат

        # 1) пользователи --------------------------------------------------
        admin = self._get_or_create_user(
            username='admin', email='admin@example.com',
            role='admin', full_name='Администратор',
            is_superuser=True, is_staff=True,
        )
        teachers = [
            self._get_or_create_user(
                username=f'teacher{i}', email=f'teacher{i}@example.com',
                role='teacher', full_name=f'Преподаватель {i}',
            )
            for i in (1, 2)
        ]
        students = [
            self._get_or_create_user(
                username=f'student{i}', email=f'student{i}@example.com',
                role='student', full_name=f'Студент {i}',
            )
            for i in range(1, 6)
        ]
        self.stdout.write(self.style.SUCCESS(
            f'Пользователи: admin={admin.username}, '
            f'teachers={len(teachers)}, students={len(students)}'
        ))

        # 2) курсы / модули / уроки / тесты --------------------------------
        course_specs = [
            ('Python для начинающих', 'beginner',   'Основы синтаксиса и типов данных.'),
            ('Django REST Framework', 'intermediate', 'REST API на Django с нуля.'),
            ('Алгоритмы и структуры данных', 'advanced', 'Классические алгоритмы и задачи.'),
        ]

        courses = []
        for i, (title, level, description) in enumerate(course_specs):
            author = teachers[i % len(teachers)]
            course = self._get_or_create_course(
                title=title, level=level, description=description, author=author,
            )
            courses.append(course)

            # 2 модуля по 3 урока
            for m_order in range(1, 3):
                module = self._get_or_create_module(
                    course=course, title=f'Модуль {m_order}: тема',
                    order=m_order,
                )
                for l_order in range(1, 4):
                    lesson = self._get_or_create_lesson(
                        module=module,
                        title=f'Урок {m_order}.{l_order}',
                        order=l_order,
                    )
                    # quiz на каждый чётный урок
                    if (m_order + l_order) % 2 == 0:
                        self._create_quiz_for_lesson(lesson)

        self.stdout.write(self.style.SUCCESS(
            f'Курсы: {Course.objects.count()}, '
            f'модули: {Module.objects.count()}, '
            f'уроки: {Lesson.objects.count()}, '
            f'тесты: {Quiz.objects.count()}, '
            f'вопросы: {Question.objects.count()}, '
            f'ответы: {Answer.objects.count()}'
        ))

        # 3) записи и прогресс --------------------------------------------
        for student in students:
            picked = random.sample(courses, k=random.randint(2, 3))
            for course in picked:
                Enrollment.objects.get_or_create(student=student, course=course)
                lessons = list(Lesson.objects.filter(
                    module__course=course,
                ).order_by('module__order', 'order'))
                # пройти 20–80% уроков
                n_done = int(len(lessons) * random.uniform(0.2, 0.8))
                for lesson in lessons[:n_done]:
                    Progress.objects.get_or_create(
                        student=student, lesson=lesson,
                        defaults={'is_completed': True},
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Записи: {Enrollment.objects.count()}, '
            f'прогресс: {Progress.objects.count()}'
        ))
        self.stdout.write(self.style.SUCCESS('Готово. Пароль всех пользователей: ' + PASSWORD))

    # ---------- helpers --------------------------------------------------

    def _get_or_create_user(self, *, username, email, role, full_name,
                            is_superuser=False, is_staff=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        if created:
            user.email = email
            user.role = role
            user.full_name = full_name
            user.is_superuser = is_superuser
            user.is_staff = is_staff
            user.set_password(PASSWORD)
            user.save()
        return user

    def _get_or_create_course(self, *, title, level, description, author):
        course, _ = Course.objects.get_or_create(
            title=title,
            defaults={
                k: v for k, v in {
                    'level': level, 'description': description, 'author': author,
                }.items() if _has_field(Course, k)
            },
        )
        return course

    def _get_or_create_module(self, *, course, title, order):
        module, _ = Module.objects.get_or_create(
            course=course, order=order,
            defaults={'title': title} if _has_field(Module, 'title') else {},
        )
        return module

    def _get_or_create_lesson(self, *, module, title, order):
        lesson, _ = Lesson.objects.get_or_create(
            module=module, order=order,
            defaults={'title': title} if _has_field(Lesson, 'title') else {},
        )
        return lesson

    def _create_quiz_for_lesson(self, lesson):
        if Quiz.objects.filter(lesson=lesson).exists():
            return
        quiz = _create(Quiz, lesson=lesson, title=f'Тест: {getattr(lesson, "title", lesson.pk)}')
        for q_num in range(1, 4):
            question = _create(
                Question, quiz=quiz,
                text=f'Вопрос {q_num}. Выберите правильный вариант.',
            )
            for a_num in range(1, 5):
                _create(
                    Answer, question=question,
                    text=f'Вариант ответа {a_num}',
                    is_correct=(a_num == 1),
                )
